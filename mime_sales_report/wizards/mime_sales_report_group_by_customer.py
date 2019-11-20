# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from datetime import datetime, timezone, timedelta, date
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
REPORT_DATE_FORMAT = '%B {S}, %Y'
CUSTOMER_TYPE = [
    # ('retail', 'Retail'),
    ('corporate', 'Corporate'),
    ('sohoandsme', 'SOHO and SME')
]
class MimeSalesReportRetailGROUPByCustomer(models.TransientModel):

    _name = 'mime_sales_report.customer_transient_by_group'
    _auto = False
    _log_access = True
    create_uid = fields.Integer('ID')
    res_id = fields.Integer()
    customer_name = fields.Char()
    lead_type = fields.Char()
    total_recieveable_amount = fields.Float()
    total_due_amount = fields.Float()
    total_payable = fields.Float()

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'mime_sales_report_customer_transient_by_group')

        self._cr.execute("""
            CREATE OR REPLACE VIEW mime_sales_report_customer_transient_by_group AS (
                             SELECT
                            row_number() OVER () as id,
			                 row_number() OVER () as create_uid,
                             row_number() OVER () as write_uid,
                             '2019-02-05' as write_date,	
                             '2019-02-05' as create_date,
                             res_partner.id as res_id,
                             res_partner.name as customer_name,
                             lead_type,
                             SUM(account_invoice.toal_amount_otc_mrc) as total_recieveable_amount,
                             SUM(account_invoice.residual_signed) as total_due_amount,
                             SUM(account_invoice.toal_amount_otc_mrc - account_invoice.residual_signed) as total_payable
                             FROM res_partner
                             RIGHT OUTER JOIN account_invoice on res_partner.id=account_invoice.partner_id
                             RIGHT OUTER JOIN crm_lead on account_invoice.partner_id=crm_lead.partner_id
                             where
                             is_potential_customer = false and
                             (state = 'open' or state = 'paid') 
			                 GROUP BY res_id,lead_type
                     )""")



    @api.multi
    def get_report(self,lead_type):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'lead_type': lead_type,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `get_report_values()` and pass `data` automatically.
        return self.env.ref('mime_sales_report.group_sales_report').report_action(self, data=data)

class MimeSalesReportRetailGroupAbstract(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.mime_sales_report.sales_group_report_view'

    @api.model
    def get_report_values(self, docids, data=None):

        lead_type_report = ('lead_type', '=', data['form']['lead_type'])
        domain= []
        domain.append(lead_type_report)
        docs=[]
        grand_recieveable = 0
        grand_paid = 0
        grand_due = 0
        all_data=self.env['mime_sales_report.customer_transient_by_group'].search(domain)
        print(len(all_data))
        for data in all_data:
            print(data.customer_name,data.total_recieveable_amount,data.total_payable,data.total_due_amount)
            total_recieveable_amount = data.total_recieveable_amount
            total_payable = data.total_payable
            total_due_amount = data.total_due_amount

            grand_recieveable = grand_recieveable + total_recieveable_amount
            grand_paid = grand_paid + total_payable
            grand_due = grand_due + total_due_amount

            docs.append({
                'customer_name':data.customer_name,
                'total_recieveable': "{0:.2f}".format(total_recieveable_amount),
                'total_paid': "{0:.2f}".format(total_payable),
                'total_due': "{0:.2f}".format(total_due_amount)
            })
        docs.append({
            'customer_name': 'Total',
            'total_recieveable': "{0:.2f}".format(grand_recieveable),
            'total_paid': "{0:.2f}".format(grand_paid),
            'total_due': "{0:.2f}".format(grand_due)
        })
        return {
            'doc_ids': 2323223,
            'doc_model': 'mime_sales_report.customer_transient_by_group',
            'docs':docs
            # 'customer_name':lead_type_display,
            # 'total_recieveable': docs_new,
            # 'total_paid':docs_old,
            # 'total_due':grand_recieveable,

        }





