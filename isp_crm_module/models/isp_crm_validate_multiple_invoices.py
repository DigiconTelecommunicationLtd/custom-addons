# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class AccountInvoiceValidate(models.TransientModel):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _name = "account.invoice.validate"
    _description = "Validate the selected invoices"

    @api.multi
    def action_invoice_validate(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            if record.state != 'draft':
                raise UserError(_("Selected invoice(s) cannot be validated as they are not in 'Draft' state."))
            record.action_invoice_open()
        return {'type': 'ir.actions.act_window_close'}