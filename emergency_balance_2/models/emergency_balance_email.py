
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Team(models.Model):
    DEFAULT_FROM_MAIL = 'notice.mime@cg-bd.com'

    _name = 'emergency_balance.mail'
    _rec_name = 'name'
    _order = "name, id"

    name = fields.Char('Mail Name', translate=True)
    body_html = fields.Text('Mail Body')

    @api.multi
    def action_send_email(self, days,name,subid,package,price,template_obj):
        body = template_obj.body_html
        body = body.replace('--emergencydays--', days)
        body = body.replace('--customername--', name)
        body = body.replace('--customerid--', subid)
        body = body.replace('--packagename--', package)
        body = body.replace('--packageprice--', price)
        if template_obj:
            mail_values = {
                'subject': 'Emergency Balance Approval Request',
                'body_html': body,
                'email_to': 'hod.mime@cg-bd.com',
                'email_cc': '',
                'email_from': self.DEFAULT_FROM_MAIL,
            }
            create_and_send_email = self.env['mail.mail'].create(mail_values).send()

        # return True