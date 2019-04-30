# -*- coding: utf-8 -*-

import string
import random
from datetime import datetime, timedelta
import logging
from passlib.context import CryptContext
from odoo import http
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning, UserError
from odoo.tools import email_split
import base64
import ctypes

DEFAULT_DATE_FORMAT = '%Y-%m-%d'

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
    ('Done', 'Done'),
]

class RetailSohoBandwidthChange(models.Model):
    """
    Model for different type of service_requests.
    """
    _name = "isp_crm_module.corporate_bandwidth_change"
    _description = "Corporate SOHO Bandwidth Change Request."
    _order = "create_date desc, id"
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']

    name = fields.Char('Request Name', index=True, copy=False, default='New')
    problem = fields.Char(string="Problem",help='Ticket Problem.')
    ticket_ref = fields.Char(string="Ticket ID (reference)", default='New')
    description = fields.Text('Description')
    default_stages = fields.Selection(AVAILABLE_STAGES, string="Stages",group_expand='_default_stages')
    customer = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True), ('opportunity_ids.lead_type', '!=', 'retail')],
                               track_visibility='onchange', required=True)
    customer_id = fields.Char(related='customer.subscriber_id', help='Customer ID.')
    current_package = fields.Many2one(related='customer.current_package_id', help='Current Package.', required=True)
    proposed_new_package = fields.Many2one('product.product', string='Proposed New Package', domain=[('sale_ok', '=', True), ('default_code', '=', 'Corporate')],
                                         change_default=True, ondelete='restrict', track_visibility='onchange', required=True)
    bandwidth = fields.Float(string='Current Bandwidth', required=True, track_visibility='onchange')
    proposed_package_price = fields.Float(related='proposed_new_package.lst_price', digits=dp.get_precision('Product Price'), default=0.0, track_visibility='onchange', required=True)
    proposed_activation_date = fields.Date(string="Proposed Activation Date", default=None, required=True)
    customer_email = fields.Char(related='customer.email', store=True)
    customer_mobile = fields.Char(string="Mobile", related='customer.mobile', store=True)
    customer_phone = fields.Char(string="Phone", related='customer.phone', store=True)
    customer_company = fields.Char(string="Company", related='customer.parent_id.name', store=True)
    customer_address = fields.Char(string="Address", track_visibility='onchange')
    customer_type = fields.Selection(related='customer.opportunity_ids.lead_type', string='Customer Type')
    priority = fields.Selection(AVAILABLE_PRIORITIES, string="Priority")
    customer_rating = fields.Selection(AVAILABLE_RATINGS, string="Rating")
    customer_feedback = fields.Text('Feedback')
    color = fields.Integer(default=1)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.corporate_bandwidth_change') or '/'
            ticket_id = self.env['ir.sequence'].next_by_code(
                'isp_crm_module.corporate_bandwidth_change') or '/'
            vals['ticket_ref'] = ticket_id
            vals['default_stages'] = 'New'
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.corporate_bandwidth_change') or '/'
            ticket_id = self.env['ir.sequence'].next_by_code(
                'isp_crm_module.corporate_bandwidth_change') or '/'
            vals['ticket_ref'] = ticket_id
            vals['default_stages'] = 'New'

        newrecord = super(RetailSohoBandwidthChange, self).create(vals)
        template_obj = self.env['mail.template'].search(
            [('name', '=', 'isp_crm_module_user_package_change_mail_template')])
        mail_obj = self.env['isp_crm_module.mail'].sending_mail_for_package_change_request(
            package_change_obj=newrecord,
            template_obj=template_obj)
        return newrecord

    def _default_stages(self, stages, domain, order):
        stage_ids = self._fields['default_stages'].get_values(self.env)
        return stage_ids

    # @api.onchange('quantity')
    # def _onchange_quantity(self):
    #     if self.quantity > 1 and self.proposed_new_package:
    #         proposed_package_price = self.proposed_new_package.lst_price * self.quantity
    #         self.write({
    #             'proposed_package_price': proposed_package_price
    #         })
    #
    # @api.onchange('proposed_new_package')
    # def _onchange_proposed_package_price(self):
    #     if self.quantity > 1 and self.proposed_new_package:
    #         proposed_package_price = self.proposed_new_package.lst_price * self.quantity
    #         self.write({
    #             'proposed_package_price': proposed_package_price
    #         })

    @api.onchange('default_stages')
    def _onchange_default_stages(self):
        tomorrow = date.today() + timedelta(days=1)
        if self.default_stages != 'Done':
            raise UserError('System does not allow you to change stage after Mark Done. ')
        if self.default_stages == 'Done':
            if self.color == 1:
                raise UserError('You can not drag the ticket to Done stage unless customer payment is done.')
            if self.proposed_activation_date >= tomorrow:
                raise UserError('Proposed activation date is over. Please set a new date.')
        else:
            self.write({
                'color': 7,
            })
