# -*- coding: utf-8 -*-



from ast import literal_eval
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import Warning, UserError
import re
import odoo.addons.decimal_precision as dp
from odoo import tools

class ISPCRMSaleReport(models.Model):
    """Inherits res.partner and adds Customer info in partner form"""
    _inherit = 'sale.report'

    customer_type = fields.Selection(related='partner_id.opportunity_ids.lead_type', string='Customer Type')
    # corporate_otc_amount = fields.Monetary(related='partner_id.invoice_ids.corporate_otc_amount', string='OTC Amount', readonly=True)
    # toal_amount_otc_mrc = fields.Monetary(related='partner_id.invoice_ids.toal_amount_otc_mrc', string='Total (OTC + MRC)', readonly=True)
    corporate_otc_amount = fields.Float(string='OTC Amount',readonly=True)
    toal_amount_otc_mrc = fields.Float(string='Total (OTC + MRC)', readonly=True)
    toal_amount_mrc = fields.Float(string='MRC Amount', readonly=True)

    product_id = fields.Float(related='corporate_otc_amount',readonly=True)
    categ_id = fields.Float(related='corporate_otc_amount',readonly=True)
    product_tmpl_id = fields.Float(related='corporate_otc_amount',readonly=True)
    product_uom = fields.Float(related='corporate_otc_amount',readonly=True)
    qty_delivered = fields.Float(related='corporate_otc_amount',readonly=True)
    qty_to_invoice = fields.Float(related='corporate_otc_amount',readonly=True)
    qty_invoiced = fields.Float(related='corporate_otc_amount',readonly=True)
    price_subtotal = fields.Float(related='corporate_otc_amount',readonly=True)
    amt_to_invoice = fields.Float(related='corporate_otc_amount',readonly=True)
    amt_invoiced = fields.Float(related='corporate_otc_amount',readonly=True)
    weight = fields.Float(related='corporate_otc_amount',readonly=True)
    volume = fields.Float(related='corporate_otc_amount',readonly=True)
    nbr = fields.Float(related='corporate_otc_amount',readonly=True)
    product_uom_qty = fields.Float(related='corporate_otc_amount',readonly=True)
    warehouse_id = fields.Float(related='corporate_otc_amount',readonly=True)
    price_total = fields.Float(related='corporate_otc_amount',readonly=True)

    # commercial_partner_id = fields.Many2one('res.partner', 'Commercial Entity', readonly=True)
    # state = fields.Selection([
    #     ('draft', 'Draft Quotation'),
    #     ('sent', 'Quotation Sent'),
    #     ('sale', 'Sales Order'),
    #     ('done', 'Sales Done'),
    #     ('cancel', 'Cancelled'),
    # ], string='Status', readonly=True)


    # def _select(self):
    #     select_str = """
    #         WITH currency_rate as (%s)
    #          SELECT min(l.id) as id,
    #                 l.product_id as product_id,
    #                 t.uom_id as product_uom,
    #                 sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
    #                 sum(l.qty_delivered / u.factor * u2.factor) as qty_delivered,
    #                 sum(l.qty_invoiced / u.factor * u2.factor) as qty_invoiced,
    #                 sum(l.qty_to_invoice / u.factor * u2.factor) as qty_to_invoice,
    #                 sum(l.price_total / COALESCE(cr.rate, 1.0)) as price_total,
    #                 sum(l.price_subtotal / COALESCE(cr.rate, 1.0)) as price_subtotal,
    #                 sum(l.amt_to_invoice / COALESCE(cr.rate, 1.0)) as amt_to_invoice,
    #                 sum(l.amt_invoiced / COALESCE(cr.rate, 1.0)) as amt_invoiced,
    #                 count(*) as nbr,
    #                 s.price_total as corporate_otc_amount,
    #                 sum(l.price_subtotal / COALESCE(cr.rate, 1.0)) as toal_amount_mrc,
    #                 s.price_total+sum(l.price_subtotal / COALESCE(cr.rate, 1.0)) as toal_amount_otc_mrc,
    #                 s.name as name,
    #                 s.date_order as date,
    #                 s.confirmation_date as confirmation_date,
    #                 s.state as state,
    #                 s.partner_id as partner_id,
    #                 s.user_id as user_id,
    #                 s.company_id as company_id,
    #                 extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
    #                 t.categ_id as categ_id,
    #                 s.pricelist_id as pricelist_id,
    #                 s.analytic_account_id as analytic_account_id,
    #                 s.team_id as team_id,
    #                 p.product_tmpl_id,
    #                 partner.country_id as country_id,
    #                 partner.commercial_partner_id as commercial_partner_id,
    #                 sum(p.weight * l.product_uom_qty / u.factor * u2.factor) as weight,
    #                 sum(p.volume * l.product_uom_qty / u.factor * u2.factor) as volume
    #     """ % self.env['res.currency']._select_companies_rates()
    #     return select_str
    #
    # def _from(self):
    #     from_str = """
    #             sale_order_line l
    #                   join sale_order s on (l.order_id=s.id)
    #                   join res_partner partner on s.partner_id = partner.id
    #                     left join product_product p on (l.product_id=p.id)
    #                         left join product_template t on (p.product_tmpl_id=t.id)
    #                 left join product_uom u on (u.id=l.product_uom)
    #                 left join product_uom u2 on (u2.id=t.uom_id)
    #                 left join product_pricelist pp on (s.pricelist_id = pp.id)
    #                 left join currency_rate cr on (cr.currency_id = pp.currency_id and
    #                     cr.company_id = s.company_id and
    #                     cr.date_start <= coalesce(s.date_order, now()) and
    #                     (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
    #     """
    #     return from_str
    #
    # def _group_by(self):
    #     group_by_str = """
    #         GROUP BY l.product_id,
    #                 l.order_id,
    #                 t.uom_id,
    #                 t.categ_id,
    #                 s.name,
    #                 s.amount_total,
    #                 s.price_total,
    #                 s.date_order,
    #                 s.confirmation_date,
    #                 s.partner_id,
    #                 s.user_id,
    #                 s.state,
    #                 s.company_id,
    #                 s.pricelist_id,
    #                 s.analytic_account_id,
    #                 s.team_id,
    #                 p.product_tmpl_id,
    #                 partner.country_id,
    #                 partner.commercial_partner_id
    #     """
    #     return group_by_str

    def _select(self):
        try:
            select_str = """
                WITH currency_rate as (%s)
                 SELECT min(s.id) as id,
                        count(*) as nbr,
                        s.price_total as corporate_otc_amount,
                        s.amount_total as toal_amount_mrc,
                        s.price_total+s.amount_total as toal_amount_otc_mrc,
                        s.name as name,
                        s.date_order as date,
                        s.confirmation_date as confirmation_date,
                        s.state as state,
                        s.partner_id as partner_id,
                        s.user_id as user_id,
                        s.company_id as company_id,
                        extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                        s.pricelist_id as pricelist_id,
                        s.analytic_account_id as analytic_account_id,
                        s.team_id as team_id,
                        partner.country_id as country_id,
                        partner.commercial_partner_id as commercial_partner_id
            """ % self.env['res.currency']._select_companies_rates()
            return select_str
        except Exception as ex:
            print(ex)

    def _from(self):
        try:
            from_str = """
                    sale_order s
                          join res_partner partner on s.partner_id = partner.id
                        left join product_pricelist pp on (s.pricelist_id = pp.id)
                        left join currency_rate cr on (cr.currency_id = pp.currency_id and
                            cr.company_id = s.company_id and
                            cr.date_start <= coalesce(s.date_order, now()) and
                            (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
            """
            return from_str
        except Exception as ex:
            print(ex)

    def _group_by(self):
        try:
            group_by_str = """
                GROUP BY s.amount_total,
                        s.price_total,
                        s.name,
                        s.date_order,
                        s.confirmation_date,
                        s.partner_id,
                        s.user_id,
                        s.state,
                        s.company_id,
                        s.pricelist_id,
                        s.analytic_account_id,
                        s.team_id,
                        partner.country_id,
                        partner.commercial_partner_id
            """
            return group_by_str
        except Exception as ex:
            print(ex)