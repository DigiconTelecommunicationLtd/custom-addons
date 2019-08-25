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
            'is_mark_lost': True,
            'stage': mark_lost_stage.id,
            # 'mark_done_date': datetime.today()
        })


        leads.write({
            'color': 9,
            'lost_reason': mark_lost_stage.id,
            'current_service_request_status': MARK_LOST_STATUS,
            'is_service_request_created': False
        })
        leads.write({'lost_reason': mark_lost_stage.id})
        # # checks for invoices
        # invoice = self.env['account.invoice'].search([('partner_id', '=', service_request.customer.id)], limit=1)

        # the invoice is canceled -> membership state of the customer goes to canceled
        # invoice.action_invoice_cancel()

        #send email
        # 'email_to': ", ".join(recipients)
        template_obj = self.env['mail.mail']
        template_data = {
            'subject': 'Mark Lost : ' + service_request.problem,
            'body_html': "<h1> Lead Lost. Please cancel the invoice manually </h1>",
            'email_from': 'notice.mime@cg-bd.com',
            'email_cc': '',
            'email_to': 'ripon.kumar@cg-bd.com'
        }
        template_id = template_obj.create(template_data).send()
        #if we want to put some duration
        #template_obj.send(template_id)



        return leads.action_set_lost()
