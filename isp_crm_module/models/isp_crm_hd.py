# -*- coding: utf-8 -*-

from odoo import api, fields, models
from . import isp_crm_hd_ticket_history

AVAILABLE_PRIORITIES = [
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
]

class Helpdesk(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk"
    _description = "Helpdesk"
    _rec_name = 'type'

    type = fields.Many2one('isp_crm_module.helpdesk_type', string='Type', ondelete='set null',
                                  help='Ticket Type.')
    stage = fields.Many2one('isp_crm_module.helpdesk_stage', string='Stage', ondelete='set null',
                           help='Stage of the ticket.')
    assigned_to = fields.Many2one('hr.employee', string='Assigned To', ondelete='set null',
                                  help='Person assigned to complete the task.')
    team = fields.Many2one('hr.department', string='Department', store=True)
    team_leader = fields.Many2one('hr.employee', string='Team Leader', store=True)

    customer = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)],
                               track_visibility='onchange')
    customer_email = fields.Char(related='customer.email', store=True)
    customer_mobile = fields.Char(string="Mobile", related='customer.mobile', store=True)
    customer_company = fields.Char(string="Company", related='customer.parent_id.name', store=True)
    customer_address = fields.Char(string="Address", track_visibility='onchange')
    complexity = fields.Many2one('isp_crm_module.helpdesk_ticket_complexity', string='Complexity', ondelete='set null',
                                  help='Complexity level of the ticket.')
    solution_ids = fields.One2many('isp_crm_module.helpdesk_tasks', 'problem', string="Solutions", copy=True,
                                   auto_join=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string="Priority")
    color = fields.Integer()

    @api.model
    def create(self, vals):

        newrecord = super(Helpdesk, self).create(vals)
        self.env['isp_crm_module.helpdesk_ticket_history'].create(
            {
                'type': vals.get('type'),
                'assigned_to': vals.get('assigned_to'),
                'ticket_id': newrecord.id
            }
        )

        return newrecord