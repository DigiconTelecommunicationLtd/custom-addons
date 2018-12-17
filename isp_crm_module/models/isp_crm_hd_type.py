# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskType(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_type"
    _description = "Helpdesk Type"
    _order = "create_date desc, id"

    name = fields.Char('Name', translate=True)
    color = fields.Integer()