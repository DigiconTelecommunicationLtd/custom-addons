# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskTicketHistory(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_ticket_history"
    _description = "Helpdesk Ticket History"

    ticket_id = fields.Many2one('isp_crm_module.helpdesk', string='Ticket', ondelete='set null',
                                help='Ticket of the problem to solve.')
    type = fields.Many2one('isp_crm_module.helpdesk_type', string='Type', ondelete='set null',
                           help='Ticket Type.')
    assigned_to = fields.Many2one('hr.employee', string='Team', ondelete='set null',
                                  help='Person assigned to complete the task.')
    color = fields.Integer()