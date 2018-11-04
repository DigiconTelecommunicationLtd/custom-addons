# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskProblems(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_problem"
    _description = "Helpdesk Type"

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer()