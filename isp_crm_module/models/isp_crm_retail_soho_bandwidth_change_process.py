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
    _name = "isp_crm_module.retail_soho_bandwidth_change"
    _description = "Retail SOHO Bandwidth Change Request."
    _order = "create_date desc, id"
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'format.address.mixin']

    name = fields.Char('Request Name', index=True, copy=False, default='New')
    problem = fields.Char(string="Problem",help='Ticket Problem.')
    description = fields.Text('Description')
    default_stages = fields.Selection(AVAILABLE_STAGES, string="Stages",group_expand='_default_stages')
    customer = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True), ('opportunity_ids.lead_type', '!=', 'corporate')],
                               track_visibility='onchange')
    customer_id = fields.Char(related='customer.subscriber_id', help='Customer ID.')
    current_package = fields.Many2one(related='customer.current_package_id', help='Current Package.')
    proposed_new_package = fields.Many2one('product.product', string='Proposed New Package', domain=[('sale_ok', '=', True)],
                                         change_default=True, ondelete='restrict', track_visibility='onchange')
    quantity = fields.Integer(string='Quantity', required=False, default=0, track_visibility='onchange')
    proposed_package_price = fields.Float(related='proposed_new_package.lst_price', required=True,
                                         digits=dp.get_precision('Product Price'), default=0.0, track_visibility='onchange')
    proposed_activation_date = fields.Date(string="Proposed Activation Date", default=None)
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
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.retail_soho_bandwidth_change') or '/'
            vals['default_stages'] = 'New'
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.retail_soho_bandwidth_change') or '/'
            vals['default_stages'] = 'New'

        newrecord = super(RetailSohoBandwidthChange, self).create(vals)

        return newrecord

    def _default_stages(self, stages, domain, order):
        stage_ids = self._fields['default_stages'].get_values(self.env)
        return stage_ids

    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.quantity > 0 and self.proposed_new_package:
            proposed_package_price = self.proposed_new_package.lst_price * self.quantity
            self.write({
                'proposed_package_price': proposed_package_price
            })

    @api.onchange('proposed_new_package')
    def _onchange_proposed_package_price(self):
        if self.quantity > 0 and self.proposed_new_package:
            proposed_package_price = self.proposed_new_package.lst_price * self.quantity
            self.write({
                'proposed_package_price': proposed_package_price
            })