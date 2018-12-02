# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskTDSolution(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_td_solution"
    _description = "Helpdesk TD Solution"
    _order = "create_date desc, id"

    name = fields.Char('Solution', required=True, translate=True)
    color = fields.Integer()