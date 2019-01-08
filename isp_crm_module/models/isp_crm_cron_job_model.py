# -*- coding: utf-8 -*-
import re

import base64
from odoo import models, fields, api
from odoo.exceptions import Warning, UserError
from datetime import datetime, timezone, timedelta, date

DEFAULT_THRESHOLD_DAYS = 7

DEFAULT_MONTH_DAYS = 30
DEFAULT_NEXT_MONTH_DAYS = 31
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
CUSTOMER_INCATIVE_STATUS = 'inactive'

INVOICE_PAID_STATUS = 'paid'

class CronJobModel(models.Model):
    _name = 'isp_crm.cron_job'

    name = fields.Char("name", required=False)

    def _get_next_package_end_date(self, given_date):
        given_date_obj = datetime.strptime(given_date, DEFAULT_DATE_FORMAT)
        package_end_date_obj = given_date_obj + timedelta(days=DEFAULT_MONTH_DAYS)
        return package_end_date_obj.strftime(DEFAULT_DATE_FORMAT)

    def _get_next_package_start_date(self, given_date):
        given_date_obj = datetime.strptime(given_date, DEFAULT_DATE_FORMAT)
        package_start_date_obj = given_date_obj + timedelta(days=DEFAULT_NEXT_MONTH_DAYS)
        return package_start_date_obj.strftime(DEFAULT_DATE_FORMAT)

    def _send_mail_to_customer_before_some_days(self, customer):
        """
        Sending mail to the customers which bill cycle date will end next week
        :param customer: to whom the mail is to be sent
        :return: boolean response
        """
        template_obj = self.env['res.partner'].sudo().search(
                [('name', '=', 'sending_invoice_for_warning_the_customer')],
                limit=1)
        self.mail_to = customer.email
        self.mail_cc = customer.email
        body = template_obj.body_html
        body = body.replace('--customer_id--', str(customer.subscriber_id))
        body = body.replace('--package--', str(customer.next_package_id.name or ""))
        body = body.replace('--price--', str(customer.next_package_price))
        if customer.current_package_end_date:
            body = body.replace('--last_payment_date--', str(datetime.strptime(str(customer.current_package_end_date),'%Y-%m-%d').strftime("%d-%m-%Y")))
        else:
            body = body.replace('--last_payment_date--', str(customer.current_package_end_date))

        # Creating attachment file of the invoice
        sales_order_obj = self.env['sale.order'].search([], order='create_date asc', limit=1)
        pdf = self.env.ref('isp_crm_module.action_report_receipt_attachment').render_qweb_pdf([sales_order_obj[0].id])

        # save pdf as attachment
        # ATTACHMENT_NAME = customer.name + "_" + invoice.number
        ATTACHMENT_NAME = customer.name
        attachment = self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas_fname': ATTACHMENT_NAME + '.pdf',
            'store_fname': ATTACHMENT_NAME,
            'datas': base64.encodestring(pdf[0]),
            'mimetype': 'application/x-pdf'
        })

        if template_obj:
            mail_values = {
                'subject': template_obj.subject_mail,
                'body_html': body,
                'email_to': self.mail_to,
                'email_cc': self.mail_cc,
                'email_from': 'notice.mime@cg-bd.com',
                'attachment_ids': [(6, 0, [attachment.id])],
            }
            create_and_send_email = self.env['mail.mail'].create(mail_values).send()
        return create_and_send_email


    def _default_account(self):
        """
        Default account for payment of this invoice line
        :return: account id (str)
        """
        journal = self.env['account.journal'].search([('code', '=', 'INV')])[0]
        return journal.default_credit_account_id.id

    def _create_invoice_line_from_products_and_price(self, product, product_price):
        """
        Creating a invoice line for the product
        :param product: product for which the invoice line is creating
        :param product_price: price of the given product
        :return: created invoice line object
        """
        invoice_line_data = {}
        invoice_line_data = {
            'account_id'    : self._default_account(),
            'product_id'    : product.id,
            'name'          : product.name,
            'quantity'      : 1,
            'price_unit'    : product_price,
        }
        return invoice_line_data

    def _get_next_months_invoice(self, customer):
        """
        Returns the next months invoice for given customer
        :param customer: for whonm the invoice will be returned
        :return: invoice object
        """
        customers_last_sale_order = self.env['sale.order'].search([
                ('partner_id', '=', customer.id),
                ('state', '=', 'sale'),
                ('confirmation_date', '!=', None),
            ],
            order='create_date desc',
            limit=1
        )

        if len(customers_last_sale_order):
            product = customer.next_package_id
            product_price = customer.next_package_price
            invoice_line_data = self._create_invoice_line_from_products_and_price(product=product, product_price=product_price)
            invoice_obj = self.env['account.invoice']
            invoice_data = {
                'partner_id' : customer.id,
                'state' : 'draft',
                'payment_term_id' : '',
                'invoice_line_ids' : [(0, 0, invoice_line_data)],
                'origin' : customers_last_sale_order.name,
                'date_invoice' : fields.Date.today(),
                'date_due' : customer.current_package_end_date,
            }
            created_invoice_obj = invoice_obj.create(invoice_data)
            created_invoice_obj.action_invoice_open()
            return created_invoice_obj

    def create_customer_invoice_status(self, customer):
        customer_invoice_status_obj = self.env['isp_crm_module.customer_invoice_status'].search([])
        customer_invoice_status_obj.create({
            'customer_id' : customer.id,
        })
        return customer_invoice_status_obj

    @api.model
    def send_customer_invoice_in_email(self):
        """
        Function for running in a cron job to send mail to the customer which
        bill cycle will be completed after 7days
        :return: boolean response
        """
        today = datetime.today()
        after_threshold_days_date =  today + timedelta(days=DEFAULT_THRESHOLD_DAYS)
        after_threshold_days_date_str = after_threshold_days_date.strftime("%Y-%m-%d")
        customers_list = self.env['res.partner'].search([
            ('customer', '=', True),
            ('current_package_end_date', '=', after_threshold_days_date)
        ])

        service_request_obj = self.env['isp_crm_module.service_request']

        for customer in customers_list:
            print("Creating Invoice for customer:- " + customer.name)
            customer_invoice_status = self.create_customer_invoice_status(customer=customer)
            try:
                print("mail sending.....")
                mail_sent = self._send_mail_to_customer_before_some_days(customer=customer)
                print("mail sent")
            except Exception as ex:
                print(ex)


    @api.model
    def td_change_color_for_pending_tickets_in_l2_l3(self):
        today = datetime.now()
        helpdesk_td_ticket_complexity_l2 = self.env['isp_crm_module.helpdesk_td_ticket_complexity'].search(
            [('name', '=', 'L-2')], limit=1)
        helpdesk_td_ticket_complexity_l3 = self.env['isp_crm_module.helpdesk_td_ticket_complexity'].search(
            [('name', '=', 'L-3')], limit=1)
        if helpdesk_td_ticket_complexity_l2 and helpdesk_td_ticket_complexity_l3:
            tickets_list = self.env['isp_crm_module.helpdesk_td'].search(
                [('default_stages', '!=', 'Done'),'|',('complexity', '=', helpdesk_td_ticket_complexity_l2.id),
                 ('complexity', '=', helpdesk_td_ticket_complexity_l3.id)])
        else:
            raise UserError('Complexity level not set correctly.')
        for ticket in tickets_list:
            level_lastUpdated = ticket.level_change_time
            fmt = '%Y-%m-%d %H:%M:%S'
            d1 = datetime.strptime(level_lastUpdated, fmt)
            diff = today-d1
            hours = diff.total_seconds() / 3600
            if ticket.complexity.id == helpdesk_td_ticket_complexity_l2.id:
                if hours > float(int(re.search(r'\d+', str(helpdesk_td_ticket_complexity_l2.time_limit)).group())):
                    ticket.update(
                        {
                            'color': 3,
                        }
                    )
                else:
                    print("No need to update color")
            else:
                if hours > float(int(re.search(r'\d+', str(helpdesk_td_ticket_complexity_l3.time_limit)).group())):
                    ticket.update(
                        {
                            'color': 3,
                        }
                    )
                else:
                    print("No need to update color")
        return True

    def _update_customer_package_info(self, customer):
        """
        Updates customer's package info for next bil cycle
        :param customer: for whom the changes applies
        :return: customer obj
        """
        current_package_id = customer.next_package_id.id
        current_package_price = customer.next_package_price
        current_package_original_price = customer.next_package_id.unit_price
        current_package_sales_order_id = customer.next_package_sales_order_id
        current_package_start_date = customer.next_package_start_date
        current_package_end_date = self._get_next_package_end_date(given_date=current_package_start_date)

        next_package_id = current_package_id
        next_package_price = current_package_price
        next_package_original_price = current_package_original_price
        next_package_sales_order_id = current_package_sales_order_id
        next_package_start_date = customer._get_next_package_start_date(given_date=current_package_start_date)

        customer.update({
            'current_package_id' : current_package_id,
            'current_package_price' : current_package_price,
            'current_package_original_price' : current_package_original_price,
            'current_package_sales_order_id' : current_package_sales_order_id,
            'current_package_start_date' : current_package_start_date,
            'current_package_end_date' : current_package_end_date,
            'next_package_id' : next_package_id,
            'next_package_price' : next_package_price,
            'next_package_original_price' : next_package_original_price,
            'next_package_sales_order_id' : next_package_sales_order_id,
            'next_package_start_date' : next_package_start_date,
        })
        return customer

    @api.model
    def update_customer_package_for_next_bill_cycle(self):
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        customers_list = self.env['res.partner'].search([
            ('customer', '=', True),
            ('next_package_start_date', '=', tomorrow)
        ])
        for customer in customers_list:
            # Get customer balance
            customer_balance =  customer.get_customer_balance(customer_id=customer.id)
            # find their recent invoice that paid
            current_month_invoice = self.env['account.invoice'].search([
                ('partner_id', '=', customer.id),
                ('date_due', '=', today), ('state', '=', 'paid')
            ], limit=1)
            #
            # if current_month_invoice:
            #     self._update_customer_package_info(customer=customer)
            # else:
            #     pass

            # updating the customer active_status and package according to their balance
            if (customer_balance < 0) and (abs(customer_balance) >= customer.next_package_price):
                # updating account moves of customer
                payment_obj = self.env['account.payment']
                payment_obj.customer_bill_adjustment(
                    customer=customer,
                    package_price=customer.next_package_price
                )
                # updating package info of customer
                updated_customer = customer.update_current_bill_cycle_info(
                    customer=customer,
                    product_id=customer.next_package_id.id,
                    price=customer.next_package_price,
                    start_date=customer.next_package_start_date,
                )
                updated_customer = updated_customer.update_next_bill_cycle_info(
                    customer=updated_customer
                )
                # Adding the package change history
                package_history_obj = self.env['isp_crm_module.customer_package_history'].search([])
                created_package_history = package_history_obj.set_package_change_history(customer)
            else:
                customer.update({
                    'active_status' : CUSTOMER_INCATIVE_STATUS
                })
        return True

    def send_notification_after_invoice_due_date(self):
        """
        Function to send notification to user if invoice's due date is over.
        :return:
        """
        invoices = self.env['account.invoice'].search([])
        present = datetime.now()
        for invoice in invoices:
            if invoice.date_due:
                if present.date() > datetime.strptime(invoice.date_due, "%Y-%m-%d").date() and invoice.state != INVOICE_PAID_STATUS:
                    message = "Invoice\'s due date is over. Custome's name: '"+str(invoice.partner_id.name) + "' and Customer's Subscriber ID: '"+str(invoice.partner_id.subscriber_id)+"'"
                    invoice.user_id.notify_info(message)

    def delete_expired_reset_password_links(self):
        """
        Delete reset password links if expired.
        :return:
        """
        present = datetime.now().strftime("%Y-%m-%d %H-%M")
        present = datetime.strptime(present, "%Y-%m-%d %H-%M")
        links   = self.env['isp_crm_module.temporary_links'].search([])

        for link in links:
            link_creation_time = datetime.strptime(link.create_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H-%M")
            link_creation_time = datetime.strptime(link_creation_time, "%Y-%m-%d %H-%M")
            time_difference         = str(present - link_creation_time)
            hour               = int(time_difference.split(":")[0])
            min                = int(time_difference.split(":")[1])

            # check if link is expired or not
            if hour > 0 or min > 10 :
                # Delete the expired link
                link.unlink()
        return True
