from odoo import models, fields, api,_
from odoo.exceptions import  UserError

class InheritedStockReturnPickingEb(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.multi
    def _create_returns(self):
        print('***************** create returns')
        for line in self.product_return_moves:
            print(line.product_id.categ_id.name)
            if 'consumables' in line.product_id.categ_id.name.lower() or 'consumable' in line.product_id.categ_id.name.lower():
                raise UserError('Cannot return consumables')

        new_picking, pick_type_id = super(InheritedStockReturnPickingEb, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.write({'carrier_id': False,
                       'carrier_price': 0.0})
        return new_picking, pick_type_id
