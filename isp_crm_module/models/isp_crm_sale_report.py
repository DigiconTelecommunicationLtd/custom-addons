# -*- coding: utf-8 -*-



from ast import literal_eval
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import Warning, UserError
import re
import odoo.addons.decimal_precision as dp
from odoo import tools

class ISPCRMSaleReport(models.Model):
    """Inherits res.partner and adds Customer info in partner form"""
    _inherit = 'sale.report'

    customer_type = fields.Selection(related='partner_id.opportunity_ids.lead_type', string='Customer Type')
