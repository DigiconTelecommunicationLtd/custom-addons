# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskTicketComplexity(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_ticket_complexity"
    _description = "Helpdesk Ticket Complexity"
    _order = "create_date desc, id"

    name = fields.Char('Name', required=True, translate=True)
    time_limit = fields.Char('Time Limit', required=True, translate=True)
    color = fields.Integer()
