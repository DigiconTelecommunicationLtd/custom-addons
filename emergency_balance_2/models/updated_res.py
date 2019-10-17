# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime, timezone, timedelta, date
from odoo.addons.emergency_balance_2.models.color_code import *
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class updated_res(models.Model):
    _inherit = 'res.partner'

    emergency_date = fields.Integer(string='Emergency Balance', help="Emergency Balance")
    emergency_balance_due_amount =  fields.Float('Due Amount', required=True,
                                          default=0.0,
                                          track_visibility='onchange')
    emergency_due_date = fields.Date(string='Emergency Valid Till',default=False,track_visibility='onchange')
    has_due = fields.Boolean(string='due?',
                            track_visibility='onchange')

    new_next_start_date =fields.Date(string="New Start Date", compute='_compute_new_start_date')
    isp_invoice_id = fields.Many2one('account.invoice', string='Invoice',ondelete='restrict', track_visibility='onchange',default=False)
    customer_balance = fields.Char(string='Balance',compute='_compute_customer_balance')
    customer_state = fields.Char(compute='_compute_state', string="State")
    amount_total_signed = fields.Float(compute='_compute_state', string="Invoiced Amount")
    customer_total_due = fields.Float(compute='_compute_due', string="Due")
    comment = fields.Html('Notes')

    #for the report
    is_existing_user = fields.Boolean(string='existing?',
                            track_visibility='onchange',default=True)
    new_customer_date =  fields.Date(string='New Customer Date',default=False,track_visibility='onchange')

    #get bill from service request line
    total_monthly_bill = fields.Float(string="Monthly Bill",compute="_compute_bill_from_serivce_line")

    @api.multi
    def _compute_bill_from_serivce_line(self):
        total = 0.0
        for product in self.product_line:
            total=total+product.price_subtotal
        self.total_monthly_bill = total

    @api.one
    def _compute_due(self):
        total_due = 0.0
        for record in self:
        #     if record.is_deferred and str(record.customer_state)!='paid':
        #         total_due = record.amount_total_signed
        #         print('total_sign',str(total_due))
        #     if record.has_due:
        #         today_new = datetime.now() + timedelta(hours=6)
        #         custom_valid_till = datetime.strptime(record.new_next_start_date, DEFAULT_DATE_FORMAT)
        #         if today_new > custom_valid_till:
        #             total_due = record.emergency_balance_due_amount
        #         print('total_sign', str(total_due))
        # print('total_sign', str(total_due))
            if record.has_due:
                today_new = datetime.now() + timedelta(hours=6)
                custom_valid_till = datetime.strptime(record.new_next_start_date, DEFAULT_DATE_FORMAT)
                #custom_valid_till = custom_valid_till + timedelta(hours=6)
                custom_valid_till = custom_valid_till + timedelta(hours=30)
                if today_new > custom_valid_till:
                    total_due = record.emergency_balance_due_amount
            else:
                total_due = 0.0

        self.customer_total_due = round(total_due,2)

    @api.one
    def _compute_state(self):
        for record in self:
            record.customer_state=str(self.isp_invoice_id.state)
            print(str(self.isp_invoice_id.amount_total_signed))
            record.amount_total_signed = self.isp_invoice_id.amount_total_signed


    @api.one
    def _compute_new_start_date(self):
        for record in self:
            if record.has_due:
                due_date_obj = datetime.strptime(record.emergency_due_date, DEFAULT_DATE_FORMAT)
                modified_date_obj=due_date_obj + timedelta(hours=6)
                record.new_next_start_date = modified_date_obj.strftime(DEFAULT_DATE_FORMAT)
            else:
                record.new_next_start_date = record.current_package_end_date

    @api.one
    def _compute_customer_balance(self):
        balance="{0:.2f}".format(abs(self.env['res.partner'].get_customer_balance(self.id)))
        self.customer_balance = balance
        # for record in self:
        #     print(record)
        #     record.customer_balance=str(abs(record.get_customer_balance(record.subscriber_id)))


    @api.one
    def update_emergency_balance(self):
        for record in self:
            record.has_due = False
            record.emergency_due_date = False
            record.emergency_balance_due_amount = 0.0
            record.emergency_date = 0
            data = self.env['emergency.balance'].sudo().search(
                [('customer', '=', self.id), ('has_due', '=', 'true')], limit=1)

            data.has_due = False
            data.set_for_approval = False
            data.approved = False
            data.rejected = False
            data.due_paid = True
            data.state = 'paid'
            data.color=DUE_PAID

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
        # current_package_price           = price if price else customer.current_package_price
        # current_package_original_price  = original_price if original_price else customer.current_package_id.list_price
        current_package_start_date      = start_date if start_date else datetime.today().strftime(DEFAULT_DATE_FORMAT)
        current_package_end_date        = self._get_package_end_date(given_date=current_package_start_date)
        current_package_sales_order_id  = sales_order_id if sales_order_id else customer.current_package_sales_order_id.id

        current_package_price = 0.0
        current_package_original_price = 0.0
        for productline in customer.product_line:
            current_package_price= current_package_price + productline.price_subtotal
            current_package_original_price = current_package_original_price + productline.product_id.list_price


        print('******current_package_price',current_package_price)
        print('******current_package_original_price', current_package_original_price)
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
        # next_package_price          = price if price else customer.current_package_price
        # next_package_original_price = price if price else customer.current_package_original_price
        next_package_sales_order_id = sales_order_id if sales_order_id else customer.current_package_sales_order_id.id

        next_package_price = 0.0
        next_package_original_price = 0.0
        for productline in customer.product_line:
            next_package_price = next_package_price + productline.price_subtotal
            next_package_original_price = next_package_original_price + productline.product_id.list_price

        print('******next_package_price', next_package_price)
        print('******next_package_original_price', next_package_original_price)
        customer.update({
            'next_package_id'             : next_package_id,
            'next_package_start_date'     : next_package_start_date,
            'next_package_price'          : next_package_price,
            'next_package_original_price' : next_package_original_price,
            'next_package_sales_order_id' : next_package_sales_order_id,
            'is_sent_package_change_req_from_technical_information' : True,
        })
        return customer