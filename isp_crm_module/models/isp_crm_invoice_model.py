# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
import datetime
import calendar

DEFAULT_MONTH_DAYS = 30
DEFAULT_NEXT_MONTH_DAYS = 31
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class ISPCRMInvoice(models.Model):

    """Inherits res.partner and adds Customer info in partner form"""
    PAYMENT_SERVICE_TYPE_ID = 8


    _inherit = 'account.invoice'

    payment_service_id = fields.Many2one('isp_crm_module.selfcare_payment_service', string='Payment Service Type', default=1)
    is_deferred = fields.Boolean("Is Deferred", default=False)
    customer_po_no = fields.Char(compute='_get_customer_po_no', string='Customer PO No')
    billing_due_date = fields.Char(compute='_get_billing_due_date', string='Due Date')
    vat = fields.Char(compute='_get_vat', string='VAT')

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
                        'customer_po_no': str(order.file_name),
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


