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
    ('TD-NMC', 'TD-NMC'),
    ('SD', 'SD'),
    ('Done', 'Done'),
]

TD_FLAGS = [
    ('0', 'New'),
    ('1', 'In Progress'),
    ('2', 'Escalated to TD-TNOM/TD-CNOM'),
    ('3', 'Follow Up Pending'),
    ('4', 'Resolved by TD-TNOM/TD-CNOM'),
    ('5', 'Closed'),
    ('6', 'Pending Due to Customer'),
    ('7', 'Pending Due to Third Party'),
    ('8', 'Pending Due to Supplier Issue'),
    ('9', 'Reopened'),
]

AVAILABLE_PENDING_STATUS = [
        ('6', 'Pending Due to Customer'),
        ('7', 'Pending Due to Third Party'),
        ('8', 'Pending Due to Supplier Issue'),
]
# Constants representing complexity levels of helpdesk ticket

COMPLEXITY_LEVEL_ONE = [
    ('Name', 'L1'),
    ('Time', '8 Hours'),
]
COMPLEXITY_LEVEL_TWO = [
    ('Name', 'L2'),
    ('Time', '16 Hours'),
]
COMPLEXITY_LEVEL_THREE = [
    ('Name', 'L3'),
    ('Time', '24 Hours'),
]

SD_GROUP_MAIL_ADDRESS = "sd.mime@cg-bd.com"
TD_NMC_GROUP_MAIL_ADDRESS = "nmc.mime@cg-bd.com"
ALL_DEPARTMENTAL_HEAD_GROUP_MAIL = "hod.mime@cg-bd.com"
TD_TNOM_GROUP_MAIL = "tnom.mime@cg-bd.com"
TD_CNOM_GROUP_MAIL = "cnom.mime@cg-bd.com"

class Helpdesk(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk"
    _description = "Helpdesk"
    _order = "create_date desc, id"
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']

    name = fields.Char('Request Name', index=True, copy=False, default='New', track_visibility='onchange')
    problem = fields.Many2one('isp_crm_module.helpdesk_problem',string="Problem", ondelete='set null',help='Ticket Problem.', track_visibility='onchange')
    type = fields.Many2one('isp_crm_module.helpdesk_type', string='Type', ondelete='set null',
                                  help='Ticket Type.', track_visibility='onchange')
    helpdesk_td_ticket = fields.Many2one('isp_crm_module.helpdesk_td', string="Helpdesk TD Ticket", required=False, translate=True,
                                     ondelete='set null', help='Helpdesk TD Ticket.')
    description = fields.Text('Description', track_visibility='onchange')
    stage = fields.Many2one('isp_crm_module.helpdesk_stage', string='Stage', ondelete='set null',
                           help='Stage of the ticket.')
    default_stages = fields.Selection(AVAILABLE_STAGES, string="Stages",group_expand='_default_stages', track_visibility='onchange')
    assigned_to = fields.Many2one('hr.employee', string='Assigned To', ondelete='set null',
                                  help='Person assigned to complete the task.',track_visibility='onchange')
    team = fields.Many2one('hr.department', string='Department', store=True, track_visibility='onchange')
    team_leader = fields.Many2one('hr.employee', string='Team Leader', store=True, track_visibility='onchange')

    customer = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)],
                               track_visibility='onchange')
    customer_email = fields.Char(related='customer.email', store=True)
    customer_mobile = fields.Char(string="Mobile", related='customer.mobile', store=True)
    customer_phone = fields.Char(string="Phone", related='customer.phone', store=True)
    customer_company = fields.Char(string="Company", related='customer.parent_id.name', store=True)
    customer_address = fields.Char(string="Address", track_visibility='onchange')
    complexity = fields.Many2one('isp_crm_module.helpdesk_ticket_complexity', string='Service Level', ondelete='set null',
                                  help='Complexity level of the ticket.', track_visibility='onchange')
    solution_ids = fields.One2many('isp_crm_module.helpdesk_tasks', 'problem', string="Solutions", copy=True,
                                   auto_join=True)
    priority = fields.Selection(AVAILABLE_PRIORITIES, string="Priority")
    customer_rating = fields.Selection(AVAILABLE_RATINGS, string="Rating")
    customer_feedback = fields.Text('Feedback')
    color = fields.Integer(default=1)
    td_flags = fields.Selection(TD_FLAGS, string="Status", track_visibility='onchange')
    sd_resolved_by = fields.Many2one('res.users', string='Resolved By', store=True, track_visibility='onchange')
    assigned_rm = fields.Many2one(string='RM', related='customer.assigned_rm', track_visibility='onchange', readonly=True)
    pending_status = fields.Selection(AVAILABLE_PENDING_STATUS, string="Pending Status", track_visibility='onchange')
    level_change_time = fields.Datetime(string='Level Change Time', default=datetime.datetime.now(), track_visibility='onchange')
    complexity_name = fields.Char(string='Complexity Name', track_visibility='onchange')
    is_resolved_by_td_tnom_cnom = fields.Boolean()
    send_to_sd = fields.Boolean()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.helpdesk') or '/'
            vals['default_stages'] = 'New'
            vals['td_flags'] = TD_FLAGS[0][0]
            helpdesk_ticket_complexity = self.env['isp_crm_module.helpdesk_ticket_complexity'].search([('name', '=', COMPLEXITY_LEVEL_ONE[0][1])])
            if helpdesk_ticket_complexity:
                vals['complexity'] = helpdesk_ticket_complexity.id
                vals['complexity_name'] = helpdesk_ticket_complexity.name
                # pass
            else:
                helpdesk_ticket_complexity = helpdesk_ticket_complexity.env['isp_crm_module.helpdesk_ticket_complexity'].create(
                    {
                        'name': COMPLEXITY_LEVEL_ONE[0][1],
                        'time_limit': COMPLEXITY_LEVEL_ONE[1][1],
                    }
                )
                vals['complexity'] = helpdesk_ticket_complexity.id
                vals['complexity_name'] = helpdesk_ticket_complexity.name

        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.helpdesk') or '/'
            vals['default_stages'] = 'New'
            vals['td_flags'] = TD_FLAGS[0][0]
            helpdesk_ticket_complexity = self.env['isp_crm_module.helpdesk_ticket_complexity'].search(
                [('name', '=', COMPLEXITY_LEVEL_ONE[0][1])])
            if helpdesk_ticket_complexity:
                vals['complexity'] = helpdesk_ticket_complexity.id
                vals['complexity_name'] = helpdesk_ticket_complexity.name
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
                vals['complexity_name'] = helpdesk_ticket_complexity.name

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
        self.env['isp_crm_module.mail'].action_send_email(subject_mail,newrecord.assigned_rm.partner_id.email,newrecord.name,template_obj)
        self.env['isp_crm_module.mail'].action_send_email(subject_mail,SD_GROUP_MAIL_ADDRESS,newrecord.name,template_obj)
        self.env['isp_crm_module.mail'].action_send_email(subject_mail,TD_NMC_GROUP_MAIL_ADDRESS,newrecord.name,template_obj)

        return newrecord

    def _default_stages(self, stages, domain, order):
        stage_ids = self._fields['default_stages'].get_values(self.env)
        return stage_ids

    @api.model
    def _default_complexity(self):
        complexity_ids = self.env['isp_crm_module.helpdesk_ticket_complexity'].search([('name', '=', COMPLEXITY_LEVEL_ONE[0][1])])
        return complexity_ids

    @api.onchange('complexity')
    def _onchange_complexity(self):
        helpdesk_ticket_complexity = self.env['isp_crm_module.helpdesk_ticket_complexity'].search(
            [('name', '=', COMPLEXITY_LEVEL_ONE[0][1])])
        helpdesk_ticket_complexity_l2 = self.env['isp_crm_module.helpdesk_ticket_complexity'].search(
            [('name', '=', COMPLEXITY_LEVEL_TWO[0][1])])
        helpdesk_ticket_complexity_l3 = self.env['isp_crm_module.helpdesk_ticket_complexity'].search(
            [('name', '=', COMPLEXITY_LEVEL_THREE[0][1])])
        if self.complexity.id == helpdesk_ticket_complexity.id and self.default_stages == 'TD-NMC':
            raise UserError('System does not allow you to change service level to L1 once you have changed it to L2/L3.')
        elif self.td_flags != '2' and self.default_stages == 'TD-NMC' and (self.complexity.id == helpdesk_ticket_complexity_l2.id or self.complexity.id == helpdesk_ticket_complexity_l3.id):
            raise UserError(
                'You must change service level by clicking appropriate button above.')

    @api.multi
    def action_assign_complexity_l2(self):
        """
        
        :return:
        """
        helpdesk_ticket_complexity_l2 = self.env['isp_crm_module.helpdesk_ticket_complexity'].search(
            [('name', '=', COMPLEXITY_LEVEL_TWO[0][1])])
        if helpdesk_ticket_complexity_l2:
            self.update({
                'complexity': helpdesk_ticket_complexity_l2,
                'complexity_name': helpdesk_ticket_complexity_l2.name,
                'level_change_time': datetime.datetime.now(),
                'td_flags': TD_FLAGS[2][0],
                'pending_status': 0,
            })
        else:
            helpdesk_ticket_complexity_l2 = helpdesk_ticket_complexity_l2.env[
                'isp_crm_module.helpdesk_ticket_complexity'].create(
                {
                    'name': COMPLEXITY_LEVEL_TWO[0][1],
                    'time_limit': COMPLEXITY_LEVEL_TWO[1][1],
                }
            )
            self.update({
                'complexity': helpdesk_ticket_complexity_l2,
                'complexity_name': helpdesk_ticket_complexity_l2.name,
                'level_change_time': datetime.datetime.now(),
                'td_flags': TD_FLAGS[2][0],
                'pending_status': 0,
            })

        template_obj = self.env['isp_crm_module.mail'].sudo().search(
            [('name', '=', 'Helpdesk_Ticket_Complexity_Mail')],
            limit=1)
        # template_obj = self.env['isp_crm_module.mail_template_helpdesk_ticket_complexity'].sudo().search([],limit=1)
        subject_mail = "Mime Ticket Update Notice"
        hour = self.env[
            'isp_crm_module.helpdesk_ticket_complexity'].search(
            [('name', '=', COMPLEXITY_LEVEL_TWO[0][1])]).time_limit
        self.env['isp_crm_module.mail'].action_td_send_email(subject_mail, self.customer_email, self.name,
                                                             template_obj, hour)
        self.env['isp_crm_module.mail'].action_td_send_email(subject_mail, self.assigned_rm.partner_id.email,
                                                             self.name,
                                                             template_obj, hour)
        self.env['isp_crm_module.mail'].action_td_send_email(subject_mail, SD_GROUP_MAIL_ADDRESS, self.name,
                                                             template_obj, hour)

    @api.multi
    def action_assign_complexity_l3(self):
        helpdesk_ticket_complexity_l3 = self.env['isp_crm_module.helpdesk_ticket_complexity'].search(
            [('name', '=', COMPLEXITY_LEVEL_THREE[0][1])])
        if helpdesk_ticket_complexity_l3:
            self.update({
                'complexity': helpdesk_ticket_complexity_l3,
                'complexity_name': helpdesk_ticket_complexity_l3.name,
                'level_change_time': datetime.datetime.now(),
                'td_flags': TD_FLAGS[2][0],
                'pending_status': 0,
            })
        else:
            helpdesk_ticket_complexity_l3 = helpdesk_ticket_complexity_l3.env[
                'isp_crm_module.helpdesk_ticket_complexity'].create(
                {
                    'name': COMPLEXITY_LEVEL_THREE[0][1],
                    'time_limit': COMPLEXITY_LEVEL_THREE[1][1],
                }
            )
            self.update({
                'complexity': helpdesk_ticket_complexity_l3,
                'complexity_name': helpdesk_ticket_complexity_l3.name,
                'level_change_time': datetime.datetime.now(),
                'td_flags': TD_FLAGS[2][0],
                'pending_status': 0,
            })

        template_obj = self.env['isp_crm_module.mail'].sudo().search(
            [('name', '=', 'Helpdesk_Ticket_Complexity_Mail')],
            limit=1)
        # template_obj = self.env['isp_crm_module.mail_template_helpdesk_ticket_complexity'].sudo().search([],limit=1)
        subject_mail = "Mime Ticket Update Notice"
        hour = self.env[
            'isp_crm_module.helpdesk_ticket_complexity'].search(
            [('name', '=', COMPLEXITY_LEVEL_THREE[0][1])]).time_limit
        self.env['isp_crm_module.mail'].action_td_send_email(subject_mail, self.customer_email, self.name,
                                                             template_obj, hour)
        self.env['isp_crm_module.mail'].action_td_send_email(subject_mail, self.assigned_rm.partner_id.email, self.name,
                                                             template_obj, hour)
        self.env['isp_crm_module.mail'].action_td_send_email(subject_mail, SD_GROUP_MAIL_ADDRESS, self.name,
                                                             template_obj, hour)

    @api.onchange('assigned_to')
    def _onchange_assigned_to(self):
        self.team_leader = self.assigned_to and self.assigned_to.parent_id
        self.team = self.assigned_to.department_id

        if self.assigned_to:
            for ticket in self:
                if self._origin.name:
                    template_obj = self.env['isp_crm_module.mail'].sudo().search(
                        [('name', '=', 'Ticket_Assignment')],
                        limit=1)
                    # template_obj = self.env['isp_crm_module.mail_template_helpdesk_ticket_complexity'].sudo().search([],limit=1)
                    subject_mail = "New Ticket Assignment"
                    self.env['isp_crm_module.mail'].action_send_email(subject_mail, TD_TNOM_GROUP_MAIL, self._origin.name,
                                                                      template_obj)
                    self.env['isp_crm_module.mail'].action_send_email(subject_mail, TD_CNOM_GROUP_MAIL, self._origin.name,
                                                                      template_obj)
                else:
                    name = 'New'
                    template_obj = self.env['isp_crm_module.mail'].sudo().search(
                        [('name', '=', 'Ticket_Assignment')],
                        limit=1)
                    # template_obj = self.env['isp_crm_module.mail_template_helpdesk_ticket_complexity'].sudo().search([],limit=1)
                    subject_mail = "New Ticket Assignment"
                    self.env['isp_crm_module.mail'].action_send_email(subject_mail, TD_TNOM_GROUP_MAIL, name,
                                                                      template_obj)
                    self.env['isp_crm_module.mail'].action_send_email(subject_mail, TD_CNOM_GROUP_MAIL, name,
                                                                      template_obj)

    @api.onchange('default_stages')
    def _onchange_default_stages(self):
        # Prevent dragging back from TD-NMC to New stage
        if self.default_stages == 'New' and self.color == 3:
            raise UserError('System does not allow you to drag ticket from TD-NMC to New stage.')
        # Prevent dragging back from TD-NMC to New stage
        elif self.default_stages == 'New' and self.color == 4:
            raise UserError('System does not allow you to drag ticket from TD-NMC to New stage.')
        # Prevent dragging back from SD to New stage
        elif self.default_stages == 'New' and self.color == 7:
            raise UserError('System does not allow you to drag ticket from SD to New stage.')
        # Prevent dragging back from SD to TD-NMC stage
        elif self.default_stages == 'TD-NMC' and self.color == 7:
            raise UserError('System does not allow you to drag ticket from SD to TD-NMC stage.')
        # Prevent dragging back from Done to New stage
        elif self.default_stages == 'New' and self.color == 10:
            raise UserError('System does not allow you to drag ticket from Done to New stage.')
        # Prevent dragging back from Done to TD-NMC stage
        elif self.default_stages == 'TD-NMC' and self.color == 10:
            raise UserError('System does not allow you to drag ticket from Done to TD-NMC stage.')
        # Prevent dragging back from Done to SD stage
        elif self.default_stages == 'SD' and self.color == 10:
            raise UserError('System does not allow you to drag ticket from Done to SD stage.')
        # Prevent dragging to Done stage
        elif self.default_stages == 'Done' and self.td_flags != TD_FLAGS[5][0]:
            raise UserError('System does not allow you to drag ticket to Done stage.')
        # Prevent dragging to SD stage
        elif self.default_stages == 'SD' and self.td_flags != TD_FLAGS[3][0]:
            raise UserError('System does not allow you to drag ticket to SD stage.')
        # Change ticket color to red
        elif self.default_stages == 'New':
            self.update({
                    'color': 1,
                })
        # Change status to 'In Progress' and color to yellow
        elif self.default_stages == 'TD-NMC':
            self.update({
                    'td_flags': TD_FLAGS[1][0],
                    'color': 3,
                })

    @api.onchange('td_flags')
    def _onchange_td_flags(self):
        if self.default_stages == 'New':
            raise UserError('You can not change status of a ticket when it is in new stage.')
        elif self.default_stages == 'TD-NMC':
            if self.td_flags == TD_FLAGS[0][0] or self.td_flags == TD_FLAGS[3][0] or self.td_flags == TD_FLAGS[5][0] or self.td_flags == TD_FLAGS[9][0]:
                raise UserError('You can not change status of a ticket from dropdown.')
            elif self.td_flags == TD_FLAGS[2][0] or self.td_flags == TD_FLAGS[4][0]:
                helpdesk_ticket_complexity = self.env['isp_crm_module.helpdesk_ticket_complexity'].search(
                    [('name', '=', COMPLEXITY_LEVEL_ONE[0][1])])
                if self.complexity != helpdesk_ticket_complexity.id:
                    raise UserError('You can not change status of a ticket from dropdown.')
            elif self.td_flags == TD_FLAGS[6][0] or self.td_flags == TD_FLAGS[7][0] or self.td_flags == TD_FLAGS[8][0]:
                if self.pending_status:
                    pass
                else:
                    raise UserError('You can not change status of a ticket from dropdown.')


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
    def action_resolved_by_td_tnom_cnom(self):
        # Change ticket color to light blue, update status to 'Resolved by TD-TNOM/TD-CNOM'
        self.update({
            'td_flags': TD_FLAGS[4][0],
            'color': 4,
            'pending_status': 0,
            'is_resolved_by_td_tnom_cnom': True,
        })

        template_obj = self.env['isp_crm_module.mail'].sudo().search(
            [('name', '=', 'Ticket_Resolved')],
            limit=1)
        # template_obj = self.env['isp_crm_module.mail_template_helpdesk_ticket_closing'].sudo().search([],limit=1)
        subject_mail = "Ticket Resolved"
        self.env['isp_crm_module.mail'].action_send_email(subject_mail, self.assigned_rm.partner_id.email, self.name,
                                                          template_obj)
        self.env['isp_crm_module.mail'].action_send_email(subject_mail, SD_GROUP_MAIL_ADDRESS, self.name, template_obj)
        self.env['isp_crm_module.mail'].action_send_email(subject_mail, TD_NMC_GROUP_MAIL_ADDRESS, self.name,
                                                          template_obj)

        return True

    @api.multi
    def action_resolved_by_sd(self):
        # Change ticket color to blue, stage to SD, status to 'Follow Up Pending'
        self.update({
            'td_flags': TD_FLAGS[3][0],
            'default_stages': 'SD',
            'sd_resolved_by':self.env.uid,
            'color':7,
            'send_to_sd':True,
        })

        return True

    @api.multi
    def action_final_resolved_by_sd(self):
        # Close the ticket, Change the color to green
        self.update({
            'td_flags': TD_FLAGS[5][0],
            'default_stages': 'Done',
            'color': 10,
        })

        template_obj = self.env['isp_crm_module.mail'].sudo().search(
            [('name', '=', 'Helpdesk_Ticket_Closing_Mail')],
            limit=1)
        # template_obj = self.env['isp_crm_module.mail_template_helpdesk_ticket_closing'].sudo().search([],limit=1)
        subject_mail = "Mime Ticket Resolved"
        self.env['isp_crm_module.mail'].action_send_email(subject_mail, self.customer_email, self.name, template_obj)
        self.env['isp_crm_module.mail'].action_send_email(subject_mail, self.assigned_rm.partner_id.email, self.name, template_obj)
        self.env['isp_crm_module.mail'].action_send_email(subject_mail, SD_GROUP_MAIL_ADDRESS, self.name, template_obj)
        self.env['isp_crm_module.mail'].action_send_email(subject_mail, TD_NMC_GROUP_MAIL_ADDRESS, self.name, template_obj)


    @api.multi
    def action_not_resolved(self):
        helpdesk_ticket_complexity = self.env['isp_crm_module.helpdesk_ticket_complexity'].search(
            [('name', '=', COMPLEXITY_LEVEL_ONE[0][1])])
        self.update({
            'td_flags': TD_FLAGS[9][0],
            'default_stages': 'TD-NMC',
            'color': 3,
            'complexity': helpdesk_ticket_complexity,
            'complexity_name': helpdesk_ticket_complexity.name,
            'pending_status': 0,
            'is_resolved_by_td_tnom_cnom': False,
            'send_to_sd': False,
        })

        template_obj = self.env['isp_crm_module.mail'].sudo().search(
            [('name', '=', 'Helpdesk_Ticket_Reopening_Mail')],
            limit=1)
        # template_obj = self.env['isp_crm_module.mail_template_helpdesk_ticket_closing'].sudo().search([],limit=1)
        subject_mail = "Mime Ticket Re-opening"
        self.env['isp_crm_module.mail'].action_send_email(subject_mail, self.customer_email, self.name, template_obj)
        self.env['isp_crm_module.mail'].action_send_email(subject_mail, ALL_DEPARTMENTAL_HEAD_GROUP_MAIL, self.name, template_obj)

    @api.multi
    def action_btn_send_email(self):
        return True

    @api.onchange('pending_status')
    def _onchange_pending_status(self):
        """

        :return:
        """
        try:
            pending_status = int(self.pending_status)
            if pending_status == 0:
                self.td_flags = TD_FLAGS[3][0]
            else:
                self.td_flags = TD_FLAGS[pending_status][0]
        except Exception as ex:
            print(ex)