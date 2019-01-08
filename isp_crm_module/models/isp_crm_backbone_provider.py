# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class BackboneProvider(models.Model):
    _name = 'isp_crm_module.backbone_provider'
    _description = "ISP CRM Backbone Provider"
    _rec_name = 'name'
    _order = "create_date desc, name, id"

    name = fields.Char(string="Backbone Provider", required=False, default='MIME')