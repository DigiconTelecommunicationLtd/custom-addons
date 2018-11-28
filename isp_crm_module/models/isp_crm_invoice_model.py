# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

DEFAULT_MONTH_DAYS = 30
DEFAULT_NEXT_MONTH_DAYS = 31
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class Customer(models.Model):
    """Inherits res.partner and adds Customer info in partner form"""
    _inherit = 'account.invoice'

    payment_service_id = fields.Many2one('isp_crm_module.selfcare_payment_service', string='Payment Service Type', default=1)