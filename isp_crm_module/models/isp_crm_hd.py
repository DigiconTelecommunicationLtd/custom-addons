# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import Warning, UserError

from .isp_crm_hd_td import HelpdeskTD
from . import isp_crm_hd_ticket_history
import datetime

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
AVAILABLE_STAGES = [
    ('0', 'New'),
    ('1', 'Doing'),
    ('2', 'TD'),
    ('3', 'Done'),
]

TD_FLAGS = [
    ('0', 'Not Sent to TD'),
    ('1', 'Sent to TD'),
    ('2', 'Marked Done by TD'),
    ('3', 'Cancelled by TD'),
]

class Helpdesk(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk"
    _description = "Helpdesk"
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']

    name = fields.Char('Request Name', required=True, index=True, copy=False, default='New')
    problem = fields.Many2one('isp_crm_module.helpdesk_problem',string="Problem", required=True, translate=True, ondelete='set null',help='Ticket Problem.')
    type = fields.Many2one('isp_crm_module.helpdesk_type', string='Type', ondelete='set null',
                                  help='Ticket Type.')
    helpdesk_td_ticket = fields.Many2one('isp_crm_module.helpdesk_td', string="Helpdesk TD Ticket", required=True, translate=True,
                                     ondelete='set null', help='Helpdesk TD Ticket.')
    description = fields.Text('Description')
    stage = fields.Many2one('isp_crm_module.helpdesk_stage', string='Stage', ondelete='set null',
                           help='Stage of the ticket.')
    default_stages = fields.Selection(AVAILABLE_STAGES, string="Stages",group_expand='_default_stages')
    assigned_to = fields.Many2one('hr.employee', string='Assigned To', ondelete='set null',
                                  help='Person assigned to complete the task.',track_visibility='onchange')
    team = fields.Many2one('hr.department', string='Department', store=True)
    team_leader = fields.Many2one('hr.employee', string='Team Leader', store=True)

    customer = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)],
                               track_visibility='onchange')
    customer_email = fields.Char(related='customer.email', store=True)
    customer_mobile = fields.Char(string="Mobile", related='customer.mobile', store=True)
    customer_phone = fields.Char(string="Phone", related='customer.phone', store=True)
    customer_company = fields.Char(string="Company", related='customer.parent_id.name', store=True)
    customer_address = fields.Char(string="Address", track_visibility='onchange')
    complexity = fields.Many2one('isp_crm_module.helpdesk_ticket_complexity', string='Complexity', ondelete='set null',
                                  help='Complexity level of the ticket.')
    solution_ids = fields.One2many('isp_crm_module.helpdesk_tasks', 'problem', string="Solutions", copy=True,
                                   auto_join=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string="Priority")
    customer_rating = fields.Selection(AVAILABLE_RATINGS, string="Rating")
    customer_feedback = fields.Text('Feedback')
    color = fields.Integer()
    td_flags = fields.Selection(TD_FLAGS, string="TD Flags")


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.helpdesk') or '/'
            vals['default_stages'] = '0'
            vals['td_flags'] = '0'
        newrecord = super(Helpdesk, self).create(vals)
        self.env['isp_crm_module.helpdesk_ticket_history'].create(
            {
                'type': vals.get('type'),
                'assigned_to': vals.get('assigned_to'),
                'ticket_id': newrecord.id
            }
        )

        return newrecord

    def _default_stages(self, stages, domain, order):
        stage_ids = self._fields['default_stages'].get_values(self.env)
        return stage_ids

    @api.model
    def _default_complexity(self):
        complexity_ids = self.env['isp_crm_module.helpdesk_ticket_complexity'].search([('name', '=', 'L-1')])
        return complexity_ids

    @api.onchange('assigned_to')
    def _onchange_assigned_to(self):
        self.team_leader = self.assigned_to and self.assigned_to.parent_id
        self.team = self.assigned_to.department_id

    @api.onchange('default_stages')
    def _onchange_default_stages(self):
        for helpdesk_ticket in self:
            if self.env['isp_crm_module.helpdesk'].search([('name', '=', helpdesk_ticket.name)]).default_stages =='3':
                raise UserError('System does not allow you to change stage after resolving the ticket.')
            if self.env['isp_crm_module.helpdesk'].search([('name', '=', helpdesk_ticket.name)]).td_flags =='1':
                raise UserError('Can not change stage. Ticket is not resolved by TD.')

    @api.onchange('td_flags')
    def _onchange_td_flags(self):
        for helpdesk_ticket in self:
            print(helpdesk_ticket.color)
            if self.env['isp_crm_module.helpdesk'].search([('name', '=', helpdesk_ticket.name)]).td_flags == '2':
                print(helpdesk_ticket.color)
                helpdesk_ticket.color = 3
                print(helpdesk_ticket.color)

    def get_customer_address_str(self, customer):
        address_str = ""
        if len(customer) > 0:
            address_str = ", ".join([
                customer.street or '',
                customer.street2 or '',
                customer.city or '',
                customer.state_id.name or '',
                customer.zip or '',
                customer.country_id.name or '',
            ])
        return address_str

    @api.onchange('customer')
    def _onchange_customer(self):
        self.customer_address = self.get_customer_address_str(customer=self.customer)

    @api.multi
    def action_send_ticket_to_td(self):
        for helpdesk_ticket in self:
            helpdesk_ticket.update({
                'td_flags': '1',
                'default_stages': '2',
            })

            helpdesk_td_problem = helpdesk_ticket.env['isp_crm_module.helpdesk_td_problem'].search([('name', '=', helpdesk_ticket.problem.name)])
            if helpdesk_td_problem :
                pass
            else:
                helpdesk_td_problem = helpdesk_ticket.env['isp_crm_module.helpdesk_td_problem'].create(

                    {

                        'name': helpdesk_ticket.problem.name,

                    }

                )

            helpdesk_td_type = helpdesk_ticket.env['isp_crm_module.helpdesk_td_type'].search(
                [('name', '=', helpdesk_ticket.type.name)])
            if helpdesk_td_type:
                pass
            else:
                helpdesk_td_type = helpdesk_ticket.env['isp_crm_module.helpdesk_td_type'].create(

                    {

                        'name': helpdesk_ticket.type.name,

                    }

                )

            helpdesk_td_ticket_complexity = helpdesk_ticket.env['isp_crm_module.helpdesk_td_ticket_complexity'].search(
                [('name', '=', helpdesk_ticket.complexity.name)])
            if helpdesk_td_ticket_complexity:
                pass
            else:
                helpdesk_td_ticket_complexity = helpdesk_ticket.env['isp_crm_module.helpdesk_td_ticket_complexity'].create(

                    {

                        'name': helpdesk_ticket.complexity.name,
                        'time_limit': helpdesk_ticket.complexity.time_limit,

                    }

                )

            helpdesk_ticket.env['isp_crm_module.helpdesk_td'].create(
            {
                'name': 'New',
                'problem': helpdesk_td_problem.id,
                'type': helpdesk_td_type.id,
                'helpdesk_ticket':helpdesk_ticket.id,
                'description': helpdesk_ticket.description,
                # 'assigned_to': helpdesk_ticket.assigned_to.id,
                # 'team': helpdesk_ticket.team.id,
                # 'team_leader': helpdesk_ticket.team_leader.id,
                'customer': helpdesk_ticket.customer.id,
                'customer_address': helpdesk_ticket.customer_address,
                'complexity': helpdesk_td_ticket_complexity.id,
                # 'solution_ids': helpdesk_ticket.solution_ids.id,
                'priority': helpdesk_ticket.priority,
                'customer_rating': helpdesk_ticket.customer_rating,
                'customer_feedback': helpdesk_ticket.customer_feedback,
                'color': helpdesk_ticket.color,

            }
        )

        return True

    @api.multi
    def action_cancel_ticket_to_td(self):
        for helpdesk_ticket in self:
            if helpdesk_ticket.td_flags == '1':
                helpdesk_ticket.update({
                    'td_flags': '0',
                    'default_stages': '1',
                })
                helpdesk_ticket.env['isp_crm_module.helpdesk_td'].search(
                        [('helpdesk_ticket', '=', helpdesk_ticket.id)]).unlink()
        return True