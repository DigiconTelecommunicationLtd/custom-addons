# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import Warning, UserError
from datetime import datetime, timezone, timedelta, date
from odoo.addons.isp_crm_module.models.radius_integration import *
from odoo.addons.emergency_balance_2.models.color_code import *


class RealIpChangeRequest(models.Model):
    _name = 'real_ip.change_request'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(string='name', track_visibility='onchange', default="")

    color = fields.Integer(default=1)
    customer = fields.Many2one('res.partner', String='Customer', track_visibility='onchange',default=False,
                               domain=[('subscriber_id', '!=', 'New'), ('subscriber_id', 'like', 'MR')])

    real_ip_filter = fields.Boolean(default=True)

    real_ip = fields.Char(string='Real IP')
    proposed_date = fields.Date(string="Proposed Date")

    approved = fields.Boolean(string='approved?',
                              track_visibility='onchange', default=False)
    rejected = fields.Boolean(string='rejected?',
                              track_visibility='onchange', default=False)

    approved_by = fields.Many2one('res.users', string='Approved By', track_visibility='onchange', default=False)
    rejected_by = fields.Many2one('res.users', string='Rejected By', track_visibility='onchange', default=False)
    state = fields.Selection([
        ('create', 'Create'),
        ('new', 'New request'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ],default='create')
    service_type = fields.Selection([
        ('assign', 'Assign Real IP'),
        ('remove', 'Remove Real IP'),
    ])

    @api.onchange('service_type')
    def service_type_change(self):
        for record in self:
            if record.service_type == 'remove':
                record.real_ip_filter = True
            elif record.service_type == False:
                record.real_ip_filter = True
            else:
                record.real_ip_filter = False
            print(record.real_ip_filter)


    @api.onchange('state')
    def stage_onchange(self):
        for record in self:
            if record.state == 'approved':
                raise UserError('System does not allow you to drag record')
            if record.state == 'rejected':
                raise UserError('System does not allow you to drag record')


    @api.onchange('customer')
    def customer_onchange(self):
        for record in self:
            record.proposed_date = record.customer.current_package_end_date

    @api.one
    def on_ip_approve(self):
        for record in self:
            if record.service_type == 'assign':
                record.state = 'approved'
                record.approved_by = self.env.uid
                record.customer.real_ip=record.real_ip
                record.customer.has_real_ip = True
                record.customer.real_ip_subtotal=1.0
                record.customer.reaL_ip_original=1.0

                real_ip=self.env['product.product'].sudo().search([('name', '=', 'Real IP')])

                customer_product_line_obj = self.env['isp_crm_module.customer_product_line']
                customer_product_line_obj.sudo().create({
                    'customer_id': record.customer.id,
                    'name': real_ip.name,
                    'product_id': real_ip.id,
                    'product_uom_qty': 1,
                    'price_unit': real_ip.lst_price,
                    'price_subtotal': real_ip.lst_price,
                    'price_total': real_ip.lst_price,
                })
                # created_product_line_list.append(created_product_line.id)
                # record.customer.sudo().update({
                #     'product_line': [(6, None, created_product_line_list)]
                # })
                # result=[]
                for line in record.customer.product_line:
                    print(line)

                # result.append((0,0,real_ip))




            elif record.service_type == 'remove':
                record.state = 'approved'
                record.approved_by = self.env.uid
                record.customer.real_ip = False
                record.customer.has_real_ip = False
                record.customer.real_ip_subtotal = 0.0
                record.customer.reaL_ip_original = 0.0
                result=[]
                for line in record.customer.product_line:
                    if line.name !='Real IP':
                        result.append(line.id)

                record.customer.product_line=[(6,None,result)]

    @api.one
    def on_ip_rejected(self):
        for record in self:
            record.state = 'rejected'
            record.rejected_by = self.env.uid

    @api.model
    def create(self, values):
        values['state']='new'
        return super(RealIpChangeRequest, self).create(values)
