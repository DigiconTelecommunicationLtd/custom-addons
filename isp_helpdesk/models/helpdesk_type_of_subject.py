# -*- coding: utf-8 -*-

from odoo import api, fields, models

class TypeOfSubject(models.Model):
    """
    Model for different type of tickets.
    """
    _name = "isp_helpdesk.type_of_subject"
    _description = "Type of Subject of ISP HelpDesk."
    _rec_name = 'name'
    _order = "name, id"

    name = fields.Char('Type of Subject', required=True, translate=True)