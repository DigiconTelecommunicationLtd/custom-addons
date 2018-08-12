# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timezone, timedelta

class CronJobModel(models.Model):
    _name = 'isp_crm.cron_job'

    name = fields.Char("name", required=False)

    @api.model
    def send_customer_invoice_in_email(self):
        today = datetime.today()
        after_7_days =  today + timedelta(days=7)
        customers_list = self.env['res.partner'].search([('customer', '=', True), ('bill_cycle_date', '=', after_7_days)])
        for customer in customers_list:
            print(customer.email)
        return True