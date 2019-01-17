# -*- coding: utf-8 -*-

import string
import random
from datetime import datetime, timedelta
import logging
from passlib.context import CryptContext
from odoo import http
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from odoo.tools import email_split
import base64
import ctypes

AVAILABLE_PRIORITIES = [
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
]

DEFAULT_STATES = [
    ('new', 'New'),
    ('core', 'Core'),
    ('transmission', 'Transmission'),
    ('done', 'Done'),
]

DEFAULT_PASSWORD_SIZE = 8
DEFAULT_MONTH_DAYS = 30
DEFAULT_NEXT_MONTH_DAYS = 31
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

OTC_PRODUCT_CODE = 'ISP-OTC'
DEFAULT_PACKAGE_CAT_NAME = 'Packages'

default_crypt_context = CryptContext(
    # kdf which can be verified by the context. The default encryption kdf is
    # the first of the list
    ['pbkdf2_sha512', 'md5_crypt'],
    # deprecated algorithms are still verified as usual, but ``needs_update``
    # will indicate that the stored hash should be replaced by a more recent
    # algorithm. Passlib 1.6 supports an `auto` value which deprecates any
    # algorithm but the default, but Ubuntu LTS only provides 1.5 so far.
    deprecated=['md5_crypt'],
)


class ServiceRequest(models.Model):
    """
    Model for different type of service_requests.
    """
    _name = "isp_crm_module.service_request"
    _description = "Service Request To be solved."
    _rec_name = 'name'
    _order = "create_date desc, name, id"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']

    @api.depends('product_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for service_request in self:
            amount_untaxed = 0.00
            for line in service_request.product_line:
                amount_untaxed += line.price_subtotal
            service_request.update({
                'amount_total': amount_untaxed,
            })

    def _get_default_portal(self):
        return self.env['res.groups'].search([('is_portal', '=', True)], limit=1)

    def extract_email(self, email):
        """ extract the email address from a user-friendly email address """
        addresses = email_split(email)
        return addresses[0] if addresses else ''

    name = fields.Char('Request Name', required=True, index=True, copy=False, default='New')
    problem = fields.Char(string="Problem", required=True, translate=True, default="Problem")
    description = fields.Text('Description')
    stage = fields.Many2one('isp_crm_module.stage', string='Stage', required=False,
                            group_expand='_default_stages')

    assigned_to = fields.Many2one('hr.employee', string='Assigned To', index=True, track_visibility='onchange')
    team = fields.Many2one('hr.department', string='Department', store=True)
    team_leader = fields.Many2one('hr.employee', string='Team Leader', store=True)

    customer = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)], track_visibility='onchange')
    customer_email = fields.Char(related='opportunity_id.email_from', store=True)
    customer_mobile = fields.Char(string="Mobile", related='opportunity_id.mobile', store=True)
    customer_phone = fields.Char(string="Phone", related='opportunity_id.phone', store=True)
    customer_company = fields.Char(string="Company", related='customer.parent_id.name', store=True)
    customer_address = fields.Char(string="Address", track_visibility='onchange')

    project = fields.Many2one('project.project', string="Project")
    priority = fields.Selection(AVAILABLE_PRIORITIES, string="Priority")
    close_date = fields.Datetime('Close Date', readonly=True, default=None)
    is_service_request_closed = fields.Boolean('Is Service Request Closed', default=False)
    solution_ids = fields.One2many('isp_crm_module.solution_line', 'service_request_id', string="Solutions", copy=True, auto_join=True)
    color = fields.Integer()
    is_done = fields.Boolean("Is Done", default=False)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',  readonly=True,
                                   help="Pricelist for Service Request.")
    currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True)
    product_line = fields.One2many('isp_crm_module.product_line', 'service_request_id', string='Product Lines', copy=True, auto_join=True)

    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   track_visibility='always')
    opportunity_id = fields.Many2one('crm.lead', string='Opportunity', readonly=True,
                                   help="Opportunity for which the service Request created.")

    is_helpdesk_ticket = fields.Boolean("Is Ticket", default=False)
    confirmed_sale_order_id = fields.Many2one('sale.order', string='Confirmed Sale Order')
    order_line = fields.One2many('sale.order.line', 'service_request_id', string='Order Lines', copy=True, auto_join=True)
    order_line_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_order_line_total',
                                   track_visibility='always')
    tagged_product_ids = fields.Many2many('product.product', 'isp_crm_module_service_request_product_rel', 'service_request_id', 'product_id',
                                          string='Products',
                                          help="Classify and analyze your lead/opportunity according to Products : Unlimited Package etc")
    ip = fields.Char('IP Address')
    subnet_mask = fields.Char('Subnet Mask')
    gateway = fields.Char('Gateway')

    def _get_next_package_end_date(self, given_date):
        given_date_obj = datetime.strptime(given_date, DEFAULT_DATE_FORMAT)
        package_end_date_obj = given_date_obj + timedelta(days=DEFAULT_MONTH_DAYS)
        return package_end_date_obj.strftime(DEFAULT_DATE_FORMAT)

    def _get_next_package_start_date(self, given_date):
        given_date_obj = datetime.strptime(given_date, DEFAULT_DATE_FORMAT)
        package_start_date_obj = given_date_obj + timedelta(days=DEFAULT_NEXT_MONTH_DAYS)
        return package_start_date_obj.strftime(DEFAULT_DATE_FORMAT)



    def get_customer_address_str(self, customer):
        address_str = ""
        if len(customer) > 0:
            address_str = ", ".join([
                customer.street or '',
                customer.street2 or '',
                customer.city or '',
                customer.state_id.name or '',
                customer.zip or '',
                customer.country_id.name or '',
            ])
        return address_str

    @ api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['isp_crm_module.stage'].search([])
        return stage_ids

    @api.onchange('assigned_to')
    def _onchange_assigned_to(self):
        self.team_leader = self.assigned_to and self.assigned_to.parent_id
        self.team = self.assigned_to.department_id

    @api.onchange('customer')
    def _onchange_customer(self):
        self.customer_address = self.get_customer_address_str(customer=self.customer)

    def _create_random_password(self, size):
            chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
            return ''.join(random.choice(chars) for _ in range(size))

    @api.model
    def create(self, vals):
        first_stage = self.env['isp_crm_module.stage'].search([], order="sequence asc")[0]
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.service_request') or '/'
            vals['stage'] = first_stage.id
        return super(ServiceRequest, self).create(vals)

    def _default_account(self):
        journal = self.env['account.journal'].search([('code', '=', 'INV')])[0]
        return journal.default_credit_account_id.id

    def _default_stages(self, stages, domain, order):
        stage_ids = self.env['isp_crm_module.stage'].search([('name', '!=', 'Undefined')])
        return stage_ids

    @api.multi
    def action_make_service_request_done(self):
        for service_req in self:
            # update the stage of this service request to done
            last_stage_obj = self.env['isp_crm_module.stage'].search([], order='sequence desc', limit=1)
            service_req.update({
                'is_done': True,
                'stage': last_stage_obj.id,
            })
            customer = service_req.customer
            get_opportunity = self.env['crm.lead'].search([('partner_id', '=', customer.id)], limit=1)
            if get_opportunity:
                customer_type = "MR" if get_opportunity.lead_type == "retail" else "MC"
            else:
                customer_type = "MR" if customer.company_type == 'person' else "MC"
            sequence = self.env['ir.sequence'].next_by_code('res.partner')
            sequence_str = customer_type + sequence
            customer_subs_id = sequence_str
            cust_password = self._create_random_password(size=DEFAULT_PASSWORD_SIZE)
            encrypted = "abcd1234"

            # updating customer's potentiality
            customer.update({
                'is_potential_customer' : False,
                'subscriber_id' : customer_subs_id
            })

            # Create an user
            user_created = self._create_user(partner=customer, username=customer_subs_id, password=cust_password)

            # invoice generation
            last_invoice                    = self.env['account.invoice'].search([('partner_id', '=', customer.id)], order='create_date desc', limit=1)
            last_invoices_inv_lines         = last_invoice[0].invoice_line_ids

            for line in last_invoices_inv_lines:
                try:
                    if line.product_id.categ_id.name == DEFAULT_PACKAGE_CAT_NAME:
                        package_line = line

                except UserError as ex:
                    print(ex)

            sales_order_obj                 = self.env['sale.order'].search([('name', '=', last_invoice.origin)], order='create_date desc', limit=1)
            current_package_id              = package_line.product_id.id
            current_package_price           = package_line.price_unit
            current_package_start_date      = fields.Date.today()
            current_package_sales_order_id  = sales_order_obj.id

            # updating current package info
            customer.update_current_bill_cycle_info(
                customer        = customer,
                start_date      = current_package_start_date,
                product_id      = current_package_id,
                price           = current_package_price,
                sales_order_id  = current_package_sales_order_id
            )
            # updating next package info
            customer.update_next_bill_cycle_info(
                customer = customer,
            )

            # Adding the package change history
            package_history_obj = self.env['isp_crm_module.customer_package_history'].search([])
            created_package_history = package_history_obj.set_package_change_history(customer)

            # updating opportunity
            opportunity = service_req.opportunity_id
            opportunity.update({
                'color'                             : 10,
                'current_service_request_id'        : service_req.name,
                'current_service_request_status'    : 'Done',
            })

            # Generate Dynamic Invoice and Send in mail.
            template_obj = self.env['mail.template'].sudo().search([('name', '=', 'Send_Service_Request_Mail')], limit=1)
            invoice      = self.env['account.invoice'].sudo().search([])[-1]
            pdf          = self.env.ref('sale.action_report_saleorder').render_qweb_pdf([sales_order_obj.id])

            # save pdf as attachment
            ATTACHMENT_NAME = "Test Attachment Name"
            attachment = self.env['ir.attachment'].create({
                'name': ATTACHMENT_NAME,
                'type': 'binary',
                'datas_fname': ATTACHMENT_NAME + '.pdf',
                'store_fname': ATTACHMENT_NAME,
                'datas': base64.encodestring(pdf[0]),
                'mimetype': 'application/x-pdf'
            })

            # showing warning for not setting ip, subnetmask and gateway
            if self.ip is False or self.subnet_mask is False or self.gateway is False:
                raise UserError('Please give all the technical information to mark done this ticket.')
            self.env['isp_crm_module.mail'].service_request_send_email(customer.email,customer_subs_id,cust_password,str(self.ip),str(self.subnet_mask),str(self.gateway),template_obj,attachment)

        return True

    def _crypt_context(self):
        """ Passlib CryptContext instance used to encrypt and verify
        passwords. Can be overridden if technical, legal or political matters
        require different kdfs than the provided default.

        Requires a CryptContext as deprecation and upgrade notices are used
        internally
        """
        return default_crypt_context

    def _create_user(self, partner, username, password, name=''):
        portal_group = self._get_default_portal()
        # creating portal user
        created_user = self.env['res.users'].with_context(no_reset_password=True).create({
            'email': self.extract_email(email=partner.email),
            'login': username,
            'partner_id': partner.id,
            'company_id': partner.company_id.id,
            'company_ids': [(6, 0, [partner.company_id.id])],
            'groups_id': [(6, 0, [portal_group.id])],
        })
        created_user.write({
            'password' : password
        })
        return created_user


        user_model = self.env['isp_crm_module.login']
        vals_user = {
            'name': name,
            'subscriber_id': username,
            'password': password,
        }
        user_model.create(vals_user)
        return True

    def update_bill_cycle_date(self, customer):
        """
        Updates bill cycle date of customer in technical information

        :param customer:
        :return: Boolean
        """
        today_datetime = datetime.now()
        customer.update({
            'bill_cycle_date' : int(today_datetime.day) + int(7)
        })
        return True


    def create_invoice_for_customer(self, customer):
        sales_order_line_list = []
        sales_order_line = None
        sales_order_obj = self.env['sale.order'].search(
                [
                    ('partner_id', '=', customer.id),
                    ('state', '=', 'sale'),
                    ('confirmation_date', '!=', None),
                ],
                order='create_date asc',
                limit=1)
        if len(sales_order_obj) > 0:
            sales_order_line_list = [order_line for order_line in sales_order_obj.order_line if order_line.product_id.default_code != OTC_PRODUCT_CODE]
        else:
            raise UserError(_('You Have To create a Sales Order First.'))

        if len(sales_order_line_list) > 0:
            sales_order_line = sales_order_line_list[0]
            invoice_line_data = self._create_invoice_line_from_sales_order_line(sales_order_line=sales_order_line)
            invoice_obj = self.env['account.invoice']
            invoice_data = {
                'partner_id' : customer.id,
                'invoice_line_ids' : [(0, 0, invoice_line_data)],
                'origin' : sales_order_obj.name
            }
            created_invoice_obj = invoice_obj.create(invoice_data)
            if not created_invoice_obj:
                return False
            else:
                return created_invoice_obj
        else:
            raise UserError(_('You Have To create a Sales Order First.'))


    def _create_invoice_line_from_sales_order_line(self, sales_order_line):
        invoice_line_data = {}
        invoice_line_data = {
            'account_id'    : self._default_account(),
            'product_id'    : sales_order_line.product_id.id,
            'name'          : sales_order_line.name,
            'quantity'      : sales_order_line.product_uom_qty,
            'price_unit'    : sales_order_line.price_unit,
        }
        return invoice_line_data

    def send_invoice_to_customer_111(self, invoice):
        # self.ensure_one()
        template = self.env.ref('account.email_template_edi_invoice', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
                default_model='account.invoice',
                default_res_id=invoice.id,
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                default_composition_mode='comment',
                mark_invoice_as_sent=True,
                custom_layout="account.mail_template_data_notification_email_account_invoice",
                force_email=True
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.depends('order_line.price_total')
    def _compute_order_line_total(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
            order.update({
                'order_line_total': amount_untaxed,
            })
