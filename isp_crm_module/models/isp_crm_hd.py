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
    ('New', 'New'),
    ('Doing', 'Doing'),
    ('TD', 'TD'),
    ('RM', 'RM'),
    ('Done', 'Done'),
]

TD_FLAGS = [
    ('0', 'Not Sent to TD'),
    ('1', 'Sent to TD'),
    ('2', 'Marked Done by TD'),
    ('3', 'Resolved'),
    ('4', 'Pending in RM'),
    ('5', 'Confirmed by RM'),
]

# Constants representing complexity levels of helpdesk ticket

COMPLEXITY_LEVEL_ONE = [
    ('Name', 'L-1'),
    ('Time', '8 Hours'),
]
COMPLEXITY_LEVEL_TWO = [
    ('Name', 'L-2'),
    ('Time', '16 Hours'),
]
COMPLEXITY_LEVEL_THREE = [
    ('Name', 'L-3'),
    ('Time', '24 Hours'),
]

class Helpdesk(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk"
    _description = "Helpdesk"
    _order = "create_date desc, id"
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']

    name = fields.Char('Request Name', index=True, copy=False, default='New')
    problem = fields.Many2one('isp_crm_module.helpdesk_problem',string="Problem", ondelete='set null',help='Ticket Problem.')
    type = fields.Many2one('isp_crm_module.helpdesk_type', string='Type', ondelete='set null',
                                  help='Ticket Type.')
    helpdesk_td_ticket = fields.Many2one('isp_crm_module.helpdesk_td', string="Helpdesk TD Ticket", required=False, translate=True,
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
    complexity = fields.Many2one('isp_crm_module.helpdesk_ticket_complexity', string='Service Level', ondelete='set null',
                                  help='Complexity level of the ticket.')
    solution_ids = fields.One2many('isp_crm_module.helpdesk_tasks', 'problem', string="Solutions", copy=True,
                                   auto_join=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string="Priority")
    customer_rating = fields.Selection(AVAILABLE_RATINGS, string="Rating")
    customer_feedback = fields.Text('Feedback')
    color = fields.Integer(default=1)
    td_flags = fields.Selection(TD_FLAGS, string="Status")
    sd_resolved_by = fields.Many2one('res.users', string='Resolved By', store=True, track_visibility='onchange')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.helpdesk') or '/'
            vals['default_stages'] = 'New'
            vals['td_flags'] = TD_FLAGS[0][0]
            helpdesk_ticket_complexity = self.env['isp_crm_module.helpdesk_ticket_complexity'].search([('name', '=', COMPLEXITY_LEVEL_ONE[0][1])])
            if helpdesk_ticket_complexity:
                vals['complexity'] = helpdesk_ticket_complexity.id
                # pass
            else:
                helpdesk_ticket_complexity = helpdesk_ticket_complexity.env['isp_crm_module.helpdesk_ticket_complexity'].create(
                    {
                        'name': COMPLEXITY_LEVEL_ONE[0][1],
                        'time_limit': COMPLEXITY_LEVEL_ONE[1][1],
                    }
                )
                vals['complexity'] = helpdesk_ticket_complexity.id

        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.helpdesk') or '/'
            vals['default_stages'] = 'New'
            vals['td_flags'] = TD_FLAGS[0][0]
            helpdesk_ticket_complexity = self.env['isp_crm_module.helpdesk_ticket_complexity'].search(
                [('name', '=', COMPLEXITY_LEVEL_ONE[0][1])])
            if helpdesk_ticket_complexity:
                vals['complexity'] = helpdesk_ticket_complexity.id
                # pass
            else:
                helpdesk_ticket_complexity = helpdesk_ticket_complexity.env[
                    'isp_crm_module.helpdesk_ticket_complexity'].create(
                    {
                        'name': COMPLEXITY_LEVEL_ONE[0][1],
                        'time_limit': COMPLEXITY_LEVEL_ONE[1][1],
                    }
                )
                vals['complexity'] = helpdesk_ticket_complexity.id

        newrecord = super(Helpdesk, self).create(vals)
        self.env['isp_crm_module.helpdesk_ticket_history'].create(
            {
                'type': vals.get('type'),
                'assigned_to': vals.get('assigned_to'),
                'ticket_id': newrecord.id
            }
        )

        customer = newrecord.customer
        if customer:
            get_assigned_rm_from_customer = customer.assigned_rm
            if get_assigned_rm_from_customer:
                notification_message = "Ticket No. : " + str(newrecord.name) + " Created"
                get_user = self.env['res.users'].search([('id', '=', get_assigned_rm_from_customer.id)])
                get_user.notify_info(notification_message)

                try:
                    recipient_ids = [(get_user.partner_id.id)]
                    channel_ids = [(get_user.partner_id.channel_ids)]

                    ch = []
                    for channel in channel_ids[0]:
                        ch.append(channel.id)
                        channel.message_post(subject='New notification', body=notification_message,
                                             subtype="mail.mt_comment")
                except Exception as ex:
                    error = 'Failed to send notification. Error Message: ' + str(ex)
                    raise UserError(error)


        template_obj = self.env['isp_crm_module.mail'].sudo().search(
            [('name', '=', 'Helpdesk_Ticket_Creation_Mail')],
            limit=1)
        # template_obj = self.env['isp_crm_module.mail_template_helpdesk_ticket_creation'].sudo().search([],limit=1)
        subject_mail = "Mime New Ticket Creation"
        self.env['isp_crm_module.mail'].action_send_email(subject_mail,newrecord.customer_email,newrecord.name,template_obj)

        return newrecord

    def _default_stages(self, stages, domain, order):
        stage_ids = self._fields['default_stages'].get_values(self.env)
        return stage_ids

    @api.model
    def _default_complexity(self):
        complexity_ids = self.env['isp_crm_module.helpdesk_ticket_complexity'].search([('name', '=', COMPLEXITY_LEVEL_ONE[0][1])])
        return complexity_ids

    @api.onchange('assigned_to')
    def _onchange_assigned_to(self):
        self.team_leader = self.assigned_to and self.assigned_to.parent_id
        self.team = self.assigned_to.department_id

    @api.onchange('default_stages')
    def _onchange_default_stages(self):
        if self.default_stages != 'Done' and self.td_flags == TD_FLAGS[3][0]:
            raise UserError('System does not allow you to change stage after resolving the ticket.')
        if self.td_flags == TD_FLAGS[1][0]:
            raise UserError('Can not change stage. Ticket is not resolved by TD.')
        if self.td_flags == TD_FLAGS[2][0]:
            raise UserError('Can not change stage. Ticket is not resolved by SD.')
        if self.default_stages !='RM' and self.td_flags == TD_FLAGS[4][0]:
            raise UserError('System does not allow you to drag ticket from RM stage.')
        elif self.default_stages !='RM' and self.td_flags == TD_FLAGS[5][0]:
            raise UserError('System does not allow you to drag ticket from RM stage.')

        if self.default_stages == 'New':
            self.update({
                    'color': 1,
                })
        if self.default_stages == 'Doing':
            self.update({
                    'color': 3,
                })
        if self.default_stages == 'Done' and self.td_flags == TD_FLAGS[5][0]:
            self.update({
                    'td_flags': TD_FLAGS[3][0],
                    'color': 11,
                })
        elif self.default_stages == 'Done' and self.td_flags != TD_FLAGS[5][0]:
            raise UserError('You can not drag the ticket to Done stage unless it is resolved by RM.')
        if self.default_stages == 'TD':
            raise UserError('You can not drag the ticket to TD stage unless you assign it to TD by action.')
        if self.default_stages == 'RM':
            if self.td_flags != TD_FLAGS[3][0]:
                raise UserError('You can not drag the ticket to RM stage unless you assign it to RM by action.')

    @api.onchange('td_flags')
    def _onchange_td_flags(self):
        if self.td_flags == TD_FLAGS[2][0]:
            self.update({
                'color': 10,
            })

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
    def action_send_ticket_to_rm(self):
        self.update({
            'td_flags': TD_FLAGS[4][0],
            'default_stages': 'RM',
            'color': 7,
        })
        # Send notification to assigned RM
        notification_message = "You have got new helpdesk ticket, Ticket ID: "+ str(self.name)
        customer = self.customer
        if customer:
            get_assigned_rm_from_customer = customer.assigned_rm
            if get_assigned_rm_from_customer:
                get_user = self.env['res.users'].search([('id','=', get_assigned_rm_from_customer.id)])
                get_user.notify_info(notification_message)

                try:
                    recipient_ids = [(get_user.partner_id.id)]
                    channel_ids = [(get_user.partner_id.channel_ids)]

                    ch = []
                    for channel in channel_ids[0]:
                        ch.append(channel.id)
                        channel.message_post(subject='New ticket at RM', body=notification_message, subtype="mail.mt_comment")
                except Exception as ex:
                    error = 'Failed to send notification. Error Message: ' + str(ex)
                    raise UserError(error)
        return True

    @api.multi
    def action_send_ticket_to_td(self):
        self.update({
            'td_flags': TD_FLAGS[1][0],
            'default_stages': 'TD',
            'color': 4,
        })

        helpdesk_td_problem = self.env['isp_crm_module.helpdesk_td_problem'].search([('name', '=', self.problem.name)])
        if helpdesk_td_problem :
            pass
        else:
            helpdesk_td_problem = self.env['isp_crm_module.helpdesk_td_problem'].create(

                {

                    'name': self.problem.name,

                }

            )

        helpdesk_td_type = self.env['isp_crm_module.helpdesk_td_type'].search(
            [('name', '=', self.type.name)])
        if helpdesk_td_type:
            pass
        else:
            helpdesk_td_type = self.env['isp_crm_module.helpdesk_td_type'].create(

                {

                    'name': self.type.name,

                }

            )

        helpdesk_td_ticket_complexity = self.env['isp_crm_module.helpdesk_td_ticket_complexity'].search(
            [('name', '=', self.complexity.name)])
        if helpdesk_td_ticket_complexity:
            pass
        else:
            helpdesk_td_ticket_complexity = self.env['isp_crm_module.helpdesk_td_ticket_complexity'].create(

                {

                    'name': self.complexity.name,
                    'time_limit': self.complexity.time_limit,

                }

            )

        self.env['isp_crm_module.helpdesk_td'].create(
        {
            'name': 'New',
            'problem': helpdesk_td_problem.id,
            'type': helpdesk_td_type.id,
            'helpdesk_ticket':self.id,
            'description': self.description,
            'customer': self.customer.id,
            'customer_address': self.customer_address,
            'complexity': helpdesk_td_ticket_complexity.id,
            'priority': self.priority,
            'customer_rating': self.customer_rating,
            'customer_feedback': self.customer_feedback,
            'color': 1,

        }
        )

        customer = self.customer
        if customer:
            get_assigned_rm_from_customer = customer.assigned_rm
            if get_assigned_rm_from_customer:
                notification_message = "Ticket No. : " + str(self.name) + " sent to td"
                get_user = self.env['res.users'].search([('id', '=', get_assigned_rm_from_customer.id)])
                get_user.notify_info(notification_message)

                try:
                    recipient_ids = [(get_user.partner_id.id)]
                    channel_ids = [(get_user.partner_id.channel_ids)]

                    ch = []
                    for channel in channel_ids[0]:
                        ch.append(channel.id)
                        channel.message_post(subject='New notification', body=notification_message,
                                             subtype="mail.mt_comment")
                except Exception as ex:
                    error = 'Failed to send notification. Error Message: ' + str(ex)
                    raise UserError(error)

        return True

    @api.multi
    def action_cancel_ticket_to_td(self):
        if self.td_flags == TD_FLAGS[1][0]:
            self.update({
                'td_flags': TD_FLAGS[0][0],
                'default_stages': 'Doing',
            })

            customer = self.customer
            if customer:
                get_assigned_rm_from_customer = customer.assigned_rm
                if get_assigned_rm_from_customer:
                    notification_message = "Ticket No. : " + str(self.name) + " cancelled from td"
                    get_user = self.env['res.users'].search([('id', '=', get_assigned_rm_from_customer.id)])
                    get_user.notify_info(notification_message)

                    try:
                        recipient_ids = [(get_user.partner_id.id)]
                        channel_ids = [(get_user.partner_id.channel_ids)]

                        ch = []
                        for channel in channel_ids[0]:
                            ch.append(channel.id)
                            channel.message_post(subject='New notification', body=notification_message,
                                                 subtype="mail.mt_comment")
                    except Exception as ex:
                        error = 'Failed to send notification. Error Message: ' + str(ex)
                        raise UserError(error)


            self.env['isp_crm_module.helpdesk_td'].search(
                    [('helpdesk_ticket', '=', self.id)]).unlink()
        return True

    @api.multi
    def action_resolved_by_sd(self):
        if self.td_flags == TD_FLAGS[2][0]:
            self.update({
                'td_flags': TD_FLAGS[4][0],
                'default_stages': 'RM',
                'sd_resolved_by':self.env.uid,
                'color':7,
            })

        customer = self.customer
        if customer:
            get_assigned_rm_from_customer = customer.assigned_rm
            if get_assigned_rm_from_customer:
                notification_message = "Ticket No. : " + str(self.name) + " resolved by sd and sent to RM"
                get_user = self.env['res.users'].search([('id', '=', get_assigned_rm_from_customer.id)])
                get_user.notify_info(notification_message)

                try:
                    recipient_ids = [(get_user.partner_id.id)]
                    channel_ids = [(get_user.partner_id.channel_ids)]

                    ch = []
                    for channel in channel_ids[0]:
                        ch.append(channel.id)
                        channel.message_post(subject='New notification', body=notification_message,
                                             subtype="mail.mt_comment")
                except Exception as ex:
                    error = 'Failed to send notification. Error Message: ' + str(ex)
                    raise UserError(error)

        return True

    @api.multi
    def action_resolved_by_rm(self):
        customer = self.customer
        if customer:
            get_assigned_rm_from_customer = customer.assigned_rm
            if get_assigned_rm_from_customer:
                if get_assigned_rm_from_customer.id != self.env.uid:
                    raise UserError('This ticket can only be resolved by the assigned RM.')
                else:
                    notification_message = "Ticket No. : " + str(self.name) + " resolved by RM"
                    get_user = self.env['res.users'].search([('id', '=', get_assigned_rm_from_customer.id)])
                    get_user.notify_info(notification_message)

                    try:
                        recipient_ids = [(get_user.partner_id.id)]
                        channel_ids = [(get_user.partner_id.channel_ids)]

                        ch = []
                        for channel in channel_ids[0]:
                            ch.append(channel.id)
                            channel.message_post(subject='New notification', body=notification_message,
                                                 subtype="mail.mt_comment")
                    except Exception as ex:
                        error = 'Failed to send notification. Error Message: ' + str(ex)
                        raise UserError(error)

        self.update({
            'td_flags': TD_FLAGS[5][0],
        })

        return True

    @api.multi
    def action_final_resolved_by_sd(self):
        self.update({
            'td_flags': TD_FLAGS[3][0],
            'default_stages': 'Done',
            'color': 11,
        })

        customer = self.customer
        if customer:
            get_assigned_rm_from_customer = customer.assigned_rm
            if get_assigned_rm_from_customer:
                notification_message = "Ticket No. : " + str(self.name) + " resolved"
                get_user = self.env['res.users'].search([('id', '=', get_assigned_rm_from_customer.id)])
                get_user.notify_info(notification_message)

                try:
                    recipient_ids = [(get_user.partner_id.id)]
                    channel_ids = [(get_user.partner_id.channel_ids)]

                    ch = []
                    for channel in channel_ids[0]:
                        ch.append(channel.id)
                        channel.message_post(subject='New notification', body=notification_message,
                                             subtype="mail.mt_comment")
                except Exception as ex:
                    error = 'Failed to send notification. Error Message: ' + str(ex)
                    raise UserError(error)

        template_obj = self.env['isp_crm_module.mail'].sudo().search(
            [('name', '=', 'Helpdesk_Ticket_Closing_Mail')],
            limit=1)
        # template_obj = self.env['isp_crm_module.mail_template_helpdesk_ticket_closing'].sudo().search([],limit=1)
        subject_mail = "Mime Ticket Resolved"
        self.env['isp_crm_module.mail'].action_send_email(subject_mail, self.customer_email, self.name, template_obj)

    @api.multi
    def action_not_resolved(self):
        customer = self.customer
        if customer:
            get_assigned_rm_from_customer = customer.assigned_rm
            if get_assigned_rm_from_customer:
                if get_assigned_rm_from_customer.id != self.env.uid:
                    raise UserError('This ticket can only be resolved by the assigned RM.')
                else:
                    notification_message = "Ticket No. : " + str(self.name) + " marked as not resolved"
                    get_user = self.env['res.users'].search([('id', '=', get_assigned_rm_from_customer.id)])
                    get_user.notify_info(notification_message)

                    try:
                        recipient_ids = [(get_user.partner_id.id)]
                        channel_ids = [(get_user.partner_id.channel_ids)]

                        ch = []
                        for channel in channel_ids[0]:
                            ch.append(channel.id)
                            channel.message_post(subject='New notification', body=notification_message,
                                                 subtype="mail.mt_comment")
                    except Exception as ex:
                        error = 'Failed to send notification. Error Message: ' + str(ex)
                        raise UserError(error)

        self.update({
            'td_flags': TD_FLAGS[0][0],
            'default_stages': 'Doing',
            'color': 3,
        })

    @api.multi
    def action_btn_send_email(self):
        return True

