# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


GENDERS = [
    ('male', _('Male')),
    ('female', _('Female')),
    ('others', _('Others')),
]



class Customer(models.Model):
    """Inherits res.partner and adds Customer info in partner form"""
    _inherit = 'res.partner'

    subscriber_id = fields.Char('Subcriber ID', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    father = fields.Char("Father's Name")
    mother = fields.Char(string="Mother's Name")
    birthday = fields.Date('Date of Birth')
    gender = fields.Selection(GENDERS, string='Gender', help="Gender of the Subscriber")
    identifier_name = fields.Char(string="Identifier's Name")
    identifier_phone = fields.Char(string="Identifier's Telephone")
    identifier_mobile = fields.Char(string="Identifier's Mobile")
    identifier_nid = fields.Char(string="Identifier's NID")
    service_type = fields.Many2one('isp_crm.service_type', string='Service Type')
    connection_type = fields.Many2one('isp_crm.connection_type', string='Connection Type')
    connection_media = fields.Many2one('isp_crm.connection_media', string='Connection Media')

    @api.model
    def create(self, vals):
        if vals.get('subscriber_id', 'New') == 'New':
            vals['subscriber_id'] = self.env['ir.sequence'].next_by_code('isp_crm.subscriber_id') or '/'
        return super(Customer, self).create(vals)

    @api.model
    def save(self, vals):
        if vals.get('subscriber_id', 'New') == 'New':
            vals['subscriber_id'] = self.env['ir.sequence'].next_by_code('isp_crm.subscriber_id') or '/'
        return super(Customer, self).save(vals)
