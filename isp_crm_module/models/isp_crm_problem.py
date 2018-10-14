# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Problem(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.problem"
    _description = "Type of Problems of Service Request."
    _rec_name = 'name'
    _order = "name, id"

    name = fields.Char('Problem', required=True, translate=True)
    shortcode = fields.Char('Short Code', required=True, translate=True)