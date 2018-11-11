# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

class Team(models.Model):
    _name = 'isp_crm_module.mail'
    _description = "ISP CRM Mail Module"
    _rec_name = 'name'
    _order = "name, id"


    name = fields.Char('Mail Name', translate=True)
    body_html = fields.Text('Mail Body')


