# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timezone, timedelta

DEFAULT_THRESHOLD_DAYS = 7

class CronJobModel(models.Model):
    _name = 'isp_crm.cron_job'

    name = fields.Char("name", required=False)

    @api.model
    def send_customer_invoice_in_email(self):
        today = datetime.today()
        after_threshold_days_date = int(today.day) + int(DEFAULT_THRESHOLD_DAYS)
        customers_list = self.env['res.partner'].search([('customer', '=', True), ('bill_cycle_date', '=', after_threshold_days_date)])
        service_request_obj = self.env['isp_crm_module.service_request']
        for customer in customers_list:
            print("Creating Invoice for customer:- " + customer.name)
            created_invoice_obj = service_request_obj.create_invoice_for_customer(customer=customer)
            if created_invoice_obj:
                mail_sent = service_request_obj.send_invoice_to_customer(invoice=created_invoice_obj)
                if mail_sent:
                    print("Mail Sent for customer:- " + customer.name)
                else:
                    print("Some Error is occurred.")