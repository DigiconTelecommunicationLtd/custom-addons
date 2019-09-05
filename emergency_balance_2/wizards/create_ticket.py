from odoo import models, fields, api,_
from odoo.exceptions import Warning, UserError
from datetime import datetime, timezone, timedelta, date
from odoo.addons.isp_crm_module.models.radius_integration import *
from odoo.addons.emergency_balance_2.models.color_code import *


DEFAULT_DATE_FORMAT = '%Y-%m-%d'
EMERGENCY_TYPE = [
    (1, _('1 Day')),
    (2, _('2 Days')),
    (3, _('3 Days')),
    (4, _('4 Days')),
    (5, _('5 Days')),
    (6, _('6 Days')),
    (7, _('7 Days')),
]
CUSTOMER_INACTIVE_STATUS = 'inactive'
CUSTOMER_ACTIVE_STATUS = 'active'

class DashboardOne(models.TransientModel):
    _name = 'emergency.wizard.balance'

    has_due = fields.Boolean(string='due?',
                             track_visibility='onchange', default=False)

    set_for_approval = fields.Boolean(string='approval needed?',
                                      track_visibility='onchange', default=False)

    approved = fields.Boolean(string='approved?',
                              track_visibility='onchange', default=False)
    rejected = fields.Boolean(string='rejected?',
                              track_visibility='onchange', default=False)

    approved_by = fields.Many2one('res.users', string='Approved By', track_visibility='onchange', default=False)
    rejected_by = fields.Many2one('res.users', string='Rejected By', track_visibility='onchange', default=False)

    disable_header = fields.Boolean(string='header?', default=False)

    due_paid = fields.Boolean(string='paid?', default=False, track_visibility='onchange')

    customer = fields.Many2one('res.partner', String='Customer', track_visibility='onchange',
                               domain=[('subscriber_id', '!=', 'New'), ('subscriber_id', 'like', 'MR')])
    emergency_date = fields.Selection(EMERGENCY_TYPE, string='Emergency Balance', help="Emergency Balance",
                                      required=True, track_visibility='onchange')
    due_amount = fields.Float('Due Amount', required=True,
                              default=0.0,
                              track_visibility='onchange')

    subscriber_id = fields.Char(compute='change_emergency_date', string='Subscriber ID')
    current_package = fields.Char(compute='change_emergency_date', string='Current Package')
    current_package_price = fields.Char(compute='change_emergency_date', string='Current Package Price')
    current_package_end_date = fields.Char(compute='change_emergency_date', string='Valid Till')
    next_package_start_date = fields.Char(compute='change_emergency_date', string='Next Start Date')
    assigned_rm = fields.Char(compute='change_emergency_date', string='Assigned RM')
    balance = fields.Char(compute='change_emergency_date', string='Customer Balance')

    state = fields.Selection([
        ('new', 'New'),
        ('approval', 'Waiting for Approval'),
        ('due', 'Due Accepted'),
        ('paid', 'Due Paid'),
        ('rejected', 'Due Request Rejected'),
    ], default='new')
    @api.onchange('customer')
    def change_emergency_date(self):
        for records in self:
            records.current_package = str(self.customer.current_package_id.name)
            records.current_package_price = str(self.customer.current_package_price)
            records.current_package_end_date = str(self.customer.current_package_end_date)
            records.next_package_start_date = str(self.customer.next_package_start_date)
            records.assigned_rm = str(self.customer.assigned_rm.name)
            records.subscriber_id = str(self.customer.subscriber_id)
            records.balance = str(abs(self.customer.get_customer_balance(self.customer.id)))


    def on_submit(self):
        form_view_id = self.env.ref('emergency_balance_2.emergency_balance_create_ticket_wizard_view_form').ids

        data = self.env['emergency.balance'].sudo().search(
            [('customer', '=', self.customer.id), ('has_due', '=', 'true')], limit=1)
        data2 = self.env['emergency.balance'].sudo().search(
            [('customer', '=', self.customer.id), ('set_for_approval', '=', 'true')], limit=1)
        print(data)
        if data:
            raise UserError('A ticket is already raised and emergency balance is already given')
            print('raised has due')
        print(data2)
        if data2:
            raise UserError('A ticket is already raised and pending for approval')
            print('raised has approval')

        update_data = self.env['emergency.balance']

        # if greater than two days need approval
        if self.emergency_date > 2:
            update_data.create({
                'customer':self.customer.id,
                'approved': False,
                'has_due': False,
                'state':'approval',
                'set_for_approval': True,
                'approved_by': self.env.uid,
                'emergency_date': self.emergency_date,
                'color':WAITING_FOR_APPROVAL,
                'name':self.env['ir.sequence'].next_by_code('emergency_balance.emergency_balance')
            })
            template_obj_new_service_request = self.env['emergency_balance.mail'].sudo().search(
                [('name', '=', 'new_emergency_balance_approval')],
                limit=1)
            self.env['emergency_balance.mail'].action_send_email(str(self.emergency_date),
                                                                 self.customer.name,
                                                                 self.customer.subscriber_id,
                                                                 self.customer.current_package_id.name,
                                                                 str(self.customer.current_package_price),
                                                                 template_obj_new_service_request
                                                                 )
            # self.approved = False
            # self.has_due = False
            # self.set_for_approval = True
        else:
            update_data.create({
                'customer': self.customer.id,
                'approved': True,
                'has_due': True,
                'set_for_approval': False,
                'state': 'due',
                'active_status':'active',
                'emergency_date': self.emergency_date,
                'color': DUE_ACCEPTED,
                'name': self.env['ir.sequence'].next_by_code('emergency_balance.emergency_balance')
            })
            customer_ref = self.env['res.partner'].search([('subscriber_id', '=', self.customer.subscriber_id)], limit=1)
            print('customer_red', customer_ref)
            print('current_package_end_date', customer_ref.current_package_end_date)
            #if the user is active then given date is current package end date else its today plus 6 hours
            given_date_obj = None

            if customer_ref.active_status == CUSTOMER_INACTIVE_STATUS:
                today_new = datetime.now() + timedelta(hours=6)
                #today = today_new.date()
                given_date_obj = today_new.date()
            else:
                given_date_obj = datetime.strptime(customer_ref.current_package_end_date, DEFAULT_DATE_FORMAT)

            print('given_date', str(given_date_obj))
            modified_date = given_date_obj + timedelta(days=self.emergency_date)
            print('modified', str(modified_date))

            customer_ref.update({
                'has_due': True,
                'emergency_date': self.emergency_date,
                'emergency_balance_due_amount': 0,
                'active_status': 'active',
                'emergency_due_date': modified_date.strftime(DEFAULT_DATE_FORMAT),

            })
            modified_date = modified_date + timedelta(hours=6)
            status = update_expiry_bandwidth(customer_ref.subscriber_id,
                                             modified_date.strftime(DEFAULT_DATE_FORMAT),
                                             customer_ref.current_package_id.name)
            print('status', status)

        return {
            'name': 'Customer Dashboard',
            'view_mode': 'form',
             'view_type':'form',
            'views': [(form_view_id, 'form')],
            'res_model': 'emergency.wizard.balance',
            'type': 'ir.actions.act_window',
            'target': 'inline',
        }