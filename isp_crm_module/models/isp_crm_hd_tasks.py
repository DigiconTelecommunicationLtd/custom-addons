# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskTasks(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_tasks"
    _description = "Helpdesk Solution"

    name = fields.Text('Description')
    problem = fields.Many2one('isp_crm_module.helpdesk', string='Problem', ondelete='set null',
                                  help='Problem to solve.')
    solution_id = fields.Many2one('isp_crm_module.helpdesk_solution', string='Solution', ondelete='set null',
                              help='Solution of the task.')
    assigned_to = fields.Many2one('hr.employee', string='Assigned To', ondelete='set null',
                              help='Person assigned to complete the task.')
    is_done = fields.Boolean('Is Done',
                          help='Is Task Complete.')
    color = fields.Integer()
