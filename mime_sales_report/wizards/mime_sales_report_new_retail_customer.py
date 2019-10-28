# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from datetime import datetime, timezone, timedelta, date
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
REPORT_DATE_FORMAT = '%B {S}, %Y'
CUSTOMER_TYPE = [
    ('retail', 'Retail'),
    ('corporate', 'Corporate'),
    ('sohoandsme', 'SOHO and SME')
]
class MimeSalesReportRetailGroupBYCustomer(models.TransientModel):

    _name = 'mime_sales_report.new_customer_retail_transient'
    _auto = False
    _log_access = True
    create_uid = fields.Integer('ID')
    res_id = fields.Integer()
    customer_name = fields.Char()
    amount = fields.Float()




    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'mime_sales_report_new_customer_retail_transient')

        self._cr.execute("""
            CREATE OR REPLACE VIEW mime_sales_report_new_customer_retail_transient AS (
                            SELECT
                             row_number() OVER () as id,
                             res_partner.id as res_id,
                             res_partner.name as customer_name,
                             SUM(account_payment.amount) as amount,
                             row_number() OVER () as create_uid,
                             row_number() OVER () as write_uid, 
                             '2019-02-05' as write_date,
                             '2019-02-05' as create_date
                             FROM res_partner
                             RIGHT OUTER JOIN account_payment on res_partner.id=account_payment.partner_id
                             RIGHT OUTER JOIN crm_lead on account_payment.partner_id=crm_lead.partner_id
                             where
                             is_potential_customer = false and 
                             lead_type = 'retail' and 
                             is_potential_customer = false and 
                             account_payment.state = 'posted'
                             GROUP BY res_id
                     )""")



    @api.multi
    def get_report(self,date):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,

        }
        print('asdsadasdsdasdasda')
        # use `module_name.report_id` as reference.
        # `report_action()` will call `get_report_values()` and pass `data` automatically.
        return self.env.ref('mime_sales_report.group_retail_sales_report').report_action(self, data=data)

class MimeSalesReportRetailNewCustomerAbstract(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.mime_sales_report.sales_group_retail_report_view'

    @api.model
    def get_report_values(self, docids, data=None):

        docs_new = []
        print('asdsadasdsdasdasda')
        #total for new customers
        new_total_recieveable = 0.0
        new_total_paid = 0.0
        new_total_due = 0.0
        filtered_customers_new = self.env['mime_sales_report.new_customer_retail_transient'].search([])
        print('****** new customer',len(filtered_customers_new))
        for customer in filtered_customers_new:
            new_total_recieveable = new_total_recieveable + customer.amount
            new_total_paid = new_total_paid + customer.amount
            new_total_due = new_total_due + 0.0


            docs_new.append({
                'customer_name': customer.customer_name,
                'total_recieveable': "{0:.2f}".format(customer.amount),
                'total_paid': "{0:.2f}".format(customer.amount),
                'total_due': 0.0,
            })

        docs_new.append({
            'customer_name': 'Total',
            'otc': 'Sub Total',
            'total_recieveable': "{0:.2f}".format(new_total_recieveable),
            'total_paid': "{0:.2f}".format(new_total_paid),
            'total_due': "{0:.2f}".format(new_total_due)
        })


        return {
            'doc_ids': 2323223,
            'doc_model': 'mime_sales_report.new_customer_retail_transient',
            'docs':docs_new
        }




