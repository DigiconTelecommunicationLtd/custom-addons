# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

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

    def send_reset_password_link_email(self, user, mailto, template_obj):
        random_number = self.env['isp_crm_module.temporary_links'].randomString(10)
        link = "http://10.10.16.6:8069/selfcare/reset/password/"+str(random_number)
        temporary_link = self.env['isp_crm_module.temporary_links'].sudo().create({

            'name': user.id,
            'link': link
        })
        if temporary_link:
            body = template_obj.body_html
            body = body.replace('--passowrd-reset-link--', link)
            if template_obj:
                mail_values={
                    'subject': template_obj.subject,
                    'body_html': body,
                    'email_to': mailto,
                    'email_from': 'mime@cgbd.com',
                }
                create_and_send_email = self.env['mail.mail'].sudo().create(mail_values).send()
            return True
        else:
            raise UserError('Could not create temporary link to reset password.')


    def sending_mail_for_payment(self, payment_obj, template_obj):
        body = template_obj.body_html
        body = body.replace('--date--', str(payment_obj.create_date))
        body = body.replace('--subscriber_id--', str(payment_obj.partner_id.subscriber_id))
        body = body.replace('--name--', str(payment_obj.partner_id.name))
        body = body.replace('--address--', str(payment_obj.partner_id.get_partner_address_str()))
        body = body.replace('--email--', str(payment_obj.partner_id.email))
        body = body.replace('--mobile--', str(payment_obj.partner_id.mobile))
        body = body.replace('--payment_service_type--', str(payment_obj.service_type_id.name))
        body = body.replace('--payment_amount--', str(payment_obj.amount))
        body = body.replace('--payment_journal_name--', str(payment_obj.journal_id.name))
        body = body.replace('--card_type--', str(payment_obj.card_type) if payment_obj.card_type else "" )
        body = body.replace('--card_number--', str(payment_obj.card_number) if payment_obj.card_number else "")
        body = body.replace('--transaction_ammount--', str(payment_obj.bill_amount) if payment_obj.bill_amount else "")

        if template_obj:
            mail_values = {
                'subject': template_obj.subject,
                'body_html': body,
                'email_to': payment_obj.partner_id.email,
                'email_from': 'notice.mime@cg-bd.com',
            }
            try:
                create_and_send_email = self.env['mail.mail'].sudo().create(mail_values).send()
            except Exception as ex:
                print(ex)
            return True
        else:
            raise UserError('Could Not send the mail.')



