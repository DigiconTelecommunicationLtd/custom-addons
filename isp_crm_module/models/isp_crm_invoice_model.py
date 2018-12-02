# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

DEFAULT_MONTH_DAYS = 30
DEFAULT_NEXT_MONTH_DAYS = 31
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class ISPCRMInvoice(models.Model):

    """Inherits res.partner and adds Customer info in partner form"""
    PAYMENT_SERVICE_TYPE_ID = 8


    _inherit = 'account.invoice'

    payment_service_id = fields.Many2one('isp_crm_module.selfcare_payment_service', string='Payment Service Type', default=1)

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