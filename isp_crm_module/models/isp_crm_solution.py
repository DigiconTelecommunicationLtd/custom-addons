# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Solution(models.Model):
    """
    Model for different type of Solutions.
    """
    _name = "isp_crm_module.solution"
    _description = "Type of Solutions of ISP-CRM Service Request Solutions."
    _rec_name = 'name'
    _order = "name, id"

    name = fields.Char('Solution', required=True, translate=True)
    remarks = fields.Text('Remarks')
    is_done = fields.Boolean('Done', default=False)
