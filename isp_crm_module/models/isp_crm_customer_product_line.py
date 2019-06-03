# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
# from odoo.addons import decimal_precision as dp
import odoo.addons.decimal_precision as dp


AVAILABLE_PRIORITIES = [
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
]



class CustomerProductLine(models.Model):
    """
    Model for different type of Customer Product Lines.
    """
    _name = "isp_crm_module.customer_product_line"
    _description = "Product Line For Customer."
    _rec_name = 'name'
    _order = "create_date desc, name, id"

    customer_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Char('Request Name', required=True, index=True, copy=False, default='New')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)],
                                 change_default=True, ondelete='restrict', required=True)
    product_updatable = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', readonly=True,
                                       default=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True,
                                   default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', )
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    price_subtotal = fields.Monetary(string='Subtotal', store=True)
    price_total = fields.Monetary(string='Total', store=True)
    currency_id = fields.Many2one(related='customer_id.currency_id', store=True, string='Currency', readonly=True)
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the Product line.
        """
        for line in self:
            price = line.price_unit * (1 / 100.0)
            taxes = line.tax_id.compute_all(price, line.customer_id.currency_id, line.product_uom_qty,
                                            product=line.product_id)
            line.update({
                'price_total': taxes['total_excluded'],
                'price_subtotal': taxes['total_excluded'],
            })

        for line in self:
            price = line.price_unit * line.product_uom_qty
            # price = line.price_subtotal
            line.update({
                'price_subtotal': price,
            })

    @api.depends('product_id')
    def _compute_product_updatable(self):
        for line in self:
            line.product_updatable = True

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
                lang=self.customer_id.lang,
                partner=self.customer_id.id,
                quantity=vals.get('product_uom_qty') or self.product_uom_qty,
                date=self.customer_id.create_date,
                pricelist=self.customer_id.pricelist_id.id,
                uom=self.product_uom.id
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
                return result

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        vals['price_unit'] = product.list_price
        self.update(vals)

        return result

    @api.onchange('product_uom_qty')
    def product_uom_qty_change(self):
        """

        :return:
        """
        quantity = self.product_uom_qty
        adjusted_price = self.price_subtotal - (quantity * self.price_unit)
        self.price_subtotal= quantity * self.price_unit
        self.price_total= self.price_total - adjusted_price

        # self.update({
        #     'price_subtotal': quantity * self.price_unit,
        #     'price_total': price_total
        #
        # })

    @api.onchange('price_unit')
    def price_unit_change(self):
        """
        
        :return:
        """
        unit_price = self.price_unit
        adjusted_price = self.price_subtotal - (self.product_uom_qty * unit_price)
        self.price_subtotal = self.product_uom_qty * unit_price
        self.price_total = self.price_total - adjusted_price

        # self.update({
        #     'price_subtotal': self.product_uom_qty * unit_price,
        #     'price_total': price_total
        #
        # })
