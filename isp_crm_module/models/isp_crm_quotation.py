# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError

CONNECTIVITY_MEDIA = [
    ('cable', _('Cable')),
    ('radio', _('Radio')),
]

class CustomerQuotation(models.Model):
    _inherit = 'sale.order'
    _order = "create_date desc, name, id"

    foundation = fields.Many2one('isp_crm_module.mime_pop', string='Foundation')
    connectivity_media = fields.Selection(CONNECTIVITY_MEDIA, string='Connectivity Media', required=False,  help="Connectivity Media")
    required_tower_height = fields.Char(string='Required Tower Height', required=False)
    backbone_provider = fields.Many2one('isp_crm_module.backbone_provider', string='Backbone Provider')
    otc_price = fields.Char(string='Regular Price (In BDT)', required=False)
    discount = fields.Char(string='Discount (In BDT)', required=False)
    price_total = fields.Monetary(compute='_compute_total_amount', string='Total Price (In BDT)', readonly=True, store=True)
    price_total_without_vat = fields.Monetary(compute='_compute_total_amount',string='Total Price Without VAT (In BDT)', readonly=True, store=True)
    govt_vat = fields.Char(string='Govt. VAT (In Percentage)', required=False, readonly=False, default='5.0')
    govt_vat_in_amount = fields.Char(compute='_compute_total_amount', string='Govt. VAT (In Amount)', readonly=True, store=True)
    lead_type = fields.Char(compute='_get_lead_type', string='Lead Type', readonly=True,
                                     store=True)

    @api.depends('otc_price', 'discount')
    def _compute_total_amount(self):
        """
        Compute the amounts of the OTC.
        """
        for order in self:
            total_price = float(order.otc_price) - float(order.discount)
            govt_vat = float(order.govt_vat)
            vat = (total_price * govt_vat)/100.0
            without_vat = float(total_price) - float(vat)
            order.update({
                'price_total': total_price,
                'price_total_without_vat': without_vat,
                'govt_vat_in_amount': str(vat),
            })

    @api.depends('partner_id')
    def _get_lead_type(self):
        """
        Compute type of customer .(Corporate or Retail)
        :return:
        """

        for order in self:
            lead = order.env['crm.lead'].search([('name', '=', order.partner_id.name)], order='create_date desc', limit=1)
            lead_type = lead.lead_type

            order.update({
                'lead_type': lead_type,
            })
