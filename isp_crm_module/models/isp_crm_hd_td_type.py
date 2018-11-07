# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskTDType(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_td_type"
    _description = "Helpdesk TD Type"

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer()