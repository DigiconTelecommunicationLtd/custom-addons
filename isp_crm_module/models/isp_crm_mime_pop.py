# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MimePop(models.Model):
    _name = 'isp_crm_module.mime_pop'
    _description = "ISP CRM Mime Pop"
    _rec_name = 'name'
    _order = "create_date desc, name, id"

    name = fields.Char(string="Pop Name", required=False, default='')