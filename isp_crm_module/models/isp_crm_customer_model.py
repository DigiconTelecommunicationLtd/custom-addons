# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime


GENDERS = [
    ('male', _('Male')),
    ('female', _('Female')),
    ('others', _('Others')),
]


class Customer(models.Model):
    """Inherits res.partner and adds Customer info in partner form"""
    _inherit = 'res.partner'

    subscriber_id = fields.Char('Subcriber ID', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    father = fields.Char("Father's Name", default='', required=False,)
    mother = fields.Char(string="Mother's Name", required=False, default='')
    birthday = fields.Date('Date of Birth', required=False, default=None)
    gender = fields.Selection(GENDERS, string='Gender', required=False, help="Gender of the Subscriber", default='')
    identifier_name = fields.Char(string="Identifier's Name", required=False, default='')
    identifier_phone = fields.Char(string="Identifier's Telephone", required=False, default='')
    identifier_mobile = fields.Char(string="Identifier's Mobile", required=False, default='')
    identifier_nid = fields.Char(string="Identifier's NID", required=False, default=False)
    service_type = fields.Many2one('isp_crm.service_type', default=False, required=False, string='Service Type')
    connection_type = fields.Many2one('isp_crm.connection_type', default=False, required=False, string='Connection Type')
    connection_media = fields.Many2one('isp_crm.connection_media', default=False, required=False, string='Connection Media' )
    connection_status = fields.Boolean(string='Connection Up', default=False, required=False)
    bill_cycle_date = fields.Date(string='Bill Cycle Date', required=False, default=None)

    @api.model
    def create(self, vals):
        if vals.get('subscriber_id', 'New') == 'New':
            vals['subscriber_id'] = self.env['ir.sequence'].next_by_code('isp_crm.subscriber_id') or '/'
        return super(Customer, self).create(vals)