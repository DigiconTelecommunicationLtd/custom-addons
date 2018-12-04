# -*- coding: utf-8 -*-



from ast import literal_eval
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import Warning, UserError
import re
import odoo.addons.decimal_precision as dp

GENDERS = [
    ('male', _('Male')),
    ('female', _('Female')),
    ('others', _('Others')),
]

DEFAULT_MONTH_DAYS = 30
DEFAULT_NEXT_MONTH_DAYS = 31
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class Customer(models.Model):
    """Inherits res.partner and adds Customer info in partner form"""
    _inherit = 'res.partner'

    subscriber_id = fields.Char('Subcriber ID', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    father = fields.Char("Father's Name", default='', required=False,)
    mother = fields.Char(string="Mother's Name", required=False, default='')
    birthday = fields.Date('Date of Birth', required=False, default=None)
    gender = fields.Selection(GENDERS, string='Gender', required=False, help="Gender of the Subscriber", default='')
    identifier_name = fields.Char(string="Identifier's Name", required=False, default='')
    identifier_phone = fields.Char(string="Identifier's Telephone", required=False, default='')
    identifier_mobile = fields.Char(string="Identifier's Mobile", required=False, default='')
    identifier_nid = fields.Char(string="Identifier's NID", required=False, default=False)
    service_type = fields.Many2one('isp_crm.service_type', default=False, required=False, string='Service Type')
    connection_type = fields.Many2one('isp_crm.connection_type', default=False, required=False, string='Connection Type')
    connection_media = fields.Many2one('isp_crm.connection_media', default=False, required=False, string='Connection Media' )
    connection_status = fields.Boolean(string='Connection Up', default=False, required=False)
    bill_cycle_date = fields.Integer(string='Bill Cycle Date', required=False, default=None, readonly=True)
    total_installation_charge = fields.Monetary(compute='_compute_installation_charge', string="Total Instl. Charge")
    is_potential_customer = fields.Boolean(string='Is This Customer potential or not?', default=True, required=False)
    package_id = fields.Many2one('product.product', string='Package', domain=[('sale_ok', '=', True)],
                                 change_default=True, ondelete='restrict')
    # Package Info
    current_package_id = fields.Many2one('product.product', string='Package', domain=[('sale_ok', '=', True)],
                                         change_default=True, ondelete='restrict')
    current_package_start_date = fields.Date('Start Date', default=None)
    current_package_end_date = fields.Date('Valid Till', default=None)
    current_package_price = fields.Float('Current Package Price', required=True,
                                         digits=dp.get_precision('Product Price'), default=0.0)
    current_package_original_price = fields.Float('Current Package Original Price',
                                                  digits=dp.get_precision('Product Price'), default=0.0)
    current_package_sales_order_id = fields.Many2one('sale.order', string='Current Package Sales Order')
    next_package_id = fields.Many2one('product.product', string='Future Package', domain=[('sale_ok', '=', True)],
                                      change_default=True, ondelete='restrict')
    next_package_start_date = fields.Date('Next Package Start Date', default=None)
    next_package_price = fields.Float('Next Package Price',
                                      digits=dp.get_precision('Product Price'), default=0.0)
    next_package_original_price = fields.Float('Next Package Original Price',
                                               digits=dp.get_precision('Product Price'), default=0.0)
    next_package_sales_order_id = fields.Many2one('sale.order', string='Next Package Sales Order')
    is_deferred = fields.Boolean("Is Deferred", default=False)
    body_html = fields.Text()
    subject_mail = fields.Char()
    mail_to = fields.Char()
    mail_cc = fields.Char()


    def _get_next_package_end_date(self, given_date):
        """
        Returns date of after adding DEFAULT_MONTH_DAYS days
        :param given_date: start_date of the package
        :return: date str
        """
        given_date_obj          = datetime.strptime(given_date, DEFAULT_DATE_FORMAT)
        package_end_date_obj    = given_date_obj + timedelta(days=DEFAULT_MONTH_DAYS)
        return package_end_date_obj.strftime(DEFAULT_DATE_FORMAT)

    def _get_next_package_start_date(self, given_date):
        """
        Returns date of after adding DEFAULT_NEXT_MONTH_DAYS days
        :param given_date: start_date of the package
        :return: date str
        """
        given_date_obj          = datetime.strptime(given_date, DEFAULT_DATE_FORMAT)
        package_start_date_obj  = given_date_obj + timedelta(days=DEFAULT_NEXT_MONTH_DAYS)
        return package_start_date_obj.strftime(DEFAULT_DATE_FORMAT)

    def update_current_bill_cycle_info(self, customer, start_date=False, product_id=False, price=False, sales_order_id=False):
        """
        Updates current month's package and bill cycle info of given customer
        :param customer: package user
        :param start_date: start date of the package
        :param product_id: package id
        :param price: price of the package
        :param sales_order_id: sales order id of the package
        :return: updated customer
        """
        current_package_id              = product_id if product_id else customer.current_package_id
        current_package_price           = price if price else customer.current_package_price
        current_package_original_price  = current_package_price
        current_package_start_date      = start_date if start_date else datetime.today().strftime(DEFAULT_DATE_FORMAT)
        current_package_end_date        = self._get_next_package_end_date(given_date=current_package_start_date)
        current_package_sales_order_id  = sales_order_id if sales_order_id else customer.current_package_sales_order_id

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
        next_package_id             = product_id if product_id else customer.current_package_id
        next_package_start_date     = start_date if start_date else self._get_next_package_start_date(given_date=customer.current_package_start_date)
        next_package_price          = price if price else customer.current_package_price
        next_package_original_price = price if price else customer.current_package_original_price
        next_package_sales_order_id = sales_order_id if sales_order_id else customer.current_package_sales_order_id

        customer.update({
            'next_package_id'             : next_package_id,
            'next_package_start_date'     : next_package_start_date,
            'next_package_price'          : next_package_price,
            'next_package_original_price' : next_package_original_price,
            'next_package_sales_order_id' : next_package_sales_order_id,
        })
        return customer


    @api.model
    def create(self, vals):
        validated = True

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

    @api.onchange('is_deferred')
    def onchange_is_deferred(self):
        all_partner_ids = []
        opportunity = False
        for partner in self:
            all_partner_ids = partner.search([('customer', '=', True)])
        if self.is_deferred:
            for partner in all_partner_ids:
                if partner.id == self._origin.id:
                    opportunity = self.env['crm.lead'].search([('partner_id', '=', partner.id)])
                    # Show 'Create service request' button in opportunity .
                    if opportunity:
                        opportunity.write({
                            'is_customer_deferred': True,
                            'probability': 100,
                        })
        else:
            for partner in all_partner_ids:
                if partner.id == self._origin.id:
                    opportunity = self.env['crm.lead'].search([('partner_id', '=', partner.id)])
                    # Remove 'Create service request' button in opportunity .
                    if opportunity:
                        opportunity.write({
                            'is_customer_deferred': False,
                            'probability': 98,
                        })

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

