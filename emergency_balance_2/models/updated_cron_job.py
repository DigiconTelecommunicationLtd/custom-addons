# -*- coding: utf-8 -*-
import re

import base64
from odoo import models, fields, api
from odoo.exceptions import Warning, UserError
import datetime
from datetime import datetime, timezone, timedelta, date
from dateutil.relativedelta import relativedelta

DEFAULT_THRESHOLD_DAYS = 7
DEFAULT_SECOND_THRESHOLD_DAYS = 3
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

DEFAULT_MONTH_DAYS = 30
DEFAULT_NEXT_MONTH_DAYS = 31
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
CUSTOMER_INACTIVE_STATUS = 'inactive'
CUSTOMER_ACTIVE_STATUS = 'active'
DEFAULT_DONE_STAGE = 'Done'
DEFAULT_PACKAGES_CATEGORY_NAME = 'Packages'


INVOICE_PAID_STATUS = 'paid'
from odoo.addons.isp_crm_module.models.radius_integration import *

class UpdateCronJobModel(models.Model):
    _inherit = 'isp_crm.cron_job'


    @api.model
    def update_customer_package_for_next_bill_cycle(self):
        try:
            today_new = datetime.now() + timedelta(hours=6)
            today = today_new.date()
            #today = date.today()

            tomorrow = today + timedelta(days=1)
            # Check if it is a customer,
            # and if the customer is inactive or next package start date is tomorrow.
            # If the customer is inactive, then we will check if
            # the customer has sufficient balance otherwise
            # if the customer is active and next package start date is tomorrow then check if
            # the customer has sufficient balance.
            # If the customer has sufficient balance then reactivate the customer
            customers_list = self.env['res.partner'].search([
                ('customer', '=', True)
            ])
            for customer in customers_list:
                # Get customer balance
                customer_balance =  customer.get_customer_balance(customer_id=customer.id)
                #update customer balance for emergency. add due only if today passed emergency valid till
                if customer.has_due:
                    custom_valid_till = datetime.strptime(customer.new_next_start_date, DEFAULT_DATE_FORMAT)
                    if today_new > custom_valid_till:
                        customer_balance = customer_balance + customer.emergency_balance_due_amount
                # find their invoices that are paid
                current_month_invoice = self.env['account.invoice'].search([
                    ('partner_id', '=', customer.id),
                    ('state', '=', 'paid')
                ], limit=1)
                #
                # if current_month_invoice:
                #     self._update_customer_package_info(customer=customer)
                # else:
                #     pass
                opportunity = self.env['crm.lead'].search([('partner_id', '=', customer.id)], limit=1)
                ticket_obj = self.env['isp_crm_module.corporate_bandwidth_change']
                ticket = self.env['isp_crm_module.corporate_bandwidth_change']
                if opportunity:
                    if opportunity.lead_type != "retail":
                        ticket = ticket_obj.search(
                            [('customer', '=', customer.id), ('color', '=', 5), ('default_stages', '=', DEFAULT_DONE_STAGE)], order='create_date desc', limit=1)
                    else:
                        ticket_obj = self.env['isp_crm_module.retail_soho_bandwidth_change']
                        ticket = ticket_obj.search(
                            [('customer', '=', customer.id), ('color', '=', 5), ('default_stages', '=', DEFAULT_DONE_STAGE)], order='create_date desc', limit=1)
                if ticket:
                    # updating the customer active_status and package according to their balance
                    if ticket.default_stages == DEFAULT_DONE_STAGE and ticket.color == 5:
                        # updating account moves of customer
                        payment_obj = self.env['account.payment']
                        payment_obj.customer_bill_adjustment(
                            customer=customer,
                            package_price=customer.next_package_price
                        )
                        # updating package info of customer
                        sale_order_lines = customer.next_package_sales_order_id.order_line
                        original_price = 0.0
                        for sale_order_line in sale_order_lines:
                            discount = (sale_order_line.discount * sale_order_line.price_subtotal) / 100.0
                            original_price_sale_order_line = sale_order_line.price_subtotal + discount
                            original_price = original_price + original_price_sale_order_line

                        check_customer = self.env['res.partner'].search([('id', '=', customer.id)], limit=1)
                        if check_customer:
                            # get the opportunity of the customer, one customer should have one opportunity.
                            opportunity = self.env['crm.lead'].search([('partner_id', '=', check_customer.id)], limit=1)
                            if opportunity and opportunity.lead_type != "sohoandsme":
                                updated_customer = customer.update_current_bill_cycle_info(
                                    customer=customer,
                                    product_id=customer.next_package_id.id,
                                    price=customer.next_package_price,
                                    original_price = customer.next_package_original_price,
                                    start_date=customer.next_package_start_date,
                                )
                                updated_customer = updated_customer.update_next_bill_cycle_info(
                                    customer=updated_customer
                                )

                            else:
                                # same as corporate
                                today = datetime.today()
                                next_month_first_day = str(datetime(today.year, today.month + 1, 1)).split(" ")[0]
                                updated_customer = customer.update_current_bill_cycle_info(
                                    customer=customer,
                                    product_id=customer.next_package_id.id,
                                    price=customer.next_package_price,
                                    original_price=customer.next_package_original_price,
                                    start_date=customer.next_package_start_date,
                                )
                                updated_customer = updated_customer.update_next_bill_cycle_info(
                                    customer=updated_customer
                                )

                        ### Start of adding package change history ###
                        # Adding the package change history.
                        package_history_obj = self.env['isp_crm_module.customer_package_history'].search([])
                        # Update Last Package's end date
                        last_package_history_obj = package_history_obj.search([
                            ('customer_id', '=', customer.id),
                            # ('package_id', '=', customer.current_package_id.id),
                        ],
                            order='create_date desc',
                            limit=1
                        )
                        last_package_history_obj.update({
                            'end_date': today,
                        })
                        package_history_obj.create_new_package_history(customer=customer, package=customer.next_package_id,
                                                    start_date=str(customer.next_package_start_date))
                        ### End of adding package change history ###


                        ### Start change customer service info ###
                        created_product_line_list = []
                        customer_product_line_obj = self.env['isp_crm_module.customer_product_line']
                        created_product_line = customer_product_line_obj.create({
                            'customer_id': customer.id,
                            'name': customer.next_package_id.name,
                            'product_id': customer.next_package_id.id,
                            'product_updatable': False,
                            'product_uom_qty': (customer.next_package_price / customer.next_package_id.lst_price),
                            'product_uom': customer.next_package_id.uom_id.id,
                            'price_unit': customer.next_package_id.lst_price,
                            'price_subtotal': customer.next_package_price,
                            'price_total': customer.next_package_price,
                        })
                        created_product_line_list.append(created_product_line.id)
                        customer.update({
                            'product_line': [(6, None, created_product_line_list)]
                        })
                        ### End change customer service info ###

                        # Make customer active
                        customer.update({
                            'active_status': CUSTOMER_ACTIVE_STATUS
                        })
                        # TODO UPDATE BILL CYCLE AFTER BANDWITDH CHANGE
                        update_expiry_bandwidth(customer.subscriber_id,
                                                customer.current_package_end_date,
                                                customer.current_package_id.name)
                        ticket.write({
                            'color': 7
                        })

                        if opportunity.lead_type != "retail":
                            ticket.write({
                                'bandwidth': ticket.proposed_bandwidth,
                                'old_package_price': ticket.current_package_price,
                                'current_package_price': ticket.proposed_package_price
                            })

                elif str(customer.next_package_start_date) == str(tomorrow) or customer.active_status == CUSTOMER_INACTIVE_STATUS:
                    # updating the customer active_status and package according to their balance
                    if (customer_balance < 0) and (abs(
                            customer_balance) >= customer.next_package_price):
                        # updating account moves of customer
                        payment_obj = self.env['account.payment']
                        payment_obj.customer_bill_adjustment(
                            customer=customer,
                            package_price=customer.next_package_price
                        )
                        # updating package info of customer
                        sale_order_lines = customer.next_package_sales_order_id.order_line
                        original_price = 0.0
                        for sale_order_line in sale_order_lines:
                            discount = (sale_order_line.discount * sale_order_line.price_subtotal) / 100.0
                            original_price_sale_order_line = sale_order_line.price_subtotal + discount
                            original_price = original_price + original_price_sale_order_line

                        check_customer = self.env['res.partner'].search([('id', '=', customer.id)], limit=1)
                        if check_customer:
                            # get the opportunity of the customer, one customer should have one opportunity.
                            opportunity = self.env['crm.lead'].search([('partner_id', '=', check_customer.id)], limit=1)
                            if opportunity and opportunity.lead_type != "sohoandsme":
                                updated_customer = customer.update_current_bill_cycle_info(
                                    customer=customer,
                                    product_id=customer.next_package_id.id,
                                    price=customer.next_package_price,
                                    original_price=customer.next_package_original_price,
                                    start_date=customer.next_package_start_date,
                                )
                                updated_customer = updated_customer.update_next_bill_cycle_info(
                                    customer=updated_customer
                                )

                            else:
                                # if soho and sme, then bill cycle will start form the start of the next month
                                today = datetime.today()
                                next_month_first_day = str(datetime(today.year, today.month + 1, 1)).split(" ")[0]
                                updated_customer = customer.update_current_bill_cycle_info(
                                    customer=customer,
                                    product_id=customer.next_package_id.id,
                                    price=customer.next_package_price,
                                    original_price=customer.next_package_original_price,
                                    start_date=customer.next_package_start_date,
                                )
                                updated_customer = updated_customer.update_next_bill_cycle_info(
                                    customer=updated_customer
                                )

                        # Make customer active
                        customer.update({
                            'active_status': CUSTOMER_ACTIVE_STATUS
                        })
                        #TODO UPDATE BILL CYCLE
                        update_expiry_bandwidth(updated_customer.subscriber_id,
                                                updated_customer.current_package_end_date, customer.current_package_id.name)
                        if updated_customer.has_due:
                            updated_customer.update_emergency_balance()
                    else:
                        # if customer.is_sent_package_change_req == True:
                        #     updated_customer = customer.update_next_bill_cycle_info(customer=customer)
                        # else:
                        #     customer.update({
                        #         'active_status': CUSTOMER_INACTIVE_STATUS
                        #     })
                        if customer.has_due:
                            custom_valid_till = datetime.strptime(customer.new_next_start_date, DEFAULT_DATE_FORMAT)
                            today_new = datetime.now() + timedelta(hours=6)

                            print(today_new,custom_valid_till)

                            if today_new > custom_valid_till:
                                customer.update({
                                    'active_status': CUSTOMER_INACTIVE_STATUS
                                })
                        else:
                            customer.update({
                                'active_status': CUSTOMER_INACTIVE_STATUS
                            })

                #TEST PURPOSE
                elif customer.has_due:
                    custom_valid_till = datetime.strptime(customer.new_next_start_date, DEFAULT_DATE_FORMAT)
                    today_new = datetime.now() + timedelta(hours=6)

                    print(today_new, custom_valid_till)

                    if today_new > custom_valid_till:
                        customer.update({
                            'active_status': CUSTOMER_INACTIVE_STATUS
                        })

            return True
        except Exception as ex:
            print(ex)