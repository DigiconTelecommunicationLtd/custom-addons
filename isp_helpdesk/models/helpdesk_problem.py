# -*- coding: utf-8 -*-

from odoo import api, fields, models

class Problem(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_helpdesk.problem"
    _description = "Type of Problems of ISP HelpDesk."
    _rec_name = 'name'
    _order = "name, id"

    name = fields.Char('Problem', required=True, translate=True)