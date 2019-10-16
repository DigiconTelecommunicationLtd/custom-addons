# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

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
    date_maturity = fields.Date()
    customer_name = fields.Char()
    subscriber_id = fields.Char()
    label = fields.Char()
    lead_type = fields.Char()
    debit = fields.Float()
    credit = fields.Float()
    account_code = fields.Char()
    account_name = fields.Char()
    billing_start_date = fields.Date()
    current_package_end_date = fields.Date()
    billing_type  = fields.Char(compute='_calculate_type')
    move_id = fields.Integer()
    mrc = fields.Float(compute='_calculate_billing_type')
    otc = fields.Float(compute='_calculate_billing_type')

    # total_recieveable = fields.Float(string='Total Receivable')
    # total_paid = fields.Float(string='Total Paid')
    # total_due = fields.Float(string='Total Due')



    @api.one
    def _calculate_billing_type(self):
        if 'retail' in self.lead_type:
            if 'Retail Installation Fee' in self.label:
                self.otc = self.credit
            else:
                self.mrc = self.credit

            self.total_recieveable = self.credit
            self.total_paid  = self.credit
            self.total_due = 0

    @api.one
    def _calculate_type(self):
        if 'Retail Installation Fee' in self.label:
            self.billing_type = 'OTC'
        else:
            self.billing_type = 'MRC'


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'mime_sales_report_new_customer_transient')
        self._cr.execute("""
                   CREATE OR REPLACE VIEW mime_sales_report_new_customer_transient AS (
                       SELECT
                        row_number() OVER () as id,
                        row_number() OVER () as create_uid,
                        row_number() OVER () as write_uid, 
                        res_partner.id as res_id,
                        date_maturity,
                        res_partner.name as customer_name,
                        res_partner.subscriber_id as subscriber_id,
                        account_move_line.name as label,
                        lead_type,
                        billing_start_date,
                        current_package_end_date,
                        current_package_start_date as write_date,
                        next_package_start_date as create_date,
                        debit,
                        credit,
                        account_account.code as account_code,
                        account_account.name as account_name,
                        move_id
                        FROM res_partner
                        RIGHT OUTER JOIN crm_lead on res_partner.id=crm_lead.partner_id
                        RIGHT OUTER JOIN account_move_line on res_partner.id=account_move_line.partner_id
                        RIGHT OUTER JOIN account_account on account_move_line.account_id=account_account.id
                        where
                        is_potential_customer = false
                        ORDER BY res_partner.name,date_maturity desc
                   )""")

    @api.multi
    def get_filtered_data(self,lead_type=None,subtype=None,to_date=None,from_date=None):
        sql ="""
                   CREATE OR REPLACE VIEW mime_sales_report_new_customer_transient AS (
                       SELECT
                        row_number() OVER () as id,
                        res_partner.id as res_id,
                        date_maturity,
                        res_partner.name as customer_name,
                        account_move_line.name as label,
                        lead_type,
                        billing_start_date,
                        current_package_end_date,
                        debit,
                        credit,
                        account_account.code as account_code,
                        account_account.name as account_name,
                        move_id
                        FROM res_partner
                        RIGHT OUTER JOIN crm_lead on res_partner.id=crm_lead.partner_id
                        RIGHT OUTER JOIN account_move_line on res_partner.id=account_move_line.partner_id
                        RIGHT OUTER JOIN account_account on account_move_line.account_id=account_account.id
                        where
                        is_potential_customer = false and
                        lead_type like '%s'
                        ORDER BY res_partner.name,date_maturity desc
                   )"""%(lead_type)
        res_data=self.env.cr.execute(sql).fetchall()
        return res_data

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
        print("asdad",data)
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        lead_type_report = ('lead_type', '=', data['form']['lead_type'])
        print('********************',data['form']['lead_type'])
        if data['form']['lead_type'] == 'retail':

            ######################### NEW CUSTOMERS ######################################
            docs_new = []
            domain_new = []
            domain_new.append(lead_type_report)
            domain_data = ('credit', '!=', 0)
            domain_new.append(domain_data)

            #condition for new customer
            domain_data=('billing_start_date', '>=', str(date_start))
            domain_new.append(domain_data)
            # domain_data = ('current_package_end_date', '<=', str(date_end))
            # domain_new.append(domain_data)
            domain_data = ('date_maturity', '>=', str(date_start))
            domain_new.append(domain_data)
            domain_data = ('date_maturity', '<=', str(date_end))
            domain_new.append(domain_data)

            #total for new customers
            new_total_recieveable = 0.0
            new_total_paid = 0.0
            new_total_due = 0.0
            filtered_customers_new = self.env['mime_sales_report.new_customer_transient'].search(domain_new)
            for customer in filtered_customers_new:
                new_total_recieveable = new_total_recieveable + (customer.mrc+customer.otc)
                new_total_paid = new_total_paid + (customer.mrc+customer.otc)
                new_total_due = new_total_due + 0.0

                if data['form']['lead_type'] == 'retail':
                    docs_new.append({
                        'date_maturity': customer.date_maturity,
                        'customer_name': customer.customer_name,
                        'mrc': "{0:.2f}".format(customer.mrc),
                        'otc': "{0:.2f}".format(customer.otc),
                        'total_recieveable': "{0:.2f}".format(customer.mrc+customer.otc),
                        'total_paid': "{0:.2f}".format(customer.mrc+customer.otc),
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

            ######################### OLD CUSTOMERS ######################################
            docs_old = []
            domain_old = []
            domain_old.append(lead_type_report)
            domain_data = ('credit', '!=', 0)
            old_total_recieveable=0.0
            old_total_paid=0.0
            old_total_due=0.0
            domain_old.append(domain_data)

            # condition for Existing customer
            domain_data = ('billing_start_date', '<', str(date_start))
            domain_old.append(domain_data)
            domain_data = ('current_package_end_date', '<=', str(date_end))
            domain_old.append(domain_data)
            domain_data = ('date_maturity', '>=', str(date_start))
            domain_old.append(domain_data)
            domain_data = ('date_maturity', '<=', str(date_end))
            domain_old.append(domain_data)

            filtered_customers_old = self.env['mime_sales_report.new_customer_transient'].search(domain_old)
            #for existing customers
            for customer in filtered_customers_old:
                old_total_recieveable = old_total_recieveable + (customer.mrc+customer.otc)
                old_total_paid = old_total_paid + (customer.mrc+customer.otc)
                old_total_due = old_total_due + 0.0

                if data['form']['lead_type'] == 'retail':
                    docs_old.append({
                        'date_maturity': customer.date_maturity,
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
                'date_start': date_start,
                'date_end': date_end,
                'lead_type':lead_type_display,
                'docs_new': docs_new,
                'docs_old':docs_old,
                'grand_recieveable':grand_recieveable,
                'grand_paid':grand_paid,
                'grand_due':grand_due
            }

        else:
            #get all non retail customers

            ########################### NEW CUSTOMERS ###############################
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
                    ('billing_start_date', '<=', str(date_start)),

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
                    ('billing_start_date', '<=', str(date_start)),

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
                    if invoice.state == 'paid':
                        total_recieveable = total_recieveable + invoice.amount_total_signed
                        total_paid = total_paid + invoice.amount_total_signed
                        docs_new.append({
                            'date_maturity': invoice.date_due,
                            'customer_name': partner.name,
                            'mrc': '',
                            'otc': '',
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
                            'mrc': '',
                            'otc': '',
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
                print(partner.subscriber_id)
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
                    if invoice.state == 'paid':
                        total_recieveable = total_recieveable + invoice.amount_total_signed
                        total_paid = total_paid + invoice.amount_total_signed
                        docs_old.append({
                            'date_maturity': invoice.date_due,
                            'customer_name': partner.name,
                            'mrc': '',
                            'otc': '',
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
                            'mrc': '',
                            'otc': '',
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
                'date_start': date_start,
                'date_end': date_end,
                'lead_type': data['form']['lead_type'],
                'docs_new': docs_new,
                'docs_old': docs_old,
                'grand_recieveable': new_total_recieveable + existing_total_recieveable,
                'grand_paid': new_total_paid + existing_total_paid,
                'grand_due': new_total_due + existing_total_due
            }






