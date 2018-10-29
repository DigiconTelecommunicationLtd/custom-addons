# -*- coding: utf-8 -*-



from ast import literal_eval
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import Warning, UserError
import re
import odoo.addons.decimal_precision as dp

GENDERS = [
    ('male', _('Male')),
    ('female', _('Female')),
    ('others', _('Others')),
]


class Customer(models.Model):
    """Inherits res.partner and adds Customer info in partner form"""
    _inherit = 'res.partner'

    subscriber_id = fields.Char('Subcriber ID', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    father = fields.Char("Father's Name", default='', required=False,)
    mother = fields.Char(string="Mother's Name", required=False, default='')
    birthday = fields.Date('Date of Birth', required=False, default=None)
    gender = fields.Selection(GENDERS, string='Gender', required=False, help="Gender of the Subscriber", default='')
    identifier_name = fields.Char(string="Identifier's Name", required=False, default='')
    identifier_phone = fields.Char(string="Identifier's Telephone", required=False, default='')
    identifier_mobile = fields.Char(string="Identifier's Mobile", required=False, default='')
    identifier_nid = fields.Char(string="Identifier's NID", required=False, default=False)
    service_type = fields.Many2one('isp_crm.service_type', default=False, required=False, string='Service Type')
    connection_type = fields.Many2one('isp_crm.connection_type', default=False, required=False, string='Connection Type')
    connection_media = fields.Many2one('isp_crm.connection_media', default=False, required=False, string='Connection Media' )
    connection_status = fields.Boolean(string='Connection Up', default=False, required=False)
    bill_cycle_date = fields.Integer(string='Bill Cycle Date', required=False, default=None, readonly=True)
    total_installation_charge = fields.Monetary(compute='_compute_installation_charge', string="Total Instl. Charge")
    is_potential_customer = fields.Boolean(string='Is This Customer potential or not?', default=True, required=False)
    package_id = fields.Many2one('product.product', string='Package', domain=[('sale_ok', '=', True)],
                                 change_default=True, ondelete='restrict')
    # Package Info
    current_package_id = fields.Many2one('product.product', string='Package', domain=[('sale_ok', '=', True)],
                                         change_default=True, ondelete='restrict')
    current_package_end_date = fields.Datetime('Valid Till', default=None)
    current_package_price = fields.Float('Current Package Price', required=True,
                                         digits=dp.get_precision('Product Price'), default=0.0)
    current_package_original_price = fields.Float('Current Package Original Price',
                                                  digits=dp.get_precision('Product Price'), default=0.0)
    next_package_id = fields.Many2one('product.product', string='Future Package', domain=[('sale_ok', '=', True)],
                                      change_default=True, ondelete='restrict')
    next_package_start_date = fields.Datetime('Next Package Start Date', default=None)
    next_package_price = fields.Float('Next Package Price',
                                      digits=dp.get_precision('Product Price'), default=0.0)
    next_package_original_price = fields.Float('Next Package Original Price',
                                               digits=dp.get_precision('Product Price'), default=0.0)



    @api.model
    def create(self, vals):
        if vals.get('subscriber_id', 'New') == 'New':
            customer_type = "MR" if self.company_type == 'person' else "MC"
            sequence = self.env['ir.sequence'].next_by_code('res.partner')
            sequence_str = customer_type + sequence
            vals['subscriber_id'] = sequence_str

        validated = True

        if vals.get('email'):
            if len(vals.get('email')) < 256:
                if re.match("^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9_-]+\.[a-zA-Z0-9-]+([\.]?[a-zA-Z0-9-])*$", vals.get('email')) == None:
                    validated = False
                    raise UserError(_('Please Enter a Valid Email Address!'))

            else:
                validated = False
                raise UserError(_('Email Address is too long!'))

        if vals.get('mobile'):
            if len(vals.get('mobile')) < 15:
                if re.match("^([0-9]+-)*[0-9]+$", vals.get('mobile')) == None:
                    validated = False
                    raise UserError(_('Please Enter a Valid Mobile Number!'))
            else:
                validated = False
                raise UserError(_('Mobile number is too long!'))

        if vals.get('phone'):
            if len(vals.get('phone')) < 15:
                if re.match("^([0-9]+-)*[0-9]+$", vals.get('phone')) == None:
                    validated = False
                    raise UserError(_('Please Enter a Valid Phone Number!'))
            else:
                validated = False
                raise UserError(_('Phone number is too long!'))

        if validated:
            return super(Customer, self).create(vals)

    @api.multi
    def action_view_customer_service_request(self):
        self.ensure_one()
        action = self.env.ref('isp_crm_module.isp_crm_module_service_request_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('customer', '=', self.id))
        return action

    @api.multi
    def _compute_installation_charge(self):
        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self:
            all_partner_ids = partner.search([('customer', '=', True)])

        for partner in all_partner_ids:
            customer_service_req_object = self.env['isp_crm_module.service_request'].search([('customer', '=', partner.id)])
            total_instllation_charge =  sum(req.amount_total for req in customer_service_req_object)
            partner.total_installation_charge = total_instllation_charge

