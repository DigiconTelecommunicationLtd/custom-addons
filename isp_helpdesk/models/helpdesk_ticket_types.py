# -*- coding: utf-8 -*-

from odoo import api, fields, models

class TicketType(models.Model):
    """
    Model for different type of tickets.
    """
    _name = "isp_helpdesk.ticket_type"
    _description = "Stage of ISP HelpDesk."
    _rec_name = 'name'
    _order = "name, id"

    name = fields.Char('Ticket Types', required=True, translate=True)