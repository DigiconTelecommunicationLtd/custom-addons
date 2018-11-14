# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timezone, timedelta
import datetime

DEFAULT_THRESHOLD_DAYS = 7

class CronJobModel(models.Model):
    _name = 'isp_crm.cron_job'

    name = fields.Char("name", required=False)

    @api.model
    def send_customer_invoice_in_email(self):
        today = datetime.datetime.today()
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

    @api.model
    def td_change_color_for_pending_tickets_in_l2_l3(self):
        today = datetime.datetime.now()
        helpdesk_td_ticket_complexity_l2 = self.env['isp_crm_module.helpdesk_td_ticket_complexity'].search(
            [('name', '=', 'L-2')], limit=1)
        helpdesk_td_ticket_complexity_l3 = self.env['isp_crm_module.helpdesk_td_ticket_complexity'].search(
            [('name', '=', 'L-3')], limit=1)
        tickets_list = self.env['isp_crm_module.helpdesk_td'].search(
            [('default_stages', '!=', 'Done'),'|',('complexity', '=', helpdesk_td_ticket_complexity_l2.id),
             ('complexity', '=', helpdesk_td_ticket_complexity_l3.id)])
        for ticket in tickets_list:
            level_lastUpdated = ticket.level_change_time
            fmt = '%Y-%m-%d %H:%M:%S'
            d1 = datetime.datetime.strptime(level_lastUpdated, fmt)
            diff = today-d1
            hours = diff.total_seconds() / 3600
            if ticket.complexity.id == helpdesk_td_ticket_complexity_l2.id:
                if hours > 16.00:
                    ticket.update(
                        {
                            'color': 3,
                        }
                    )
                else:
                    print("No need to update color")
            else:
                if hours > 24.00:
                    ticket.update(
                        {
                            'color': 3,
                        }
                    )
                else:
                    print("No need to update color")
        return True
