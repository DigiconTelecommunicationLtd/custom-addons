# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskTicketHistory(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_ticket_history"
    _description = "Helpdesk Ticket History"

    type = fields.Char('Type', required=True, translate=True)
    assigned = fields.Char('Assigned', required=True, translate=True)
    ticket_id = fields.Char('Ticket ID', required=True, translate=True)
    color = fields.Integer()