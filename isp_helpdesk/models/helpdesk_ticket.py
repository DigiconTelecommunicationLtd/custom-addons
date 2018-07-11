# -*- coding: utf-8 -*-

from odoo import api, fields, models

AVAILABLE_PRIORITIES = [
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
]
AVAILABLE_RATINGS = [
    ('-2', 'Worst'),
    ('-1', 'Bad'),
    ('0', 'Neutral'),
    ('1', 'Good'),
    ('2', 'Excellent'),
]


class Ticket(models.Model):
    """
    Model for different type of tickets.
    """
    _name = "isp_helpdesk.ticket"
    _description = "Type of Subject of ISP HelpDesk."
    _rec_name = 'name'
    _order = "priority, name, id"



    # TODO-Arif: give a name field in this place
    name = fields.Many2one('isp_helpdesk.problem', string="Problem", required=True, translate=True)
    description = fields.Text('Description')
    stage = fields.Many2one('isp_helpdesk.stage', string="Stage")
    assigned_to = fields.Many2one('res.users', string="Assigned To")
    customer = fields.Many2one('res.users', string="Customer", domain=[('customer', '=', True)])
    helpdesk_team = fields.Many2one('isp_helpdesk.team', string="Team")
    priority = fields.Selection(AVAILABLE_PRIORITIES, string="Priority")
    close_date = fields.Datetime('Close Date', readonly=True, default=None)
    is_ticket_closed = fields.Boolean('Is Ticket Closed', default=False) # TODO-Arif: add a compute field for close date
    customer_rating = fields.Selection(AVAILABLE_RATINGS, string="Rating")
    customer_feedback = fields.Text('Feedback')
    solutions = fields.Many2many('isp_helpdesk.solution', string="Solutions")
