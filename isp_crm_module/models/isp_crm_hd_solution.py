# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskSolution(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_solution"
    _description = "Helpdesk Solution"
    _order = "create_date desc, id"

    name = fields.Char('Solution', required=True, translate=True)
    color = fields.Integer()