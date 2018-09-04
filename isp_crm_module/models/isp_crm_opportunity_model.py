# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class Opportunity(models.Model):
    _inherit = 'crm.lead'
    _description = "Team of ISP CRM Opportunity."

    opportunity_seq_id = fields.Char('Opportunity ID', required=True, index=True, copy=False, default='New', readonly=True)
    is_service_request_created = fields.Boolean("Is Service Request Created", default=False)

    @api.model
    def create(self, vals):
        if vals.get('opportunity_seq_id', 'New') == 'New':
            vals['opportunity_seq_id'] = self.env['ir.sequence'].next_by_code('crm.lead') or '/'
        return super(Opportunity, self).create(vals)

    @api.multi
    def action_create_new_service_request(self):
        res = {}
        for opportunity in self:
            first_stage = self.env['isp_crm_module.stage'].search([], order="sequence asc")[0]
            service_req_obj = self.env['isp_crm_module.service_request'].search([])

            service_req_data = {
                'problem' : opportunity.name,
                'stage' : first_stage.id,
                'customer' : opportunity.partner_id.id,
                'customer_email' : opportunity.partner_id.email,
                'customer_mobile' : opportunity.partner_id.mobile,
            }
            service_req_obj.create(service_req_data)
            opportunity.update({
                'is_service_request_created' : True
            })
        return True


