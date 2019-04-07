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
    _sql_constraints = [
        ('customer_po_no', 'unique(customer_po_no)', 'Customer PO No. already exists!')
    ]

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
    lead_type = fields.Char(compute='_get_lead_type', string='Lead Type')
    destination = fields.Char(compute='_get_destination_address', string='Destination')
    customer_po_no = fields.Char(string='Customer PO No.')
    customer_po_no_upload = fields.Binary(string='Upload File')
    file_name = fields.Char(string="File Name")

    amount_without_vat = fields.Monetary(string='Amount Without VAT', store=True, readonly=True, compute='_amount_all',
                                     track_visibility='onchange')
    amount_vat = fields.Monetary(string='VAT', store=True, readonly=True, compute='_amount_all')

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            total = amount_untaxed + amount_tax
            vat = total - ((total * 100.0) / 105.0)
            total_without_vat = (total * 100.0) / 105.0
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
                'amount_without_vat': total_without_vat,
                'amount_vat': vat,
            })

    @api.depends('otc_price', 'discount', 'govt_vat')
    def _compute_total_amount(self):
        """
        Compute the amounts of the OTC.
        """
        for order in self:
            if order.otc_price:
                if order.discount:
                    total_price = float(order.otc_price) - float(order.discount)
                else:
                    total_price = float(order.otc_price)
            else:
                total_price = 0.0
            if order.govt_vat:
                govt_vat = float(order.govt_vat)
                govt_vat = 100.0 + govt_vat
                vat = total_price - ((total_price * 100.0)/x)
            else:
                govt_vat = 0
                vat = 0.0
            x = 100.0 + govt_vat
            without_vat = (total_price * 100.0)/x
            order.update({
                'price_total': total_price,
                'price_total_without_vat': without_vat,
                'govt_vat_in_amount': str(vat),
            })

    @api.onchange('govt_vat')
    def onchange_gov_vat(self):
        if self.otc_price:
            if self.discount:
                total_price = float(self.otc_price) - float(self.discount)
            else:
                total_price = float(self.otc_price)
        else:
            total_price = 0.0
        if self.govt_vat:
            govt_vat = float(self.govt_vat)
            vat = (total_price * govt_vat) / 100.0
        else:
            govt_vat = 0
            vat = 0.0
        x = 100.0 + govt_vat
        without_vat = (total_price * 100.0) / x
        self.update({
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
            lead = order.env['crm.lead'].search([('partner_id', '=', order.partner_id.id)], order='create_date desc', limit=1)
            lead_type = lead.lead_type

            order.update({
                'lead_type': lead_type,
            })

    def _get_destination_address(self):
        """
        Compute destination address of the customer.
        :return:
        """
        for order in self:
            customer = order.env['res.partner'].search([('id', '=', order.partner_id.id)], order='create_date desc', limit=1)
            destination_address = ""

            if customer.street:
                street = customer.street
                destination_address = destination_address + str(street) + ", "
            if customer.street2:
                street2 = customer.street2
                destination_address = destination_address + str(street2) + ", "
            if customer.zip:
                zip = customer.zip
                destination_address = destination_address + str(zip) + ", "
            if customer.city:
                city = customer.city
                destination_address = destination_address + str(city) + ", "
            if customer.state_id.name:
                state_id = customer.state_id.name
                destination_address = destination_address + str(state_id) + ", "
            if customer.country_id.name:
                country_id = customer.country_id.name
                destination_address = destination_address + str(country_id)
            if destination_address.endswith(','):
                destination_address = destination_address[:-1]
            order.update({
                'destination': destination_address,
            })
