from odoo import api, fields, models, _


class InheritedSaleOrder(models.Model):
    _inherit = 'sale.order'
    new_lead_type = fields.Char(compute='_get_new_lead_type', string='Lead Type')

    @api.multi
    def _get_new_lead_type(self):
        for record in self:
            if record.lead_type == 'retail':
                record.new_lead_type = 'Retail'
            elif record.lead_type == 'corporate':
                record.new_lead_type = 'Corporate'
            elif record.lead_type == 'sohoandsme':
                record.new_lead_type = 'SOHO and SME'
