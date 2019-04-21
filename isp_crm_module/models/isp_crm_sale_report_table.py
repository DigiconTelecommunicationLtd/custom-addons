# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class SaleReportTable(models.Model):
    _name = "sale.report.table"
    _description = "Sales Orders Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char('Order Reference', readonly=True)
    team_id = fields.Many2one('crm.team', 'Sales Channel', readonly=True, oldname='section_id')
    date = fields.Datetime('Date Order', readonly=True)
    confirmation_date = fields.Datetime('Confirmation Date', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    corporate_otc_amount = fields.Float(string='OTC Amount', readonly=True)
    toal_amount_otc_mrc = fields.Float(string='Total (OTC + MRC)', readonly=True)
    toal_amount_mrc = fields.Float(string='MRC Amount', readonly=True)

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

    @api.model_cr
    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))

