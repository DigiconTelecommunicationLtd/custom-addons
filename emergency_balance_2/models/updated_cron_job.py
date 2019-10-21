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
            print('cronjob*********************')
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
                ('customer', '=', True)])
            for customer in customers_list:
                # Get customer balance
                customer_balance =  customer.get_customer_balance(customer_id=customer.id)
                #print(customer_balance)
                #update customer balance for emergency. add due only if today passed emergency valid till
                # if customer.has_due:
                #     custom_valid_till = datetime.strptime(customer.new_next_start_date, DEFAULT_DATE_FORMAT)
                #     if today_new > custom_valid_till:
                #         customer_balance = customer_balance + customer.emergency_balance_due_amount
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

                elif str(customer.next_package_start_date) == str(today) or customer.active_status == CUSTOMER_INACTIVE_STATUS or customer.has_due == True:
                    #change the status of customer from new to existing
                    if str(customer.next_package_start_date) == str(today):
                        customer.update({
                            'is_existing_user': True
                        })

                    # updating the customer active_status and package according to their balance

                    # add deferred payment patch
                    if str(customer.customer_state) == 'paid':
                        customer.update({
                            'is_deferred': False
                        })
                    due_amount_for_customer = 0.0
                    if customer.has_due:
                        custom_valid_till = datetime.strptime(customer.new_next_start_date, DEFAULT_DATE_FORMAT)
                        #custom_valid_till = custom_valid_till + timedelta(hours=6)
                        custom_valid_till = custom_valid_till + timedelta(hours=30)
                        if today_new > custom_valid_till:
                            # due_amount_for_customer = customer.emergency_balance_due_amount
                            due_amount_for_customer = customer.customer_total_due

                    if (customer_balance < 0) and (abs(
                            customer_balance) >= customer.total_monthly_bill+due_amount_for_customer):
                    # if (customer_balance < 0) and (abs(
                    #             customer_balance) >= customer.total_monthly_bill + due_amount_for_customer):
                        # updating account moves of customer
                        payment_obj = self.env['account.payment']
                        #adjust if customer has due
                        payment_obj.customer_bill_adjustment(
                                customer=customer,
                                package_price=customer.next_package_price + due_amount_for_customer
                                # package_price=customer.total_monthly_bill + due_amount_for_customer
                            )
                        # else:
                        #     payment_obj.customer_bill_adjustment(
                        #         customer=customer,
                        #         package_price=customer.next_package_price
                        #     )
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
                                #custom_due_date.strftime(DEFAULT_DATE_FORMAT)
                                #fix deferred thing
                                if customer.is_deferred == True and opportunity.lead_type == "retail":
                                    if str(customer.customer_state) == 'paid':
                                        updated_customer = customer.update_current_bill_cycle_info(
                                            customer=customer,
                                            product_id=customer.next_package_id.id,
                                            price=customer.next_package_price,
                                            # price=customer.total_monthly_bill,
                                            original_price=customer.next_package_original_price,
                                            start_date=today.strftime(DEFAULT_DATE_FORMAT),
                                        )
                                        updated_customer = updated_customer.update_next_bill_cycle_info(
                                            customer=updated_customer
                                        )
                                        updated_customer.update({
                                            'is_deferred':False
                                        })
                                        update_expiry_bandwidth(updated_customer.subscriber_id,
                                                                updated_customer.current_package_end_date,
                                                                updated_customer.current_package_id.name)

                                        #updated_customer.is_deferred = False

                                else:
                                    updated_customer = customer.update_current_bill_cycle_info(
                                        customer=customer,
                                        product_id=customer.next_package_id.id,
                                        price=customer.next_package_price,
                                        # price=customer.total_monthly_bill,
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
                                    # price=customer.total_monthly_bill,
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
                        if customer.has_due and opportunity.lead_type == "retail":
                            custom_valid_till = datetime.strptime(customer.new_next_start_date, DEFAULT_DATE_FORMAT)
                            today_new = datetime.now() + timedelta(hours=6)
                            #custom_valid_till = custom_valid_till + timedelta(hours=6)
                            custom_valid_till = custom_valid_till + timedelta(hours=30)

                            if today_new > custom_valid_till:
                                customer.update({
                                    'active_status': CUSTOMER_INACTIVE_STATUS
                                })
                        elif opportunity.lead_type == "retail":
                            customer.update({
                                'active_status': CUSTOMER_INACTIVE_STATUS
                            })

                #TEST PURPOSE
                elif opportunity.lead_type == "retail" and customer.has_due:
                    custom_valid_till = datetime.strptime(customer.new_next_start_date, DEFAULT_DATE_FORMAT)
                    #custom_valid_till = custom_valid_till + timedelta(hours=6)
                    custom_valid_till = custom_valid_till + timedelta(hours=30)
                    today_new = datetime.now() + timedelta(hours=6)



                    if today_new > custom_valid_till:
                        customer.update({
                            'active_status': CUSTOMER_INACTIVE_STATUS
                        })

                #deffered payment

                if opportunity.lead_type == "retail" and customer.is_deferred:
                    opportunity = self.env['crm.lead'].search([('partner_id', '=', customer.id)], limit=1)
                    if opportunity:
                        if opportunity.lead_type == "retail":
                            due_date = customer.isp_invoice_id.date_due
                            customer_state = str(customer.customer_state)
                            #check if paid or not
                            if customer_state!= 'False':
                                if customer_state!='paid':
                                    # check if date expired
                                    today_new = datetime.now() + timedelta(hours=6)
                                    two_days = today_new +  timedelta(days=2)

                                    custom_due_date = datetime.strptime(due_date, DEFAULT_DATE_FORMAT)
                                    custom_due_date = custom_due_date + timedelta(hours=30)

                                    if(today_new > custom_due_date):
                                        update_expiry_bandwidth(customer.subscriber_id,
                                                                custom_due_date.strftime(DEFAULT_DATE_FORMAT),
                                                                customer.current_package_id.name)

                                        customer.update({
                                            'active_status': CUSTOMER_INACTIVE_STATUS
                                        })
                                elif customer_state == 'paid':
                                    customer.update({
                                        'active_status': CUSTOMER_ACTIVE_STATUS
                                    })
                                    #update radius database
                                    update_expiry_bandwidth(customer.subscriber_id,
                                                            customer.current_package_end_date,
                                                            customer.current_package_id.name)




            return True
        except Exception as ex:
            print(ex)

    @api.model
    def send_customer_invoice_in_email(self):
        print('************************************** updated cusomter invoice email')
        """
        Function for running in a cron job to send mail to the customer which
        bill cycle will be completed after 7days
        :return: boolean response
        """
        today = datetime.today()
        after_threshold_days_date = today + timedelta(days=DEFAULT_THRESHOLD_DAYS)
        after_threshold_days_date_str = after_threshold_days_date.strftime("%Y-%m-%d")

        after_second_threshold_days_date = today + timedelta(days=DEFAULT_SECOND_THRESHOLD_DAYS)
        after_second_threshold_days_date_str = after_second_threshold_days_date.strftime("%Y-%m-%d")

        customers_list = self.env['res.partner'].search([
            ('customer', '=', True),
            '|',
            ('current_package_end_date', '=', after_threshold_days_date),
            ('current_package_end_date', '=', after_second_threshold_days_date)
        ])

        # customers_list = self.env['res.partner'].search([
        #     ('customer', '=', True)
        # ])

        service_request_obj = self.env['isp_crm_module.service_request']

        for customer in customers_list:
            # Check if the customer is corporate or not
            opportunities = self.env['crm.lead'].search([('partner_id', '=', customer.id)])
            for opportunity in opportunities:
                # check if lead type is corporate or soho or sme
                if opportunity.lead_type != "corporate":
                    # print("Creating Invoice for customer:- " + customer.name)
                    customer_invoice_status = self.create_customer_invoice_status(customer=customer)
                    try:
                        # print("mail sending.....")
                        if customer.real_ip:
                            mail_sent = self._send_mail_to_customer_before_some_days_real_ip(customer=customer)
                        else:
                            mail_sent = self._send_mail_to_customer_before_some_days(customer=customer)
                        # print("mail sent")
                    except Exception as ex:
                        print(ex)

    def _send_mail_to_customer_before_some_days_real_ip(self, customer):
        """
        Sending mail to the customers which bill cycle date will end next week
        :param customer: to whom the mail is to be sent
        :return: boolean response
        """
        template_obj = self.env['res.partner'].sudo().search(
                [('name', '=', 'sending_invoice_for_warning_the_customer_real_ip')],
                limit=1)
        self.mail_to = customer.email
        # self.mail_cc = customer.email
        body = template_obj.body_html
        body = body.replace('--customer_id--', str(customer.subscriber_id))
        if len(str(customer.name)) > 1:
            body = body.replace('--customer_name--', str(customer.name))
        else:
            body = body.replace('--customer_name--', "N/A")
        # show package info from customer's technical information.
        if customer.opportunity_ids.lead_type != "corporate":
            body = body.replace('--package--', str(customer.current_package_id.name or ""))
            body = body.replace('--price--', str(customer.next_package_price))
            body = body.replace('--realipprice--', str(customer.real_ip_subtotal))
            body = body.replace('--totalprice--', str(customer.next_package_price+customer.real_ip_subtotal))

            if customer.current_package_end_date:
                body = body.replace('--last_payment_date--', str(datetime.strptime(str(customer.current_package_end_date),'%Y-%m-%d').strftime("%d-%m-%Y")))
            else:
                body = body.replace('--last_payment_date--', str(customer.current_package_end_date))
        else:
            body = body.replace('--package--', str(customer.next_package_id.name or ""))
            body = body.replace('--price--', str(customer.next_package_price))
            if customer.current_package_end_date:
                body = body.replace('--last_payment_date--', str(
                    datetime.strptime(str(customer.current_package_end_date), '%Y-%m-%d').strftime("%d-%m-%Y")))
            else:
                body = body.replace('--last_payment_date--', str(customer.current_package_end_date))

        # Creating attachment file of the invoice
        # sales_order_obj = self.env['sale.order'].search([], order='create_date asc', limit=1)
        # pdf = self.env.ref('isp_crm_module.action_report_receipt_attachment').render_qweb_pdf([sales_order_obj[0].id])
        #
        # # save pdf as attachment
        # # ATTACHMENT_NAME = customer.name + "_" + invoice.number
        # ATTACHMENT_NAME = customer.name
        # attachment = self.env['ir.attachment'].create({
        #     'name': ATTACHMENT_NAME,
        #     'type': 'binary',
        #     'datas_fname': ATTACHMENT_NAME + '.pdf',
        #     'store_fname': ATTACHMENT_NAME,
        #     'datas': base64.encodestring(pdf[0]),
        #     'mimetype': 'application/x-pdf'
        # })

        if template_obj:
            mail_values = {
                'subject': template_obj.subject_mail,
                'body_html': body,
                'email_to': self.mail_to,
                # 'email_cc': self.mail_cc,
                'email_from': 'notice.mime@cg-bd.com',
                # 'attachment_ids': [(6, 0, [attachment.id])],
            }
            create_and_send_email = self.env['mail.mail'].create(mail_values).send()
        return create_and_send_email