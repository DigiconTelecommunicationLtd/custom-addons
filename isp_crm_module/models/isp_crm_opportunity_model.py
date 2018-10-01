# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import re
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from . import isp_crm_service_request_model


DEFAULT_PROBLEM = "There are some Problem"

class Opportunity(models.Model):
    _inherit = 'crm.lead'
    _description = "Team of ISP CRM Opportunity."

    opportunity_seq_id = fields.Char('ID', required=True, index=True, copy=False, default='New', readonly=True)
    current_service_request_id = fields.Char(string='Service Request ID', readonly=True, required=False)
    current_service_request_status = fields.Char(string='Service Request ID', readonly=True, required=False)
    is_service_request_created = fields.Boolean("Is Service Request Created", default=False)

    @api.multi
    def action_set_won(self):
        for lead in self:
            # TODO Arif: `invoice_status` will be added later. Now checking status will be `confirm_sale`
            sale_confirmed = False
            for order in lead.order_ids:
                if order.state == 'sale':
                    sale_confirmed = True
                    break
            if not sale_confirmed:
                raise UserError(_("This Opportunity's Sale has not been confirmed.\n Confirm Sale First."))
            else:
                super(Opportunity, lead).action_set_won()
        return True

    @api.onchange('email_from')
    def onchange_email(self):
        if self.email_from:
            if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", self.email_from) == None:
                raise UserError(_('Please Enter a Valid Email Address!'))

    @api.onchange('mobile')
    def onchange_mobile(self):
        if self.mobile:
            if re.match("^([0-9]+-)*[0-9]+$", self.mobile) == None:
                raise UserError(_('Please Enter a Valid Mobile Number!'))

    @api.onchange('phone')
    def onchange_phone(self):
        if self.phone:
            if re.match("^([0-9]+-)*[0-9]+$", self.phone) == None:
                raise UserError(_('Please Enter a Valid Phone Number!'))

    @api.model
    def create(self, vals):
        if vals.get('opportunity_seq_id', 'New') == 'New':
            sequence_id = self.env['ir.sequence'].next_by_code('crm.lead') or '/'
            vals['opportunity_seq_id'] = sequence_id

        if (not vals.get('email_from')) and (not vals.get('phone')) and (not vals.get('mobile')):
            raise Warning(_('Please Provide any of this Email, Phone or Mobile'))

        return super(Opportunity, self).create(vals)

    @api.multi
    def action_create_new_service_request(self):
        res = {}
        for opportunity in self:
            first_stage = self.env['isp_crm_module.stage'].search([('name', '=', 'New'),], order="sequence asc")[0]
            service_req_obj = self.env['isp_crm_module.service_request'].search([])

            service_req_data = {
                'problem' : opportunity.description or DEFAULT_PROBLEM,
                'stage' : first_stage.id,
                'customer' : opportunity.partner_id.id,
                'customer_email' : opportunity.partner_id.email,
                'customer_mobile' : opportunity.partner_id.mobile,
                'opportunity_id' : opportunity.id,
            }
            created_service_req_obj = service_req_obj.create(service_req_data)
            opportunity.update({
                'color' : 2,
                'current_service_request_id' : created_service_req_obj.name,
                'current_service_request_status' : 'Processing',
                'is_service_request_created' : True
            })
        return True



