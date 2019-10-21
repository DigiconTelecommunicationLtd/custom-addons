# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from datetime import datetime, timezone, timedelta, date
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
CUSTOMER_TYPE = [
    ('retail', 'Retail'),
    ('corporate', 'Corporate'),
    ('sohoandsme', 'SOHO and SME')
]
class MimeSalesReportRetailNewCustomer(models.TransientModel):

    _name = 'mime_sales_report.new_customer_transient'
    _auto = False
    _log_access = True
    create_uid = fields.Integer('ID')
    res_id = fields.Integer()
    customer_name = fields.Char()
    amount = fields.Float()
    payment_date = fields.Date()
    communication = fields.Char()
    lead_type = fields.Char()
    is_existing_user = fields.Boolean()
    new_customer_date = fields.Date()
    billing_start_date = fields.Date()
    current_package_end_date = fields.Date()
    payment_state = fields.Char()
    mrc = fields.Float(compute='_calculate_billing_type')
    otc = fields.Float(compute='_calculate_billing_type')

    @api.one
    def _calculate_billing_type(self):

        if self.communication!=False and (len(self.communication) > 0) and self.is_existing_user==False:
            invoice_ref=self.env['account.invoice'].search([('number','=',self.communication)])
            for invoice in invoice_ref:
                if invoice.state == 'paid':
                    for invoiced_products in invoice.invoice_line_ids:
                        if 'Retail Installation Fee' in invoiced_products.product_id.name:
                            self.otc = invoiced_products.price_subtotal

                    self.mrc = (self.amount - self.otc)
        else:
            self.mrc = self.amount





    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'mime_sales_report_new_customer_transient')

        self._cr.execute("""
            CREATE OR REPLACE VIEW mime_sales_report_new_customer_transient AS (
                            SELECT
                             row_number() OVER () as id,
                             res_partner.id as res_id,
                             res_partner.name as customer_name,
                             account_payment.amount as amount,
                             account_payment.payment_date,
                             billing_start_date,
                             current_package_end_date,
                             account_payment.communication as communication,
                             account_payment.state as payment_state,
                             row_number() OVER () as create_uid,
                             row_number() OVER () as write_uid, 
                             current_package_start_date as write_date,
                             next_package_start_date as create_date,
                             is_existing_user,
                             new_customer_date,
                             lead_type
                             FROM res_partner
                             RIGHT OUTER JOIN account_payment on res_partner.id=account_payment.partner_id
                             RIGHT OUTER JOIN crm_lead on account_payment.partner_id=crm_lead.partner_id
                             where
                             is_potential_customer = false
                             ORDER BY account_payment.payment_date desc
                     )""")



    @api.multi
    def get_report(self,start_date,end_date,lead_type):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': str(start_date),
                'date_end': str(end_date),
                'lead_type': lead_type,
            },
        }

        # use `module_name.report_id` as reference.
        # `report_action()` will call `get_report_values()` and pass `data` automatically.
        return self.env.ref('mime_sales_report.sales_report').report_action(self, data=data)

class MimeSalesReportRetailNewCustomerAbstract(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.mime_sales_report.sales_report_view'

    @api.model
    def get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        lead_type_report = ('lead_type', '=', data['form']['lead_type'])
        print('********************',data['form']['lead_type'])

        start_date_obj=datetime.strptime(date_start, DEFAULT_DATE_FORMAT)
        end_date_obj = datetime.strptime(date_end, DEFAULT_DATE_FORMAT)

        if data['form']['lead_type'] == 'retail':

            ######################### NEW  RETAIL CUSTOMERS ######################################
            docs_new = []
            domain_new = []
            domain_new.append(lead_type_report)
            domain_data = ('new_customer_date', '>=', str(date_start))
            domain_new.append(domain_data)
            domain_data = ('new_customer_date', '<=', str(date_end))
            domain_new.append(domain_data)
            # domain_data = ('is_existing_user', '=', False)
            domain_new.append(domain_data)
            domain_data=('payment_state','=','posted')
            domain_new.append(domain_data)

            domain_data = ('payment_date', '>=', str(date_start))
            domain_new.append(domain_data)
            domain_data = ('payment_date', '<=', str(date_end))
            domain_new.append(domain_data)




            #total for new customers
            new_total_recieveable = 0.0
            new_total_paid = 0.0
            new_total_due = 0.0
            filtered_customers_new = self.env['mime_sales_report.new_customer_transient'].search(domain_new)
            print('****** new customer',len(filtered_customers_new))
            for customer in filtered_customers_new:
                new_total_recieveable = new_total_recieveable + customer.amount
                new_total_paid = new_total_paid + customer.amount
                new_total_due = new_total_due + 0.0

                if data['form']['lead_type'] == 'retail':
                    docs_new.append({
                        'date_maturity': customer.payment_date,
                        'customer_name': customer.customer_name,
                        'mrc':customer.mrc,
                        'otc':customer.otc,
                        'total_recieveable': "{0:.2f}".format(customer.amount),
                        'total_paid': "{0:.2f}".format(customer.amount),
                        'total_due': 0.0,
                    })
                # else:
                #     #this is either corporate or soho so need to fetch the invoices.If open then not paid if paid then cool
                #
                #     print(self.env['account.invoice'].search([('partner_id','=',customer.res_id)]))
                #     docs_new.append({
                #         'date_maturity': customer.date_maturity,
                #         'customer_name': customer.customer_name,
                #         'mrc': customer.mrc,
                #         'otc': customer.otc,
                #         'total_recieveable': customer.mrc + customer.otc,
                #         'total_paid': customer.mrc + customer.otc,
                #         'total_due': 0.0,
                #     })
            #add sub total
            docs_new.append({
                'date_maturity': '',
                'customer_name': '',
                'mrc': '',
                'otc': 'Sub Total',
                'total_recieveable': "{0:.2f}".format(new_total_recieveable),
                'total_paid': "{0:.2f}".format(new_total_paid),
                'total_due': "{0:.2f}".format(new_total_due)
            })

            ######################### OLD RETAIL CUSTOMERS ######################################
            docs_old = []
            domain_old = []




            old_total_recieveable=0.0
            old_total_paid=0.0
            old_total_due=0.0


            # condition for Existing customer
            domain_old.append(lead_type_report)
            domain_data = ('current_package_end_date', '>=', str(date_start))
            domain_old.append(domain_data)
            domain_data = ('current_package_end_date', '<=', str(date_end))
            domain_old.append(domain_data)
            domain_data = ('is_existing_user', '=', True)
            domain_old.append(domain_data)
            domain_data = ('payment_state', '=', 'posted')
            domain_old.append(domain_data)

            domain_data = ('payment_date', '>=', str(date_start))
            domain_old.append(domain_data)
            domain_data = ('payment_date', '<=', str(date_end))
            domain_old.append(domain_data)

            filtered_customers_old = self.env['mime_sales_report.new_customer_transient'].search(domain_old)
            #for existing customers
            for customer in filtered_customers_old:
                old_total_recieveable = old_total_recieveable + (customer.mrc+customer.otc)
                old_total_paid = old_total_paid + (customer.mrc+customer.otc)
                old_total_due = old_total_due + 0.0

                if data['form']['lead_type'] == 'retail':
                    docs_old.append({
                        'date_maturity': customer.payment_date,
                        'customer_name': customer.customer_name,
                        'mrc': "{0:.2f}".format(customer.mrc),
                        'otc': "{0:.2f}".format(customer.otc),
                        'total_recieveable': "{0:.2f}".format(customer.mrc+customer.otc),
                        'total_paid': "{0:.2f}".format(customer.mrc+customer.otc),
                        'total_due': 0.0,
                    })
            docs_old.append({
                'date_maturity': '',
                'customer_name': '',
                'mrc': '',
                'otc': 'Sub Total',
                'total_recieveable': "{0:.2f}".format(old_total_recieveable),
                'total_paid': "{0:.2f}".format(old_total_paid),
                'total_due': "{0:.2f}".format(old_total_due)
            })

            #final touch
            lead_type_display=None
            if data['form']['lead_type']=='retail':
                lead_type_display='Retail'
            elif data['form']['lead_type']=='corporate':
                lead_type_display='Corporate'
            else:
                lead_type_display='SOHO and SME'

            grand_recieveable = "{0:.2f}".format(new_total_recieveable + old_total_recieveable)
            grand_paid = "{0:.2f}".format(new_total_paid + old_total_paid)
            grand_due = "{0:.2f}".format(new_total_due + old_total_due)
            # docs_old.append({
            #     'date_maturity': '',
            #     'customer_name': '',
            #     'mrc': '',
            #     'otc': 'Total',
            #     'total_recieveable': "{0:.2f}".format(grand_recieveable),
            #     'total_paid': "{0:.2f}".format(grand_paid),
            #     'total_due': "{0:.2f}".format(grand_due)
            # })

            return {
                'doc_ids': 2323223,
                'doc_model': 'mime_sales_report.new_customer_transient',
                'date_start': start_date_obj.strftime('%d, %b %Y'),
                'date_end': end_date_obj.strftime('%d, %b %Y'),
                # 'date_start':self.custom_strftime('%B {S}, %Y',start_date_obj),
                # 'date_end': self.custom_strftime('%B {S}, %Y',end_date_obj),
                'lead_type':lead_type_display,
                'docs_new': docs_new,
                'docs_old':docs_old,
                'grand_recieveable':grand_recieveable,
                'grand_paid':grand_paid,
                'grand_due':grand_due
            }

        else:
            #get all non retail customers

            ########################### CORPORATE/SOHO CUSTOMERS ###############################
            new_total_recieveable = 0.0
            new_total_paid = 0.0
            new_total_due = 0.0
            docs_new = []
            print(data['form']['lead_type'])
            if data['form']['lead_type'] == 'sohoandsme':
                new_corporate_partners=self.env['res.partner'].search([
                    ('subscriber_id', 'like', 'MS'),
                    ('is_potential_customer','=',False),
                    ('billing_start_date', '>=', str(date_start)),
                    ('billing_start_date', '<=', str(date_end)),



                ])
                existing_corporate_partners = self.env['res.partner'].search([
                    ('subscriber_id', 'like', 'MS'),
                    ('is_potential_customer', '=', False),
                    ('billing_start_date', '<', str(date_start)),

                ])

            else:
                new_corporate_partners = self.env['res.partner'].search([
                    ('subscriber_id', 'like', 'MC'),
                    ('is_potential_customer', '=', False),
                    ('billing_start_date', '>=', str(date_start)),
                    ('billing_start_date', '<=', str(date_end)),

                ])
                existing_corporate_partners = self.env['res.partner'].search([
                    ('subscriber_id', 'like', 'MC'),
                    ('is_potential_customer', '=', False),
                    ('billing_start_date', '<', str(date_start)),

                ])

            for partner in new_corporate_partners:
                invoices=self.env['account.invoice'].search([('partner_id', '=', partner.id),
                                                             ('state','not in',['draft','cancel']),
                                                             ('date_due', '>=', str(date_start)),
                                                             ('date_due', '<=', str(date_end))
                                                             ])
                total_recieveable = 0.0
                total_paid = 0.0
                total_due = 0.0
                for invoice in invoices:
                    otc = 0.0
                    mrc = 0.0
                    if invoice.corporate_otc_amount > 0.0:
                        otc = invoice.corporate_otc_amount
                        mrc = invoice.amount_total_signed - invoice.corporate_otc_amount
                    else:
                        if invoice.state == 'paid':
                            mrc = invoice.amount_total_signed
                        if invoice.state == 'open':
                            mrc = invoice.residual_signed

                    if invoice.state == 'paid':
                        total_recieveable = total_recieveable + invoice.amount_total_signed
                        total_paid = total_paid + invoice.amount_total_signed
                        docs_new.append({
                            'date_maturity': invoice.date_due,
                            'customer_name': partner.name,
                            'mrc': "{0:.2f}".format(mrc),
                            'otc': "{0:.2f}".format(otc),
                            'total_recieveable': "{0:.2f}".format(invoice.amount_total_signed),
                            'total_paid': "{0:.2f}".format(invoice.amount_total_signed),
                            'total_due': "{0:.2f}".format(0.0)
                        })

                    elif invoice.state == 'open':
                        total_recieveable = total_recieveable + invoice.residual_signed
                        total_due = total_due + invoice.residual_signed
                        docs_new.append({
                            'date_maturity': invoice.date_due,
                            'customer_name': partner.name,
                            'mrc': "{0:.2f}".format(mrc),
                            'otc': "{0:.2f}".format(otc),
                            'total_recieveable': "{0:.2f}".format(invoice.amount_total_signed),
                            'total_paid': "{0:.2f}".format(0.0),
                            'total_due': "{0:.2f}".format(invoice.residual_signed)
                        })


                new_total_recieveable = new_total_recieveable + total_recieveable
                new_total_paid = new_total_paid + total_paid
                new_total_due = new_total_due + total_due

            docs_new.append({
                'date_maturity': '',
                'customer_name': '',
                'mrc': '',
                'otc': 'Sub Total',
                'total_recieveable': "{0:.2f}".format(new_total_recieveable),
                'total_paid': "{0:.2f}".format(new_total_paid),
                'total_due': "{0:.2f}".format(new_total_due)
            })

            existing_total_recieveable = 0.0
            existing_total_paid = 0.0
            existing_total_due = 0.0
            docs_old = []
            for partner in existing_corporate_partners:


                invoices = self.env['account.invoice'].search([
                    ('partner_id', '=', partner.id),
                    ('state', 'not in', ['draft', 'cancel']),
                    ('date_due', '>=', str(date_start)),
                    ('date_due', '<=', str(date_end))
                ])
                total_recieveable = 0.0
                total_paid = 0.0
                total_due = 0.0
                for invoice in invoices:
                    otc = 0.0
                    mrc = 0.0
                    if invoice.corporate_otc_amount > 0.0:
                        otc = invoice.corporate_otc_amount
                        mrc = invoice.amount_total_signed - invoice.corporate_otc_amount
                    else:
                        if invoice.state == 'paid':
                            mrc = invoice.amount_total_signed
                        if invoice.state == 'open':
                            mrc = invoice.residual_signed

                    if invoice.state == 'paid':
                        total_recieveable = total_recieveable + invoice.amount_total_signed
                        total_paid = total_paid + invoice.amount_total_signed
                        docs_old.append({
                            'date_maturity': invoice.date_due,
                            'customer_name': partner.name,
                            'mrc': "{0:.2f}".format(mrc),
                            'otc': "{0:.2f}".format(otc),
                            'total_recieveable': "{0:.2f}".format(invoice.amount_total_signed),
                            'total_paid': "{0:.2f}".format(invoice.amount_total_signed),
                            'total_due': "{0:.2f}".format(0.0)
                        })

                    elif invoice.state == 'open':
                        total_recieveable = total_recieveable + invoice.residual_signed
                        total_due = total_due + invoice.residual_signed
                        docs_old.append({
                            'date_maturity': invoice.date_due,
                            'customer_name': partner.name,
                            'mrc': "{0:.2f}".format(mrc),
                            'otc': "{0:.2f}".format(otc),
                            'total_recieveable': "{0:.2f}".format(invoice.amount_total_signed),
                            'total_paid': "{0:.2f}".format(0.0),
                            'total_due': "{0:.2f}".format(invoice.residual_signed)
                        })

                    # docs_old.append({
                    #     'date_maturity': invoice.date_due,
                    #     'customer_name': partner.name,
                    #     'mrc': '',
                    #     'otc': '',
                    #     'total_recieveable': "{0:.2f}".format(total_recieveable),
                    #     'total_paid': "{0:.2f}".format(total_paid),
                    #     'total_due': "{0:.2f}".format(total_due)
                    # })
                existing_total_recieveable = existing_total_recieveable + total_recieveable
                existing_total_paid = existing_total_paid + total_paid
                existing_total_due = existing_total_due + total_due

            docs_old.append({
                'date_maturity': '',
                'customer_name': '',
                'mrc': '',
                'otc': 'Sub Total',
                'total_recieveable': "{0:.2f}".format(existing_total_recieveable),
                'total_paid': "{0:.2f}".format(existing_total_paid),
                'total_due': "{0:.2f}".format(existing_total_due)
            })
            # docs_old.append({
            #     'date_maturity': '',
            #     'customer_name': '',
            #     'mrc': '',
            #     'otc': 'Total',
            #     'total_recieveable': "{0:.2f}".format(new_total_recieveable + existing_total_recieveable),
            #     'total_paid': "{0:.2f}".format(new_total_paid + existing_total_paid),
            #     'total_due': "{0:.2f}".format(new_total_due + existing_total_due)
            # })
            print('new******************',new_total_recieveable,new_total_paid,new_total_due)
            print('existing******************', existing_total_recieveable, existing_total_paid, existing_total_due)
            print('grand******************', new_total_recieveable + existing_total_recieveable, new_total_paid + existing_total_paid, new_total_due + existing_total_due)
            return {
                'doc_ids': 2323223,
                'doc_model': 'mime_sales_report.new_customer_transient',
                'date_start': start_date_obj.strftime('%d, %b %Y'),
                'date_end': end_date_obj.strftime('%d, %b %Y'),
                # 'date_start': self.custom_strftime('%B {S}, %Y', start_date_obj),
                # 'date_end': self.custom_strftime('%B {S}, %Y', end_date_obj),
                'lead_type': data['form']['lead_type'],
                'docs_new': docs_new,
                'docs_old': docs_old,
                'grand_recieveable': "{0:.2f}".format(new_total_recieveable + existing_total_recieveable),
                'grand_paid': "{0:.2f}".format(new_total_paid + existing_total_paid),
                'grand_due': "{0:.2f}".format(new_total_due + existing_total_due)
            }

    def custom_strftime(self,format, t):
        return t.strftime(format).replace('{S}', str(t.day) + self.suffix(t.day))

    def suffix(d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')





