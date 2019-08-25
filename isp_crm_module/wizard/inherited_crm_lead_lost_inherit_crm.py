# -*- coding: utf-8 -*-

from odoo import api, fields, models
MARK_LOST_STATUS = 'Mark Lost'

class InheritedCrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'
    _description = 'Get Lost Reason'
    # lost_reason=fields.Char('Lost Reason', size=100)

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
        rm = service_request.customer_rm.login if service_request.customer_rm  else ''

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
        mail_body = "<p>Service Request REQXX has been lost due to </p>" +"<h5> "+ self.lost_reason_id.name +" </h5>"+ " <p>Please cancel it’s invoice and other accounting entries accordingly</p>"
        # mail_body+= self.lost_reason_id.name
        # mail_body+="<h5>Please cancel it’s invoice and other accounting entries accordingly</h5>"
        template_data = {
            'subject': ' Service Delivery failed: ' + service_request.problem,
            'body_html': mail_body,
            'email_from': 'notice.mime@cg-bd.com',
            'email_cc': rm,
            'email_to': 'hod.mime@cg-bd.com'
        }
        template_id = template_obj.create(template_data).send()
        #if we want to put some duration
        #template_obj.send(template_id)

        return leads.action_set_lost()
