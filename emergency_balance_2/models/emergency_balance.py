# -*- coding: utf-8 -*-

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
class emergency_balance(models.Model):
     _name = 'emergency.balance'
     _rec_name = 'name'
     name = fields.Char(string='name',track_visibility='onchange',default="")
     has_due = fields.Boolean(string='due?',
                              track_visibility='onchange',default=False)

     set_for_approval = fields.Boolean(string='approval needed?',
                                       track_visibility='onchange',default=False)

     approved = fields.Boolean(string='approved?',
                               track_visibility='onchange',default=False)
     rejected = fields.Boolean(string='rejected?',
                               track_visibility='onchange',default=False)

     approved_by=fields.Many2one('res.users', string='Approved By', track_visibility='onchange',default=False)
     rejected_by = fields.Many2one('res.users', string='Rejected By', track_visibility='onchange', default=False)

     disable_header = fields.Boolean(string='header?', default=False)

     due_paid = fields.Boolean(string='paid?', default=False, track_visibility='onchange')


     customer = fields.Many2one('res.partner', String='Customer',track_visibility='onchange',
                                domain=[('subscriber_id', '!=', 'New'), ('subscriber_id', 'like', 'MR')])
     emergency_date = fields.Selection(EMERGENCY_TYPE, string='Emergency Balance', help="Emergency Balance",
                                       required=True,track_visibility='onchange')
     due_amount = fields.Float('Due Amount', required=True,
                               default=0.0,
                               track_visibility='onchange')

     color = fields.Integer(default=1)

     subscriber_id =fields.Char(compute='change_emergency_date',string='Subscriber ID')
     current_package = fields.Char(compute='change_emergency_date',string='Current Package')
     current_package_price = fields.Char(compute='change_emergency_date', string='Current Package Price')
     current_package_end_date = fields.Char(compute='change_emergency_date', string='Valid Till')
     next_package_start_date = fields.Char(compute='change_emergency_date',string='Next Start Date')
     assigned_rm = fields.Char(compute='change_emergency_date',string='Assigned RM')

     state = fields.Selection([
         ('approval', 'Waiting for Approval'),
         ('due', 'Due Accepted'),
         ('paid', 'Due Paid'),
         ('rejected', 'Due Request Rejected'),
     ], default='due')

     @api.onchange('state')
     def stage_onchange(self):

         raise UserError('System does not allow you to drag record unless mark done is confirmed by action.')


     @api.one
     @api.onchange('customer')
     def change_emergency_date(self):
         for records in self:
             records.current_package = str(self.customer.current_package_id.name)
             records.current_package_price = str(self.customer.current_package_price)
             records.current_package_end_date =str(self.customer.current_package_end_date)
             records.next_package_start_date = str(self.customer.next_package_start_date)
             records.assigned_rm = str(self.customer.assigned_rm.name)
             records.subscriber_id = str(self.customer.subscriber_id)


         #self.current_balance=str(customer.get_customer_balance(str(self.customer.subscriber_id)))
         #print(str(self.customer.current_package_id.name))
         #print(str(self.customer.current_package_price))
         #print(str(self.customer.current_package_end_date))
         #print(str(self.customer.next_package_start_date))
         #print(str(self.customer.assigned_rm.name))

     # @api.model
     # def create(self, vals):
     #     print(vals)
     #     res = super(emergency_balance, self).create(vals)
     #     data = self.env['emergency.balance'].sudo().search([('customer', '=', vals['customer']),('has_due','=','true')], limit=1)
     #     data2 = self.env['emergency.balance'].sudo().search([('customer', '=', vals['customer']), ('set_for_approval', '=', 'true')], limit=1)
     #     print(data)
     #     if data:
     #         raise UserError('A ticket is already raised and emergency balance is already given')
     #         print('raised has due')
     #     print(data2)
     #     if data2:
     #         raise UserError('A ticket is already raised and pending for approval')
     #         print('raised has approval')
     #
     #     update_data = self.env['emergency.balance'].sudo().search(
     #         [('customer', '=', vals['customer'])], limit=1)
     #
     #     customer_ref = self.env['res.partner'].sudo().search([('id', '=', vals['customer'])], limit=1)
     #     #if greater than two days need approval
     #     if vals['emergency_date'] > 2:
     #         update_data.update({
     #             'approved':False,
     #             'has_due':False,
     #             'set_for_approval':True,
     #             'approved_by': self.env.uid,
     #             'emergency_date':vals['emergency_date']
     #         })
     #
     #         # self.approved = False
     #         # self.has_due = False
     #         # self.set_for_approval = True
     #     else:
     #         update_data.update({
     #             'approved': True,
     #             'has_due': True,
     #             'set_for_approval': False,
     #             'emergency_date': vals['emergency_date']
     #         })
     #         print('customer_red',customer_ref)
     #         print('current_package_end_date',customer_ref.current_package_end_date)
     #         given_date_obj = datetime.strptime(customer_ref.current_package_end_date, DEFAULT_DATE_FORMAT)
     #         print('given_date', str(given_date_obj))
     #         modified_date = given_date_obj + timedelta(days=vals['emergency_date'])
     #         print('modified', str(modified_date))
     #
     #         customer_ref.update({
     #             'has_due': True,
     #             'emergency_date': vals['emergency_date'],
     #             'emergency_balance_due_amount': 0,
     #             'emergency_due_date':modified_date.strftime(DEFAULT_DATE_FORMAT),
     #
     #         })
     #         status=update_expiry_bandwidth(customer_ref.subscriber_id,
     #                                 modified_date.strftime(DEFAULT_DATE_FORMAT), customer_ref.current_package_id.name)
     #         print('status',status)
     #     return res


     @api.one
     def on_emergency_approve(self):
         for record in self:
             record.approved = True
             record.has_due = True
             record.set_for_approval = False

             record.customer.has_due = True
             record.customer.emergency_date = record.emergency_date
             record.approved_by = self.env.uid
             record.disable_header = True
             record.state = 'due'
             record.color = DUE_ACCEPTED

             print('current_package_end_date', record.customer.current_package_end_date)

             #if the user is active then given date is current package end date else its today plus 6 hours
             given_date_obj = None
             if record.customer.active_status == CUSTOMER_INACTIVE_STATUS:
                 today_new = datetime.now() + timedelta(hours=6)
                 #today = today_new.date()
                 given_date_obj = today_new.date()

             else:
                 given_date_obj = datetime.strptime(record.customer.current_package_end_date, DEFAULT_DATE_FORMAT)

             print('given_date', str(given_date_obj))
             modified_date = given_date_obj + timedelta(days=record.emergency_date)
             print('modified', str(modified_date))

             record.customer.emergency_due_date = modified_date.strftime(DEFAULT_DATE_FORMAT)
             current_unit_price=(record.customer.current_package_price)/30
             due_amount = current_unit_price * (record.emergency_date - 2)
             record.customer.emergency_balance_due_amount = due_amount

             modified_date = modified_date + timedelta(hours=6)
             status = update_expiry_bandwidth(record.customer.subscriber_id,
                                              modified_date.strftime(DEFAULT_DATE_FORMAT),
                                              record.customer.current_package_id.name)
             # print('status', status)

     @api.one
     def on_emergency_reject(self):
         for record in self:
            record.approved = False
            record.has_due = False
            record.set_for_approval = False
            record.rejected=True
            record.rejected_by = self.env.uid
            record.disable_header = True
            record.state = 'rejected'
            record.color = DUE_REJECTED