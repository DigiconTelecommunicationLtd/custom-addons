# -*- coding: utf-8 -*-


from ast import literal_eval
from datetime import datetime, timedelta
from odoo import http
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
import odoo.addons.decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

CUSTOMER_TYPE = [
    ('retail', _('Retail')),
    ('corporate', _('Corporate')),
    ('soho', _('SOHO')),
    ('sme', _('SME')),
]

class ISPCRMPayment(models.Model):
    """Inherits account.payment and adds Functionality in account payment"""
    _name = 'isp_crm_module.payment_report'

    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    lead_type = fields.Selection(CUSTOMER_TYPE, string='Type', required=False, help="Lead and Opportunity Type", default='retail')

    @api.multi
    def get_report(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'lead_type': self.lead_type,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `get_report_values()` and pass `data` automatically.
        return self.env.ref('isp_crm_module.monthly_payment_report').report_action(self, data=data)


class ReportISPCRMPayment(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.isp_crm_module.monthly_payment_receive_view'

    @api.model
    def get_report_values(self, docids, data=None):
        date_start = datetime.strptime(data['form']['date_start'], DATE_FORMAT)
        date_end = datetime.strptime(data['form']['date_end'], DATE_FORMAT) + timedelta(days=1)

        docs = []
        payments = self.env['account.payment'].search([('create_date', '>=', date_start.strftime(DATETIME_FORMAT)),('create_date', '<=', date_end.strftime(DATETIME_FORMAT))], order='id asc')
        for payment in payments:
            check_retail_or_corporate = self.env['res.partner'].search([('subscriber_id', '=', payment.partner_id.subscriber_id)], limit=1)

            if data['form']['lead_type'] == 'retail':
                if "MR" in str(payment.partner_id.subscriber_id):
                    docs.append({
                        'customer_id': payment.customer_id,
                        'customer_name': payment.customer_name,
                        'package_name': payment.package_name,
                        'bill_cycle': str(payment.bill_start_date) + " to " +str(payment.bill_end_date),
                        'bill_amount': payment.bill_amount,
                        'received_amount': payment.received_amount,
                        'payment_gateway_service_charge': payment.deducted_amount,
                        'bill_payment_date': payment.bill_payment_date,
                        'card_type': payment.card_type,
                        'card_number': payment.card_number,
                        'billing_status': payment.billing_status,
                    })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start.strftime(DATE_FORMAT),
            'date_end': (date_end - timedelta(days=1)).strftime(DATE_FORMAT),
            'docs': docs,
        }


