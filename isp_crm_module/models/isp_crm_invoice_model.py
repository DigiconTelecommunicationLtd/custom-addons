# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
import datetime
import calendar

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
    billing_due_date = fields.Char(compute='_get_billing_due_date', string='Due Date')
    vat = fields.Char(compute='_get_vat', string='VAT')

    amount_without_vat = fields.Monetary(string='Amount Without VAT', store=True, readonly=True, compute='_compute_amount',
                                         track_visibility='onchange')
    amount_vat = fields.Monetary(string='VAT', store=True, readonly=True, compute='_compute_amount')

    @api.multi
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        total = self.amount_untaxed + self.amount_tax
        vat = (total * 5.0) / 100.0
        total_without_vat = (total * 100.0) / 105.0
        self.update({
            'amount_without_vat': total_without_vat,
            'amount_vat': vat,
        })
        super(ISPCRMInvoice, self)._compute_amount()

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
                    if opportunity.lead_type == "corporate":
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


