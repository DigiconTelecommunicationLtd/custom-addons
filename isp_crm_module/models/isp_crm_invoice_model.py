# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
import datetime
from dateutil.relativedelta import relativedelta
import calendar
from odoo.exceptions import Warning, UserError

DEFAULT_MONTH_DAYS = 30
DEFAULT_NEXT_MONTH_DAYS = 31
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_PACKAGES_CATEGORY_NAME = 'Packages'

class ISPCRMInvoice(models.Model):

    """Inherits res.partner and adds Customer info in partner form"""
    PAYMENT_SERVICE_TYPE_ID = 8


    _inherit = 'account.invoice'

    payment_service_id = fields.Many2one('isp_crm_module.selfcare_payment_service', string='Payment Service Type', default=1)
    is_deferred = fields.Boolean("Is Deferred", default=False)
    customer_po_no = fields.Char(compute='_get_customer_po_no', string='Customer PO No')
    billing_due_date = fields.Char(compute='_get_billing_due_date', string='Due Date', default="", readonly=False)
    vat = fields.Char(compute='_get_vat', string='VAT')

    amount_without_vat = fields.Monetary(string='Amount Without VAT', store=True, readonly=True, compute='_compute_amount',
                                         track_visibility='onchange')
    amount_vat = fields.Monetary(string='VAT', store=True, readonly=True, compute='_compute_amount')
    get_sales_order_origin = fields.Many2one('sale.order', string='Origin SO', compute='_get_origin')
    corporate_soho_first_month_date_start = fields.Date(string="Start Date", required=False, inverse='compute_partial_amount')
    corporate_soho_first_month_date_end = fields.Date(string="End Date", required=False, inverse='compute_partial_amount')
    corporate_otc_amount = fields.Monetary(string='OTC Amount', store=True, readonly=True)
    toal_amount_otc_mrc = fields.Monetary(string='Total', readonly=True)
    toal_amount_mrc = fields.Monetary(string='MRC Amount', readonly=True)
    lead_type = fields.Char(compute='_get_lead_type', string='Lead Type')

    def _get_origin(self):
        sales_order_obj = self.env['sale.order']
        for invoice in self:
            sales_order = sales_order_obj.search([('name', '=', invoice.origin)], limit=1)
            invoice.update({
                'get_sales_order_origin': sales_order,
            })

    @api.depends('partner_id')
    def _get_lead_type(self):
        """
        Compute type of customer .(Corporate or Retail)
        :return:
        """

        for invoice in self:
            lead = invoice.env['crm.lead'].search([('partner_id', '=', invoice.partner_id.id)], order='create_date desc',
                                                limit=1)
            lead_type = lead.lead_type

            invoice.update({
                'lead_type': lead_type,
            })

    def compute_partial_amount(self):
        # print('this wont go to production now.')
        for invoice in self:
            # Compute partial bill amount
            get_customer = invoice.env['res.partner'].search([('id', '=', invoice.partner_id.id)], limit=1)
            if get_customer:
                opportunities = invoice.env['crm.lead'].search([('partner_id', '=', get_customer.id)])
                for opportunity in opportunities:
                    # check if lead type is corporate or soho or sme
                    if opportunity.lead_type != "retail":
                        if invoice.corporate_soho_first_month_date_start and invoice.corporate_soho_first_month_date_end:

                            # Convert the given date to specific format
                            formated_date = datetime.datetime.strptime(str(invoice.corporate_soho_first_month_date_start),
                                                                         "%Y-%m-%d").strftime(
                                "%Y-%m-%d")
                            # Convert the formated_date to date type from string type.
                            formated_date = datetime.datetime.strptime(formated_date, "%Y-%m-%d")

                            # Get the first day of the month in order to calculate total days of the month.
                            corporate_soho_first_month_date_start = formated_date.replace(
                                day=1)
                            corporate_soho_first_month_date_start = str(corporate_soho_first_month_date_start).split(" ")[0]

                            # Get the last day of the month.
                            corporate_soho_first_month_date_end = datetime.date(formated_date.year,
                                                                                formated_date.month + 1,
                                                                                1) - relativedelta(
                                days=1)

                            bill_start_date = datetime.datetime.strptime(str(corporate_soho_first_month_date_start),
                                                                         "%Y-%m-%d").strftime(
                                "%Y-%m-%d %H-%M")
                            bill_start_date = datetime.datetime.strptime(bill_start_date, "%Y-%m-%d %H-%M")

                            bill_end_date = datetime.datetime.strptime(str(corporate_soho_first_month_date_end),
                                                                       "%Y-%m-%d").strftime(
                                "%Y-%m-%d %H-%M")
                            bill_end_date = datetime.datetime.strptime(bill_end_date, "%Y-%m-%d %H-%M")

                            difference = bill_end_date - bill_start_date
                            # total_days_of_the_month = float(difference.days+1)
                            total_days_of_the_month = 30.0

                            bill_start_date = datetime.datetime.strptime(invoice.corporate_soho_first_month_date_start,
                                                                         "%Y-%m-%d").strftime(
                                "%Y-%m-%d %H-%M")
                            bill_start_date = datetime.datetime.strptime(bill_start_date, "%Y-%m-%d %H-%M")

                            bill_end_date = datetime.datetime.strptime(invoice.corporate_soho_first_month_date_end,
                                                                       "%Y-%m-%d").strftime(
                                "%Y-%m-%d %H-%M")
                            bill_end_date = datetime.datetime.strptime(bill_end_date, "%Y-%m-%d %H-%M")

                            difference = bill_end_date - bill_start_date
                            difference = float(difference.days+1)

                            for line in invoice.invoice_line_ids:
                                if line.product_id.categ_id.name == DEFAULT_PACKAGES_CATEGORY_NAME:
                                    price_subtotal = line.quantity * line.price_unit
                                    discount = (price_subtotal * line.discount) / 100
                                    price_subtotal = price_subtotal - discount
                                    price_subtotal = (price_subtotal * difference) / total_days_of_the_month
                                    line.write({
                                        'price_subtotal': price_subtotal,
                                    })
                        else:
                            print("User has not selected service start date and end date")
                            corporate_soho_first_month_date_start = datetime.date.today()
                            # corporate_soho_first_month_date_start = datetime.date.today().replace(day=1) + relativedelta(months=1)
                            corporate_soho_first_month_date_end = datetime.date(datetime.date.today().year,
                                                                                datetime.date.today().month + 1, 1) - relativedelta(
                                days=1)
                            invoice.update({
                                'corporate_soho_first_month_date_start': corporate_soho_first_month_date_start,
                                'corporate_soho_first_month_date_end': corporate_soho_first_month_date_end,
                            })

                            bill_start_date = datetime.datetime.strptime(invoice.corporate_soho_first_month_date_start,
                                                                         "%Y-%m-%d").strftime(
                                "%Y-%m-%d %H-%M")
                            bill_start_date = datetime.datetime.strptime(bill_start_date, "%Y-%m-%d %H-%M")

                            bill_end_date = datetime.datetime.strptime(invoice.corporate_soho_first_month_date_end,
                                                                       "%Y-%m-%d").strftime(
                                "%Y-%m-%d %H-%M")
                            bill_end_date = datetime.datetime.strptime(bill_end_date, "%Y-%m-%d %H-%M")

                            difference = bill_end_date - bill_start_date
                            difference = float(difference.days)

                            for line in invoice.invoice_line_ids:
                                price_subtotal = line.quantity * line.price_unit
                                discount = (price_subtotal * line.discount) / 100
                                price_subtotal = price_subtotal - discount
                                line.write({
                                    'price_subtotal': price_subtotal,
                                })
                        sales_order_obj = invoice.env['sale.order']
                        sales_order = sales_order_obj.search([('name', '=', invoice.origin)], limit=1)
                        round_curr = invoice.currency_id.round
                        invoice.amount_untaxed = sum(line.price_subtotal for line in invoice.invoice_line_ids)
                        invoice.amount_tax = sum(round_curr(line.amount_total) for line in invoice.tax_line_ids)
                        total = invoice.amount_untaxed + invoice.amount_tax
                        vat = total - ((total * 100.0) / 105.0)
                        total_without_vat = (total * 100.0) / 105.0
                        if sales_order:
                            invoice.write({
                                'corporate_otc_amount': float(sales_order.price_total),
                                'toal_amount_otc_mrc': vat + total_without_vat + float(sales_order.price_total),
                                'toal_amount_mrc': vat + total_without_vat
                            })
                        else:
                            invoice.write({
                                'toal_amount_otc_mrc': vat + total_without_vat,
                                'toal_amount_mrc': vat + total_without_vat
                            })
                    else:
                        print("Customer type is not corporate or soho")
                        round_curr = invoice.currency_id.round
                        invoice.amount_untaxed = sum(line.price_subtotal for line in invoice.invoice_line_ids)
                        invoice.amount_tax = sum(round_curr(line.amount_total) for line in invoice.tax_line_ids)
                        total = invoice.amount_untaxed + invoice.amount_tax
                        vat = total - ((total * 100.0) / 105.0)
                        total_without_vat = (total * 100.0) / 105.0
                        invoice.write({
                            'toal_amount_otc_mrc': vat + total_without_vat,
                            'toal_amount_mrc': vat + total_without_vat
                        })
                        print("Computed total for retail")

    # def _compute_partial_amount(self):
    #     self.compute_partial_amount()

    # def compute_otc_amount(self):
    #     # print("compute otc amount for invoice")
    #     # compute otc amount for invoice
    #     for invoice in self:
    #         if invoice.lead_type != "retail":
    #             sales_order_obj = invoice.env['sale.order']
    #             sales_order = sales_order_obj.search([('name', '=', invoice.origin)], limit=1)
    #             if sales_order:
    #                 invoice.update({
    #                     'corporate_otc_amount' : float(sales_order.price_total)
    #                 })

    @api.multi
    def _compute_amount(self):
        self.compute_partial_amount()
        for invoice in self:

            round_curr = invoice.currency_id.round
            invoice.amount_untaxed = sum(line.price_subtotal for line in invoice.invoice_line_ids)
            invoice.amount_tax = sum(round_curr(line.amount_total) for line in invoice.tax_line_ids)
            total = invoice.amount_untaxed + invoice.amount_tax
            vat = total - ((total * 100.0) / 105.0)
            total_without_vat = (total * 100.0) / 105.0
            invoice.update({
                'amount_without_vat': total_without_vat,
                'amount_vat': vat,
            })
        super(ISPCRMInvoice, self)._compute_amount()
        # self.compute_otc_amount()


    @api.multi
    def action_invoice_paid(self):
        # Updating the package change info
        if self.payment_service_id.id == self.PAYMENT_SERVICE_TYPE_ID:
            last_package_change_obj = self.env['isp_crm_module.change_package'].search(
                    [('customer_id', '=', self.partner_id.id)], order='create_date desc', limit=1)
            if last_package_change_obj:
                last_package_change_obj.update({
                    'state': 'invoice_paid',
                    'is_invoice_paid': True
                })
        super(ISPCRMInvoice, self).action_invoice_paid()
        return True

    @api.multi
    def action_invoice_open(self):

        # If service start date and end date is not given then give a warning.
        if self.lead_type != "retail":
            if self.corporate_soho_first_month_date_start and self.corporate_soho_first_month_date_end:
                pass
            else:
                raise UserError('Please select service start date and end date')

        # Updating the sales order of the customer
        package_line = ''
        created_product_line_list = []
        customer = self.partner_id
        invoice_lines = self.invoice_line_ids
        customer_product_line_obj = self.env['isp_crm_module.customer_product_line']
        for invoice_line in invoice_lines:
            if invoice_line.product_id.categ_id.name == DEFAULT_PACKAGES_CATEGORY_NAME:
                package_line = invoice_line
            created_product_line = customer_product_line_obj.create({
                'customer_id': customer.id,
                'name': invoice_line.name,
                'product_id': invoice_line.product_id.id,
                'product_updatable': False,
                'product_uom_qty': invoice_line.quantity,
                'product_uom': invoice_line.product_id.uom_id.id,
                'price_unit': invoice_line.price_unit,
                'price_subtotal': invoice_line.price_subtotal,
                'price_total': self.amount_total,
            })
            created_product_line_list.append(created_product_line.id)
        if package_line != '':
            customer.update({
                'invoice_product_id': package_line.product_id.id,
                'invoice_product_price': package_line.price_subtotal,
                'invoice_product_original_price': package_line.product_id.list_price,
                'invoice_sales_order_name': self.origin,
                'product_line': [(6, None, created_product_line_list)]
            })

        super(ISPCRMInvoice, self).action_invoice_open()

        if self.lead_type != "retail":
            self.update({
                'residual': self.amount_total + self.corporate_otc_amount,
                'amount_total_signed': self.amount_total + self.corporate_otc_amount,
            })

        return True

    def _get_customer_po_no(self):
        """
        Get the customer PO No from sale.order
        :return:
        """

        for invoice in self:
            order = invoice.env['sale.order'].search([('name', '=', invoice.origin)], limit=1)
            if order:
                if order.customer_po_no:
                    invoice.update({
                        'customer_po_no': str(order.customer_po_no),
                    })
                else:
                    invoice.update({
                        'customer_po_no': "",
                    })
            else:
                invoice.update({
                    'customer_po_no': "",
                })

    def add_months(self, sourcedate, months):
        getdate = datetime.datetime.strptime(sourcedate, "%Y-%m-%d")
        month = getdate.month - 1 + months
        year = getdate.year + month // 12
        month = month % 12 + 1
        day = min(getdate.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)

    def _get_billing_due_date(self):
        """
        Compute due date of billing of invoice
        :return:
        """
        for invoice in self:
            get_customer = invoice.env['res.partner'].search([('id', '=', invoice.partner_id.id)], limit=1)
            if get_customer:
                opportunities = invoice.env['crm.lead'].search([('partner_id', '=', get_customer.id)])
                for opportunity in opportunities:
                    # check if lead type is corporate or soho or sme
                    if opportunity.lead_type != "retail":
                        if invoice.date_invoice:
                            due_date = invoice.date_invoice
                            due_date = invoice.add_months(due_date, 1)
                            invoice.update({
                                'billing_due_date': str(due_date),
                            })
                        else:
                            invoice.update({
                                'billing_due_date': "",
                            })
                    else:
                        if invoice.date_due:
                            due_date = invoice.date_due
                            invoice.update({
                                'billing_due_date' : str(due_date),
                            })
                        else:
                            invoice.update({
                                'billing_due_date': "",
                            })

    def _get_vat(self):
        """
        Compute vat of invoice.
        :return:
        """
        for invoice in self:
            if invoice.amount_untaxed:
                invoice_vat = float(invoice.amount_untaxed) * 0.05
                invoice.update({
                    'vat': str(invoice_vat),
                })
            else:
                invoice_vat = 0.0
                invoice.update({
                    'vat': str(invoice_vat),
                })

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        self.compute_partial_amount()
        super(ISPCRMInvoice, self)._onchange_payment_term_date_invoice()