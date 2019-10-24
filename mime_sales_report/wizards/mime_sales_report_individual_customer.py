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
class MimeSalesReportRetailIndividualCustomer(models.TransientModel):

    _name = 'mime_sales_report.individucal_customer_transient'

    @api.multi
    def get_report(self,customer_id,lead_type):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'customer_id': customer_id,
                'lead_type': lead_type,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `get_report_values()` and pass `data` automatically.
        return self.env.ref('mime_sales_report.individual_sales_report').report_action(self, data=data)

class MimeSalesReportRetailIndividualCustomerAbstract(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.mime_sales_report.sales_individual_report_view'

    @api.model
    def get_report_values(self, docids, data=None):
        customer_id = data['form']['customer_id']
        lead_type = data['form']['lead_type']
        print(customer_id,lead_type)
        docs=[]
        total=0
        if lead_type == 'retail':
            payments=self.env['account.payment'].sudo().search([('partner_id','=',customer_id),('state','=','posted')])
            print(len(payments))
            for payment in payments:
                otc = 0
                print(payment.invoice_payment_type.name)
                print(payment.has_invoices)
                print(payment.invoice_ids)
                # count = count + 1
                # otc = 0
                # if count == len(payments):
                #     invoice_ref = self.env['account.invoice'].search([('partner_id', '=',customer_id),('status','=','paid')])
                if payment.invoice_payment_type.name == 'Installation Fee + Monthly Bill':
                    for invoice in payment.invoice_ids:

                        if invoice.state == 'paid':
                            print(invoice)
                            for invoiced_products in invoice.invoice_line_ids:
                                print(invoiced_products.product_id.name)
                                if 'Retail Installation Fee' in invoiced_products.product_id.name:
                                    otc = invoiced_products.price_subtotal
                                else:
                                    otc = 0
                mrc = (payment.amount - otc)
                total = total + mrc + otc
                docs.append({
                    'date_maturity': payment.payment_date,
                    'customer_name': payment.partner_id.name,
                    'mrc': mrc,
                    'otc': otc,
                    'total_recieveable': "{0:.2f}".format(payment.amount),
                    'total_paid': "{0:.2f}".format(payment.amount),
                    'total_due': 0,
                    'payment_date': payment.payment_date
                })

            docs.append({
                'date_maturity': '',
                'customer_name': '',
                'mrc': '',
                'otc': 'Total',
                'total_recieveable': "{0:.2f}".format(total),
                'total_paid': "{0:.2f}".format(total),
                'total_due': 0,
                'payment_date': ''
            })
        else:
            invoices = self.env['account.invoice'].search([('partner_id', '=', customer_id),
                                                           ('state', 'not in', ['draft', 'cancel']),
                                                           ])
            total_recieveable = 0.0
            total_paid = 0.0
            total_due = 0.0
            for invoice in invoices:
                otc = 0.0
                mrc = 0.0
                if invoice.corporate_otc_amount > 0.0:
                    otc = invoice.corporate_otc_amount
                    # mrc = invoice.amount_total_signed - invoice.corporate_otc_amount
                    mrc = invoice.toal_amount_otc_mrc - invoice.corporate_otc_amount
                else:
                    if invoice.state == 'paid':
                        otc = invoice.corporate_otc_amount
                        mrc = invoice.toal_amount_otc_mrc - invoice.corporate_otc_amount
                    if invoice.state == 'open':
                        # mrc = invoice.residual_signed
                        # mrc = invoice.residual
                        otc = invoice.corporate_otc_amount
                        mrc = invoice.toal_amount_otc_mrc - invoice.corporate_otc_amount

                if invoice.state == 'paid':
                    # total_recieveable = total_recieveable + invoice.amount_total_signed

                    total_recieveable = total_recieveable + invoice.toal_amount_otc_mrc
                    total_paid = total_paid + invoice.toal_amount_otc_mrc
                    payment_data=self.env['account.payment'].sudo().search([('communication','=',invoice.number)])
                    docs.append({
                        'date_maturity': invoice.date_due,
                        'customer_name': invoice.partner_id.name,
                        'mrc': "{0:.2f}".format(mrc),
                        'otc': "{0:.2f}".format(otc),
                        'total_recieveable': "{0:.2f}".format(invoice.toal_amount_otc_mrc),
                        'total_paid': "{0:.2f}".format(invoice.toal_amount_otc_mrc),
                        'total_due': "{0:.2f}".format(0.0),
                        'payment_date': payment_data.payment_date
                    })

                elif invoice.state == 'open':
                    total_recieveable = total_recieveable + invoice.toal_amount_otc_mrc
                    total_paid = total_paid + (invoice.toal_amount_otc_mrc - invoice.residual)
                    total_due = total_due + invoice.residual
                    docs.append({
                        'date_maturity': invoice.date_due,
                        'customer_name': invoice.partner_id.name,
                        'mrc': "{0:.2f}".format(mrc),
                        'otc': "{0:.2f}".format(otc),
                        'total_recieveable': "{0:.2f}".format(invoice.toal_amount_otc_mrc),
                        'total_paid': "{0:.2f}".format(invoice.toal_amount_otc_mrc - invoice.residual),
                        'total_due': "{0:.2f}".format(invoice.residual),
                        'payment_date':''
                    })



            docs.append({
                'date_maturity': '',
                'customer_name': '',
                'mrc': '',
                'otc': 'Total',
                'total_recieveable': "{0:.2f}".format(total_recieveable),
                'total_paid': "{0:.2f}".format(total_paid),
                'total_due': "{0:.2f}".format(total_due),
                'payment_date':''
            })

        return {
            'doc_ids': 23232232,
            'doc_model': 'mime_sales_report.individucal_customer_transient',
            'lead_type': lead_type,
            'docs': docs,

        }







