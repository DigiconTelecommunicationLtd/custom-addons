# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import re
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from . import isp_crm_service_request_model
from datetime import datetime, timezone, timedelta, date

DEFAULT_PROBLEM = "There are some Problem"
INVOICE_PAID_STATUS = 'paid'
DEFAULT_PACKAGE_CAT_NAME = 'Packages'
DEFAULT_PROCESSING_STATUS = 'Processing'
DEFAULT_DONE_STATUS = 'Done'

CUSTOMER_TYPE = [
    ('retail', _('Retail')),
    ('corporate', _('Corporate')),
    ('sohoandsme', _('SOHO and SME')),
]

class Opportunity(models.Model):
    _inherit = 'crm.lead'
    _description = "Team of ISP CRM Opportunity."

    name = fields.Char('Opportunity',index=True,required=False)
    opportunity_seq_id = fields.Char('ID', required=True, index=True, copy=False, default='New', readonly=True)
    current_service_request_id = fields.Char(string='Service Request ID', readonly=True, required=False)
    current_service_request_status = fields.Char(string='Service Request ID', readonly=True, required=False)
    is_service_request_created = fields.Boolean("Is Service Request Created", default=False)
    tagged_product_ids = fields.Many2many('product.product', 'crm_lead_product_rel', 'lead_id', 'product_id', string='Products', help="Classify and analyze your lead/opportunity according to Products : Unlimited Package etc")
    emergency_contact_name = fields.Char(string='Emergency Contact Name', required=False)
    is_customer_deferred = fields.Boolean("Is Customer Deferred", default=False)
    invoice_state = fields.Char('Invoice State')
    referred_by = fields.Many2one('res.partner', string='Referred By')
    assigned_rm = fields.Many2one('res.users', string='RM')
    lead_type = fields.Selection(CUSTOMER_TYPE, string='Type', help="Lead and Opportunity Type")
    cr = fields.Integer('Color Index', default=0, compute='_get_color_on_service_request_status')
    update_flag = fields.Integer('Is updated', default=1)
    update_date = fields.Datetime(string='Updated time', default=datetime.now())
    emergency_contact_number = fields.Char(string="Emergency Contact Number", required=False, default='',
                                   track_visibility='onchange')
    service_activation_date = fields.Date(string='Service Activation Date', track_visibility='onchange')
    proposed_activation_date = fields.Date(string='Proposed Service Activation Date', track_visibility='onchange')
    billing_start_date = fields.Date(string='Billing Start Date', track_visibility='onchange')


    def _get_color_on_service_request_status(self):
        for opportunity in self:
            service_request_obj = self.env['isp_crm_module.service_request'].search([('name', '=', opportunity.current_service_request_id)], limit=1)
            if service_request_obj:
                if service_request_obj.is_done:
                    opportunity.write({
                        'color'                             : 10,
                        'current_service_request_id'        : service_request_obj.name,
                        'current_service_request_status'    : DEFAULT_DONE_STATUS
                    })

    @api.depends('order_ids')
    def _compute_sale_amount_total(self):
        """
        Compute total sale amount for an opportunity
        :return:
        """
        for lead in self:
            total = 0.0
            nbr = 0
            company_currency = lead.company_currency or self.env.user.company_id.currency_id
            for order in lead.order_ids:
                if order.state in ('draft', 'sent', 'sale'):
                    nbr += 1
                if order.state not in ('draft', 'sent', 'cancel'):
                    order_amount_total = order.amount_untaxed + order.price_total
                    total += order.currency_id.compute(order_amount_total, company_currency)
            lead.sale_amount_total = total
            lead.sale_number = nbr

    def get_opportunity_address_str(self, opportunity):
        address_str = ""
        if len(opportunity) > 0:
            address_str = ", ".join([
                opportunity.street or '',
                opportunity.street2 or '',
                opportunity.city or '',
                opportunity.state_id.name or '',
                opportunity.zip or '',
                opportunity.country_id.name or '',
            ])
        return address_str

    @api.multi
    def action_set_won(self):
        for lead in self:
            # TODO Arif: `invoice_status` will be added later. Now checking status will be `confirm_sale`
            sale_confirmed = False

            # Check if invoice is paid .
            customer = self.partner_id.id
            if customer:
                check_customer = self.env['res.partner'].search([('id', '=', customer)], limit=1)
                if check_customer:
                    invoices = self.env['account.invoice'].search([('partner_id', '=', customer)], order="create_date desc", limit=1)
                    if invoices:
                        if invoices.is_deferred or invoices.state == INVOICE_PAID_STATUS:
                            self.invoice_state = invoices.state
                            super(Opportunity, lead).action_set_won()
                            self.action_create_new_service_request()
                        else:
                            raise UserError(_("This Opportunity's invoice is neither paid nor deferred."))
                    else:
                        raise UserError(_("This Opportunity's invoice has not been created yet. Please create the invoice first ."))
                else:
                    raise UserError(_("Customer not found."))
            else:
                raise UserError(_("Customer not found."))
        return True

    @api.onchange('email_from')
    def onchange_email(self):
        if self.email_from:
            if len(self.email_from) < 256:
                if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9_-]+\.[a-zA-Z0-9-]+([\.]?[a-zA-Z0-9-])*$", self.email_from) == None:
                    raise UserError(_('Please Enter a Valid Email Address!'))
            else:
                raise UserError(_('Email Address is too long!'))

    @api.onchange('mobile')
    def onchange_mobile(self):
        if self.mobile:
            if len(self.mobile) < 15:
                if re.match("^[+]*([0-9]+-)*[0-9]+$", self.mobile) == None:
                    raise UserError(_('Please Enter a Valid Mobile Number!'))
            else:
                raise UserError(_('Mobile number is too long!'))

    @api.onchange('phone')
    def onchange_phone(self):
        if self.phone:
            if len(self.phone) < 15:
                if re.match("^([0-9]+-)*[0-9]+$", self.phone) == None:
                    raise UserError(_('Please Enter a Valid Phone Number!'))
            else:
                raise UserError(_('Phone number is too long!'))

    @api.onchange('emergency_contact_number')
    def onchange_emergency_contact_number(self):
        if self.emergency_contact_number:
            if len(self.emergency_contact_number) < 15:
                if re.match("^[+]*([0-9]+-)*[0-9]+$", self.emergency_contact_number) == None:
                    raise UserError(_('Please Enter a Valid Phone Number!'))
            else:
                raise UserError(_('Phone number is too long!'))

    @api.onchange('assigned_rm')
    def onchange_assigned_rm(self):
        """
        If user changes RM , it will reflect in customer form.
        :return:
        """
        if self.assigned_rm:
            customer = self.partner_id.id
            if customer:
                check_customer = self.env['res.partner'].search([('id', '=', customer)])
                if check_customer:
                    for cust in check_customer:
                        cust.write({
                            'assigned_rm': self.assigned_rm.id,
                        })

    @api.onchange('lead_type')
    def onchange_lead_type(self):
        """
        If user changes Lead Type in opportunity form, then change Lead Type to all related sale orders of the customer of that opportunity.
        :return:
        """
        if self.lead_type:
            customer = self.partner_id.id
            if customer:
                check_customer = self.env['res.partner'].search([('id', '=', customer)], limit=1)
                if check_customer:
                    get_sales_order_of_the_customer = self.env['sale.order'].search([('partner_id', '=', check_customer.id)])
                    if get_sales_order_of_the_customer:
                        for order in get_sales_order_of_the_customer:
                            order.update({
                                'lead_type': str(self.lead_type),
                            })

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        # raise UserError('System does not allow you to drag record. You must change stage by action.')
        values = self._onchange_stage_id_values(self.stage_id.id)
        if values['probability'] == 100:
            for lead in self:
                # TODO Arif: `invoice_status` will be added later. Now checking status will be `confirm_sale`
                sale_confirmed = False

                # Check if invoice is paid .
                customer = self.partner_id.id
                if customer:
                    check_customer = self.env['res.partner'].search([('id', '=', customer)], limit=1)
                    if check_customer:
                        invoices = self.env['account.invoice'].search([('partner_id', '=', customer)],
                                                                      order="date_invoice desc", limit=1)
                        if invoices:
                            if invoices.is_deferred or invoices.state == INVOICE_PAID_STATUS:
                                self.update(values)
                            else:
                                raise UserError(_("This Opportunity's invoice is neither paid nor deferred."))
                        else:
                            raise UserError(_(
                                "This Opportunity's invoice has not been created yet. Please create the invoice first ."))
                    else:
                        raise UserError(_("Customer not found."))
                else:
                    raise UserError(_("Customer not found."))
        else:
            self.update(values)

    @api.model
    def create(self, vals):
        sequence_id = ""
        if vals.get('opportunity_seq_id', 'New') == 'New':
            sequence_id = self.env['ir.sequence'].next_by_code('crm.lead') or '/'
            vals['opportunity_seq_id'] = sequence_id



        if not vals.get('lead_type'):
            raise Warning(_('Please Provide lead type'))
        elif not vals.get('name'):
            raise Warning(_('Please Provide lead name'))
        elif (not vals.get('email_from')) and (not vals.get('phone')) and (not vals.get('mobile')):
            raise Warning(_('Please Provide any of this Email, Phone or Mobile'))
        elif not vals.get('proposed_activation_date'):
            raise Warning(_('Please Provide activation date'))
        elif vals.get('lead_type')!= 'retail':
            if not vals.get('partner_name'):
                raise Warning(_('Please Provide company name'))


        # if vals.get('email_from'):
        #     check_customer_email = self.env['res.partner'].search([('email', '=', vals.get('email_from'))], limit=1)
        #     if check_customer_email:
        #         raise Warning(_('Email should be unique'))
        # if vals.get('phone'):
        #     check_customer_phone = self.env['res.partner'].search([('phone', '=', vals.get('phone'))], limit=1)
        #     if check_customer_phone:
        #         raise Warning(_('Phone Number should be unique'))
        # if vals.get('mobile'):
        #     check_customer_mobile = self.env['res.partner'].search([('mobile', '=', vals.get('mobile'))], limit=1)
        #     if check_customer_mobile:
        #         raise Warning(_('Mobile Number should be unique'))

        if vals.get('assigned_rm'):
            get_assigned_rm_from_customer = vals.get('assigned_rm')
            if get_assigned_rm_from_customer:
                notification_message = "New Opportunity - "+str(sequence_id)+" created"
                get_user = self.env['res.users'].search([('id', '=', get_assigned_rm_from_customer)])
                get_user.notify_info(notification_message)

                try:
                    recipient_ids = [(get_user.partner_id.id)]
                    channel_ids = [(get_user.partner_id.channel_ids)]

                    ch = []
                    for channel in channel_ids[0]:
                        ch.append(channel.id)
                        channel.message_post(subject='New notification', body=notification_message,
                                             subtype="mail.mt_comment")
                except Exception as ex:
                    error = 'Failed to send notification. Error Message: ' + str(ex)
                    raise UserError(error)

        return super(Opportunity, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Update the update_flag and update_date field when user edits any lead.
        :param vals:
        :return:
        """
        # By default value of length of vals is assigned to 3 when user clicks on the back button of the view of the lead.
        # By default value of length of vals is assigned to the number of fields edited when user clicks on the save button of the view of the lead.
        # Check if length of vals has the key 'current_service_request_id' to detect whether user has edited any field or not.
        if 'current_service_request_id' in vals or 'update_flag' in vals:
            # User did not edit any field so passing it.
            pass
        else:
            # User has edited the field so updating the flags and date.
            vals['update_flag'] = 1
            vals['update_date'] = datetime.now()
        return super(Opportunity, self).write(vals)

    @api.multi
    def action_create_new_service_request(self):
        res = {}
        for opportunity in self:
            customer = opportunity.partner_id
            service_req_obj = self.env['isp_crm_module.service_request']
            first_stage = self.env['isp_crm_module.stage'].search([], order="sequence asc")[0]

            # Get the package name which is under Packages category
            package_name = ''
            if customer.invoice_product_id != False:
                for product in customer.invoice_product_id:
                    if customer.invoice_product_id.categ_id.name == DEFAULT_PACKAGE_CAT_NAME or customer.invoice_product_id.categ_id.complete_name == DEFAULT_PACKAGE_CAT_NAME:
                        package_name = customer.invoice_product_id.name
            else:
                package_name = ''
            # package_name = customer.invoice_product_id.name if (customer.invoice_product_id != False) else ''
            if package_name:
                pass
            else:
                package_name = ''
            service_req_data = {
                'problem': str(customer.name) + ' - ' + package_name or '',
                'stage': first_stage.id,
                'customer': customer.id,
                'customer_email': opportunity.email_from,
                'customer_mobile': opportunity.mobile,
                'customer_phone': opportunity.phone,
                'opportunity_id': opportunity.id,
                'customer_address': self.get_opportunity_address_str(opportunity=opportunity),
                'tagged_product_ids': [(6, None, opportunity.tagged_product_ids.ids)],
            }
            created_service_req_obj = service_req_obj.create(service_req_data)
            customer_product_lines = customer.product_line
            created_service_order_line_list = []
            service_order_line_obj = self.env['isp_crm_module.service_product_line']

            for product_line in customer_product_lines:
                created_service_order_line = service_order_line_obj.create({
                    'service_request_id': created_service_req_obj.id,
                    'name': product_line.name,
                    'product_id': product_line.product_id.id,
                    'product_updatable': False,
                    'product_uom_qty': product_line.product_uom_qty,
                    'product_uom': product_line.product_id.uom_id.id,
                    'price_unit': product_line.price_unit,
                    'price_subtotal': product_line.price_subtotal,
                })
                created_service_order_line_list.append(created_service_order_line)

            opportunity.update({
                'color' : 2,
                'current_service_request_id' : created_service_req_obj.name,
                'current_service_request_status' : DEFAULT_PROCESSING_STATUS,
                'is_service_request_created' : True
            })

        return True



