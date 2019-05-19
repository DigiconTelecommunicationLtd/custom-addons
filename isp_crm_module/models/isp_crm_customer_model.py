# -*- coding: utf-8 -*-



from ast import literal_eval
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import Warning, UserError
import re
import odoo.addons.decimal_precision as dp

GENDERS = [
    ('male', _('Male')),
    ('female', _('Female')),
    ('others', _('Others')),
]

ACTIVE_STATES = [
    ('active', _('Active')),
    ('inactive', _('Inactive')),
]

DEFAULT_MONTH_DAYS = 30
DEFAULT_NEXT_MONTH_DAYS = 31
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_ACCOUNT_CODE = '100001'

class Customer(models.Model):
    """Inherits res.partner and adds Customer info in partner form"""
    _inherit = 'res.partner'

    _sql_constraints = [
        ('phone', 'Check(1=1)', 'Phone number must be unique!'),
        ('mobile', 'Check(1=1)', 'Mobile number must be unique!'),
        ('email', 'Check(1=1)', 'Email must be unique!'),
    ]

    subscriber_id = fields.Char('Subcriber ID', copy=False, readonly=True, index=True, default=lambda self: _('New'), track_visibility='onchange')
    father = fields.Char("Father's Name", default='', required=False, track_visibility='onchange')
    mother = fields.Char(string="Mother's Name", required=False, default='', track_visibility='onchange')
    birthday = fields.Date('Date of Birth', required=False, default=None, track_visibility='onchange')
    gender = fields.Selection(GENDERS, string='Gender', required=False, help="Gender of the Subscriber", default='', track_visibility='onchange')
    identifier_name = fields.Char(string="Identifier's Name", required=False, default='', track_visibility='onchange')
    identifier_phone = fields.Char(string="Identifier's Telephone", required=False, default='', track_visibility='onchange')
    identifier_mobile = fields.Char(string="Identifier's Mobile", required=False, default='', track_visibility='onchange')
    identifier_nid = fields.Char(string="Identifier's NID", required=False, default=False, track_visibility='onchange')
    service_type = fields.Many2one('isp_crm.service_type', default=False, required=False, string='Service Type', track_visibility='onchange')
    connection_type = fields.Many2one('isp_crm.connection_type', default=False, required=False, string='Connection Type', track_visibility='onchange')
    connection_media = fields.Many2one('isp_crm.connection_media', default=False, required=False, string='Connection Media', track_visibility='onchange')
    connection_status = fields.Boolean(string='Connection Up', default=False, required=False, track_visibility='onchange')
    bill_cycle_date = fields.Integer(string='Bill Cycle Date', required=False, default=None, readonly=True, track_visibility='onchange')
    total_installation_charge = fields.Monetary(compute='_compute_installation_charge', string="Total Instl. Charge", track_visibility='onchange')
    is_potential_customer = fields.Boolean(string='Is This Customer potential or not?', default=True, required=False, track_visibility='onchange')
    package_id = fields.Many2one('product.product', string='Package', domain=[('sale_ok', '=', True)],
                                 change_default=True, ondelete='restrict', track_visibility='onchange')
    # Package Info
    current_package_id = fields.Many2one('product.product', string='Package', domain=[('sale_ok', '=', True)],
                                         change_default=True, ondelete='restrict', track_visibility='onchange')
    current_package_start_date = fields.Date('Start Date', default=None, track_visibility='onchange')
    current_package_end_date = fields.Date('Valid Till', default=None, track_visibility='onchange')
    current_package_price = fields.Float('Current Package Price', required=True,
                                         digits=dp.get_precision('Product Price'), default=0.0, track_visibility='onchange')
    current_package_original_price = fields.Float('Current Package Original Price',
                                                  digits=dp.get_precision('Product Price'), default=0.0, track_visibility='onchange')
    current_package_sales_order_id = fields.Many2one('sale.order', string='Current Package Sales Order', track_visibility='onchange')
    next_package_id = fields.Many2one('product.product', string='Future Package', domain=[('sale_ok', '=', True)],
                                      change_default=True, ondelete='restrict', track_visibility='onchange')
    next_package_start_date = fields.Date('Next Package Start Date', default=None, track_visibility='onchange')
    next_package_price = fields.Float('Next Package Price',
                                      digits=dp.get_precision('Product Price'), default=0.0, track_visibility='onchange')
    next_package_original_price = fields.Float('Next Package Original Price',
                                               digits=dp.get_precision('Product Price'), default=0.0, track_visibility='onchange')
    next_package_sales_order_id = fields.Many2one('sale.order', string='Next Package Sales Order', track_visibility='onchange')
    active_status = fields.Selection(ACTIVE_STATES, string='Active Status', required=False, help="Active Status of Current Bill Cycle", default='active', track_visibility='onchange')
    is_deferred = fields.Boolean("Is Deferred", default=False, track_visibility='onchange')
    assigned_rm = fields.Many2one('res.users', string='RM', track_visibility='onchange')
    customer_etin = fields.Char(string='Customer ETIN', track_visibility='onchange')
    customer_bin = fields.Char(string='Customer BIN', track_visibility='onchange')
    is_service_request_marked_done = fields.Boolean(compute='_get_mark_done_info', default=False, track_visibility='onchange')
    is_sent_package_change_req = fields.Boolean("Is Package Change Request Sent", default=False, track_visibility='onchange')
    is_sent_package_change_req_from_technical_information = fields.Boolean("Is Package Change Request Made from Technical Information", default=True, track_visibility='onchange')

    product_line = fields.One2many('isp_crm_module.customer_product_line', 'customer_id',
                                 string='Customer Product Lines', copy=True, auto_join=True)
    product_line_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_product_line_total',
                                       track_visibility='always')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True,
                                   help="Pricelist for Customer.")

    invoice_product_id = fields.Many2one('product.product', string='Package', domain=[('sale_ok', '=', True)],
                                         change_default=True, ondelete='restrict')
    invoice_product_price = fields.Float('Current Package Price', required=True,
                                         digits=dp.get_precision('Product Price'), default=0.0)
    invoice_product_original_price = fields.Float('Current Package Original Price',
                                                  digits=dp.get_precision('Product Price'), default=0.0)
    invoice_sales_order_name = fields.Char('Subcriber ID', copy=False, readonly=True)

    body_html = fields.Text()
    subject_mail = fields.Char()
    mail_to = fields.Char()
    mail_cc = fields.Char()
    property_product_pricelist = fields.Many2one(
        'product.pricelist', 'Sale Pricelist', compute='_compute_product_pricelist',
        inverse="_inverse_product_pricelist", company_dependent=False,  # NOT A REAL PROPERTY
        help="This pricelist will be used, instead of the default one, for sales to the current partner", track_visibility='onchange')

    technical_info_ip = fields.Char('IP Address')
    technical_info_subnet_mask = fields.Char('Subnet Mask')
    technical_info_gateway = fields.Char('Gateway')
    description_info = fields.Text('Description')

    def _get_mark_done_info(self):
        """
        Compute if service request is marked done or not
        :return:
        """
        for customer in self:
            check_done = customer.is_service_request_marked_done
            get_opportunity = self.env['isp_crm_module.service_request'].search([('customer', '=', customer.id)], limit=1)
            if get_opportunity.is_done:
                customer.update({
                    'is_service_request_marked_done': True,
                })
            else:
                customer.update({
                    'is_service_request_marked_done': False,
                })


    def _get_package_end_date(self, given_date):
        """
        Returns date of after adding DEFAULT_MONTH_DAYS days
        :param given_date: start_date of the package
        :return: date str
        """
        # Check if customer is inactive and valid till date is over
        today = str(date.today())
        today_obj = datetime.strptime(today, DEFAULT_DATE_FORMAT)
        given_date_obj          = datetime.strptime(given_date, DEFAULT_DATE_FORMAT)
        if today_obj > given_date_obj:
            package_end_date_obj = today_obj + timedelta(days=DEFAULT_MONTH_DAYS)
        else:
            package_end_date_obj    = given_date_obj + timedelta(days=DEFAULT_MONTH_DAYS)
        return package_end_date_obj.strftime(DEFAULT_DATE_FORMAT)

    def _get_next_package_start_date(self, given_date):
        """
        Returns date of after adding DEFAULT_NEXT_MONTH_DAYS days
        :param given_date: start_date of the package
        :return: date str
        """
        # Check if customer is inactive and valid till date is over
        today = str(date.today())
        today_obj = datetime.strptime(today, DEFAULT_DATE_FORMAT)
        given_date_obj          = datetime.strptime(given_date, DEFAULT_DATE_FORMAT)
        if today_obj > given_date_obj:
            package_start_date_obj = today_obj + timedelta(days=DEFAULT_NEXT_MONTH_DAYS)
        else:
            package_start_date_obj  = given_date_obj + timedelta(days=DEFAULT_NEXT_MONTH_DAYS)
        return package_start_date_obj.strftime(DEFAULT_DATE_FORMAT)

    def update_current_bill_cycle_info(self, customer, start_date=False, product_id=False, price=False, original_price=False, sales_order_id=False):
        """
        Updates current month's package and bill cycle info of given customer
        :param customer: package user
        :param start_date: start date of the package
        :param product_id: package id
        :param price: price of the package
        :param sales_order_id: sales order id of the package
        :return: updated customer
        """

        if original_price or customer.current_package_id.list_price != 0:
            if original_price != 0:
                pass
            else:
                original_price = customer.invoice_product_original_price
        else:
            # sale_order_lines = customer.next_package_sales_order_id.order_line
            # original_price = 0.0
            # for sale_order_line in sale_order_lines:
            #     discount = (sale_order_line.discount * sale_order_line.price_subtotal) / 100.0
            #     original_price_sale_order_line = sale_order_line.price_subtotal + discount
            #     original_price = original_price + original_price_sale_order_line
            original_price = customer.invoice_product_original_price

        current_package_id              = product_id if product_id else customer.current_package_id.id
        current_package_price           = price if price else customer.current_package_price
        current_package_original_price  = original_price if original_price else customer.current_package_id.list_price
        current_package_start_date      = start_date if start_date else datetime.today().strftime(DEFAULT_DATE_FORMAT)
        current_package_end_date        = self._get_package_end_date(given_date=current_package_start_date)
        current_package_sales_order_id  = sales_order_id if sales_order_id else customer.current_package_sales_order_id.id

        customer.update({
            'current_package_id'             : current_package_id,
            'current_package_price'          : current_package_price,
            'current_package_original_price' : current_package_original_price,
            'current_package_start_date'     : current_package_start_date,
            'current_package_end_date'       : current_package_end_date,
            'current_package_sales_order_id' : current_package_sales_order_id,
        })
        return customer


    def update_next_bill_cycle_info(self, customer, start_date=False, product_id=False, price=False, sales_order_id=False):
        """
        Updates next month's package and bill cycle info of given customer
        :param customer: package user
        :param start_date: start date of the package
        :param product_id: package id
        :param price: price of the package
        :param sales_order_id: sales order id of the package
        :return: updated customer
        """

        next_package_id             = product_id if product_id else customer.current_package_id.id
        next_package_start_date     = start_date if start_date else self._get_next_package_start_date(given_date=customer.current_package_start_date)
        next_package_price          = price if price else customer.current_package_price
        next_package_original_price = price if price else customer.current_package_original_price
        next_package_sales_order_id = sales_order_id if sales_order_id else customer.current_package_sales_order_id.id

        customer.update({
            'next_package_id'             : next_package_id,
            'next_package_start_date'     : next_package_start_date,
            'next_package_price'          : next_package_price,
            'next_package_original_price' : next_package_original_price,
            'next_package_sales_order_id' : next_package_sales_order_id,
            'is_sent_package_change_req_from_technical_information' : True,
        })
        return customer

    @api.onchange('current_package_id')
    def onchange_current_package_id(self):
        """

        :return:
        """
        try:
            # self contains the changed package, so get the old obj.
            res_partner_obj = self.env['res.partner'].search([('id', '=', self._origin.id)], limit=1)
            if res_partner_obj.is_sent_package_change_req_from_technical_information:

                customer_product_line_obj = self.env['isp_crm_module.customer_product_line'].search([('customer_id', '=', res_partner_obj.id),('product_id', '=', res_partner_obj.current_package_id.id)], limit=1)

                if customer_product_line_obj:
                    # updating account moves of customer
                    payment_obj = self.env['account.payment']
                    payment_obj.customer_bill_adjustment(
                        customer=res_partner_obj,
                        package_price=self.current_package_id.lst_price * int(customer_product_line_obj.product_uom_qty)
                    )

                    # self.current_package_id = self.current_package_id
                    self.current_package_price = self.current_package_id.lst_price * int(
                        customer_product_line_obj.product_uom_qty)
                    self.current_package_original_price = self.current_package_id.lst_price
                    self.current_package_end_date = self.current_package_end_date
                    self.next_package_id = self.current_package_id
                    self.next_package_price = self.current_package_id.lst_price * int(
                        customer_product_line_obj.product_uom_qty)
                    self.next_package_original_price = self.current_package_id.lst_price
                    self.next_package_start_date = self.next_package_start_date
                    self.next_package_sales_order_id = self.current_package_sales_order_id.id
                    res_partner_obj.write({
                        'current_package_id': self.current_package_id.id,
                        'current_package_price': self.current_package_id.lst_price * int(
                            customer_product_line_obj.product_uom_qty),
                        'current_package_original_price': self.current_package_id.lst_price,
                        'current_package_end_date': self.current_package_end_date,
                        'next_package_id': self.current_package_id.id,
                        'next_package_price': self.current_package_id.lst_price * int(
                            customer_product_line_obj.product_uom_qty),
                        'next_package_original_price': self.current_package_id.lst_price,
                        'next_package_start_date': self.next_package_start_date,
                        'next_package_sales_order_id': self.current_package_sales_order_id.id,
                    })

                else:
                    # updating account moves of customer
                    payment_obj = self.env['account.payment']
                    payment_obj.customer_bill_adjustment(
                        customer=res_partner_obj,
                        package_price=self.current_package_id.lst_price
                    )

                    # self.current_package_id = self.current_package_id
                    self.current_package_price = self.current_package_id.lst_price
                    self.current_package_original_price = self.current_package_id.lst_price
                    self.current_package_end_date = self.current_package_end_date
                    self.next_package_id = self.current_package_id
                    self.next_package_price = self.current_package_id.lst_price
                    self.next_package_original_price = self.current_package_id.lst_price
                    self.next_package_start_date = self.next_package_start_date
                    self.next_package_sales_order_id = self.current_package_sales_order_id.id
                    res_partner_obj.write({
                        'current_package_id': self.current_package_id.id,
                        'current_package_price': self.current_package_id.lst_price,
                        'current_package_original_price': self.current_package_id.lst_price,
                        'current_package_end_date': self.current_package_end_date,
                        'next_package_id': self.current_package_id.id,
                        'next_package_price': self.current_package_id.lst_price,
                        'next_package_original_price': self.current_package_id.lst_price,
                        'next_package_start_date': self.next_package_start_date,
                        'next_package_sales_order_id': self.current_package_sales_order_id.id,
                    })

                ### Start change customer service info ###
                created_product_line_list = []
                customer_product_line_obj = self.env['isp_crm_module.customer_product_line']
                created_product_line = customer_product_line_obj.create({
                    'customer_id': res_partner_obj.id,
                    'name': self.current_package_id.name,
                    'product_id': self.current_package_id.id,
                    'product_updatable': False,
                    'product_uom_qty': (self.current_package_price / self.current_package_id.lst_price),
                    'product_uom': self.current_package_id.uom_id.id,
                    'price_unit': self.current_package_id.lst_price,
                    'price_subtotal': self.current_package_price,
                    'price_total': self.current_package_price,
                })
                created_product_line_list.append(created_product_line.id)
                self.product_line = [(6, None, created_product_line_list)]
                # res_partner_obj.update({
                #     'product_line': [(6, None, created_product_line_list)]
                # })
                ### End change customer service info ###
            else:
                print("Partner not found.")
        except Exception as ex:
            print(ex)

    @api.onchange('assigned_rm')
    def onchange_assigned_rm(self):
        """
        If user changes RM in customer form, then change RM to all related opportunities of the customer.
        :return:
        """
        if self.assigned_rm:
            customer = self._origin.id
            get_opportunities = self.env['crm.lead'].search([('partner_id', '=', customer)])
            if get_opportunities:
                for opportunity in get_opportunities:
                    opportunity.write({
                        'assigned_rm': self.assigned_rm.id,
                    })

    @api.model
    def create(self, vals):
        validated = True
        name = vals.get('name')
        rm  = self.env['crm.lead'].search([('name', '=', name)], order='create_date desc', limit=1)

        # Update expected revenue
        products = self.env['crm.lead'].search([('name', '=', name)], order='create_date desc', limit=1).tagged_product_ids
        price = 0.00
        for product in products:
            price = price + product.price
        rm.update({
            'planned_revenue': price,
        })

        vals['assigned_rm'] = rm.assigned_rm.id
        if vals.get('email'):
            if len(vals.get('email')) < 256:
                if re.match("^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9_-]+\.[a-zA-Z0-9-]+([\.]?[a-zA-Z0-9-])*$", vals.get('email')) is None:
                    validated = False
                    raise UserError(_('Please Enter a Valid Email Address!'))

            else:
                validated = False
                raise UserError(_('Email Address is too long!'))

        if vals.get('mobile'):
            if len(vals.get('mobile')) < 15:
                if re.match("^[+]*([0-9]+-)*[0-9]+$", vals.get('mobile')) is None:
                    validated = False
                    raise UserError(_('Please Enter a Valid Mobile Number!'))
            else:
                validated = False
                raise UserError(_('Mobile number is too long!'))

        if vals.get('phone'):
            if len(vals.get('phone')) < 15:
                if re.match("^([0-9]+-)*[0-9]+$", vals.get('phone')) is None:
                    validated = False
                    raise UserError(_('Please Enter a Valid Phone Number!'))
            else:
                validated = False
                raise UserError(_('Phone number is too long!'))

        if validated:
            return super(Customer, self).create(vals)

    @api.onchange('email')
    def onchange_email(self):
        if self.email:
            if len(self.email) < 256:
                if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9_-]+\.[a-zA-Z0-9-]+([\.]?[a-zA-Z0-9-])*$", self.email) is None:
                    raise UserError(_('Please Enter a Valid Email Address!'))
            else:
                raise UserError(_('Email Address is too long!'))

    @api.onchange('mobile')
    def onchange_mobile(self):
        if self.mobile:
            if len(self.mobile) < 15:
                if re.match("^[+]*([0-9]+-)*[0-9]+$", self.mobile) is None:
                    raise UserError(_('Please Enter a Valid Mobile Number!'))
            else:
                raise UserError(_('Mobile number is too long!'))

    @api.onchange('phone')
    def onchange_phone(self):
        if self.phone:
            if len(self.phone) < 15:
                if re.match("^([0-9]+-)*[0-9]+$", self.phone) is None:
                    raise UserError(_('Please Enter a Valid Phone Number!'))
            else:
                raise UserError(_('Phone number is too long!'))

    @api.multi
    def action_view_customer_service_request(self):
        self.ensure_one()
        action = self.env.ref('isp_crm_module.isp_crm_module_service_request_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('customer', '=', self.id))
        return action

    @api.multi
    def _compute_installation_charge(self):
        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self:
            all_partner_ids = partner.search([('customer', '=', True)])

        for partner in all_partner_ids:
            customer_service_req_object = self.env['isp_crm_module.service_request'].search([('customer', '=', partner.id)])
            total_instllation_charge =  sum(req.amount_total for req in customer_service_req_object)
            partner.total_installation_charge = total_instllation_charge

    def get_customer_balance(self, customer_id, start_date=None, end_date=None):
        """
        Returns the customer's balance.
        :param customer_id: id of the customer
        :param start_date: from the date the balance checking starts
        :param end_date: to the date the balance checking ends
        :return: balance of the given customer
        """
        # Account
        unearned_account_obj =  self.env['account.account'].search([
            ('code', 'like', DEFAULT_ACCOUNT_CODE),
        ], limit=1)

        total_debit = 0.0
        total_credit = 0.0
        if start_date is None:
            start_date = self.current_package_start_date
        if end_date is None:
            end_date = self.current_package_end_date

        move_line_obj = self.env['account.move.line']
        domain = [
            ('account_id', '=', unearned_account_obj.id),
            ('partner_id', '=', customer_id),
        ]
        acc_move_lines = move_line_obj.search(domain, order='create_date desc')
        if len(acc_move_lines):
            for line in acc_move_lines:
                total_debit += line.debit
                total_credit += line.credit

        balance = 0.0 if (abs(total_debit) - abs(total_credit)) == 0.0 else abs(total_debit) - abs(total_credit)
        return balance

    def get_partner_address_str(self):
        address_str = ""
        address_str = ", ".join([
            self.street or '',
            self.street2 or '',
            self.city or '',
            self.state_id.name or '',
            self.zip or '',
            self.country_id.name or '',
        ])
        return address_str

    @api.depends('product_line.price_total')
    def _compute_product_line_total(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = 0.0
            for line in order.product_line:
                amount_untaxed += line.price_subtotal
            order.update({
                'product_line_total': amount_untaxed,
            })



