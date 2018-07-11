# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Solution(models.Model):
    """
    Model for different type of Solutions.
    """
    _name = "isp_helpdesk.solution"
    _description = "Type of Solutions of ISP HelpDesk."
    _rec_name = 'name'
    _order = "name, id"

    name = fields.Char('Solution', required=True, translate=True)