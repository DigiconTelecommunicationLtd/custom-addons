# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

class Team(models.Model):
    _name = 'isp_crm_module.mail'
    _description = "ISP CRM Mail Module"
    _rec_name = 'name'
    _order = "name, id"


    name = fields.Char('Mail Name', translate=True)
    body_html = fields.Text('Mail Body')

    @api.multi
    def action_send_email(self, subject, mailto, ticketnumber, template_obj):
        body = template_obj.body_html
        body = body.replace('--ticketnumber--', ticketnumber)
        if template_obj:
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': mailto,
                'email_cc': '',
                'email_from': 'mime@cgbd.com',
            }
            create_and_send_email = self.env['mail.mail'].create(mail_values).send()

        return True

    @api.multi
    def action_td_send_email(self, subject, mailto, ticketnumber, template_obj, hour):
        body = template_obj.body_html
        body = body.replace('--ticketnumber--', ticketnumber)
        body = body.replace('--hour--', hour)
        if template_obj:
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': mailto,
                'email_cc': '',
                'email_from': 'mime@cgbd.com',
            }
            create_and_send_email = self.env['mail.mail'].create(mail_values).send()

        return True

    def service_request_send_email(self, mailto,userid,password,ip,subnet_mask,gateway,template_obj,attachment):
        body = template_obj.body_html
        body = body.replace('--userid--', userid)
        body = body.replace('--password--', password)
        body = body.replace('--ip--', str(ip))
        body = body.replace('--subnetmask--', str(subnet_mask))
        body = body.replace('--gateWay--', str(gateway))
        if template_obj:
            mail_values = {
                'subject': template_obj.subject,
                'body_html': body,
                'email_to': mailto,
                'email_from': 'mime@cgbd.com',
                # 'attachment_ids': [(6, 0, [attachment.id])],
            }
            create_and_send_email = self.env['mail.mail'].create(mail_values).send()

        return True


