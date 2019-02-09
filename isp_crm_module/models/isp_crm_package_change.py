# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import timedelta, datetime


class ChangePackage(models.Model):
    """
    Model for Package Change.
    """
    _name = "isp_crm_module.change_package"
    _description = "Package change prompt."
    _order = "create_date desc, id"

    STATES = [
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('validated', 'Validated'),
        ('canceled', 'Canceled'),
    ]


    def _tomorrow_date(self):
        return fields.Date.today()

    name = fields.Char(string="Ticket ID (reference)", required=False,)
    ticket_ref = fields.Char(string="Ticket ID (reference)", required=True)
    customer_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)])
    from_package_id = fields.Many2one('product.product', string='From Package', domain=[('sale_ok', '=', True)],
                                         change_default=True, ondelete='restrict')
    to_package_id = fields.Many2one('product.product', string='Change To Package', domain=[('sale_ok', '=', True)],
                                      change_default=True, ondelete='restrict')
    active_from = fields.Date('Will Active From', default=_tomorrow_date)
    validated_by_id = fields.Many2one('res.users', string='Validated By', index=True, track_visibility='onchange')
    canceled_by_id = fields.Many2one('res.users', string='Canceled By', index=True, track_visibility='onchange')
    state = fields.Selection(STATES, string="State", default='draft')
    customer_balance = fields.Float(string="Customer Balance", compute="_get_customer_balance")
    is_paid = fields.Boolean("Is Paid", default=False)

    @api.multi
    def action_make_package_change_validated(self):
        for pack_change_obj in self:
            active_from_date_obj =  datetime.strptime(pack_change_obj.active_from, "%Y-%m-%d")
            valid_till_date_obj = active_from_date_obj - timedelta(days=1)
            valid_till_date_str = valid_till_date_obj.strftime('%Y-%m-%d')
            pack_change_obj.customer_id.update({
                'next_package_id' : pack_change_obj.to_package_id.id,
                'next_package_start_date' : pack_change_obj.active_from,
                'next_package_price' : pack_change_obj.to_package_id.lst_price,
                'next_package_original_price' : pack_change_obj.to_package_id.lst_price,
                'is_sent_package_change_req' : True,
            })
            pack_change_obj.update({
                'validated_by_id' : self.env.user.id,
                'state' : 'validated',

            })
        return True

    @api.multi
    def action_make_package_change_canceled(self):
        for pack_change_obj in self:
            pack_change_obj.canceled_by_id = self.env.user
            pack_change_obj.state = 'canceled'
        return True

    @api.multi
    @api.depends('customer_id')
    def _get_customer_balance(self):
        for rec in self:
            balance = rec.customer_id.get_customer_balance(customer_id=rec.customer_id.id)
            rec.customer_balance = abs(balance) if balance < 0 else 0.0
            if rec.customer_balance > rec.to_package_id.price:
                new_balance = rec.customer_balance - rec.to_package_id.price
                rec.write({
                    'is_paid' : True,
                    'customer_balance' : float(new_balance)
                })

        return True

    def send_package_change_mail(self):
        """
        Sends mail for changing package
        :return: True if the changing package mailing is successfull
        """
        template_obj = self.env['mail.template'].search([('name', '=', 'isp_crm_module_user_package_change_mail_template')])
        for record in self:
            mail_obj = self.env['isp_crm_module.mail'].sending_mail_for_package_change_request(package_change_obj=record,
                                                                                template_obj=template_obj)