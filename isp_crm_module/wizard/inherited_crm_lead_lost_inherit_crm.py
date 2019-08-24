# -*- coding: utf-8 -*-

from odoo import api, fields, models
MARK_LOST_STATUS = 'Mark Lost'

class InheritedCrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'
    _description = 'Get Lost Reason'

    @api.multi
    def action_inherit_lost_reason_apply(self):
        # customer = self.customer.id
        #
        # print("########", customer)
        # mark_lost = self.env['isp_crm_module.stage'].search([('name', '=', 'Mark Lost')], limit=1)

        # service_request = self.env['isp_crm_module.service_request'].search([('name', '=', 'REQ1903040056')], limit=1)
        # service_request = self.env['isp_crm_module.service_request'].search([('name', '=', 'REQ1903040056')], limit=1)
        service_request = self.env['isp_crm_module.service_request'].browse(self.env.context['active_id'])
        mark_lost_stage = self.env['isp_crm_module.stage'].search([('name', '=', 'Mark Lost')], limit=1)

        leads = self.env['crm.lead'].search([('current_service_request_id', '=', service_request.name)], limit=1)
        #change state to mark lost
        service_request.update({
            'is_done': False,
            'stage': mark_lost_stage.id,
            # 'mark_done_date': datetime.today()
        })

        # leads1 = self.env['crm.lead'].browse(mark_lost_stage.name)



        # leads.write({'lost_reason': self.lost_reason_id.id})
        leads.write({
            'color': 9,
            'lost_reason': mark_lost_stage.id,
            'current_service_request_status': MARK_LOST_STATUS,
            'is_service_request_created': False
        })
        leads.write({'lost_reason': mark_lost_stage.id})
        # # checks for invoices
        invoice = self.env['account.invoice'].search([('partner_id', '=', service_request.customer.id)], limit=1)

        # the invoice is canceled -> membership state of the customer goes to canceled
        invoice.action_invoice_cancel()

        return leads.action_set_lost()
