from odoo import api, fields, models, _
class InheritedIspCrmProductLineModel(models.Model):
    _inherit =  "isp_crm_module.product_line"

    # @api.model
    # @api.onchange('product_uom_qty')
    # def onchangeproduct_uom_qty(self):
    #     print("from product_line*****************************************************************")
    #     print(self._origin.id)
        # for records in self:
        #     print(records._origin)
        #     print(records.product_uom_qty)

    # @api.multi
    # def write(self, values):
    #     print("from write*****************************************************************")
    #     print("before",self.product_uom_qty)
    #     print("after", values.product_uom_qty)
    #     res = super(InheritedIspCrmProductLineModel, self).write(values)
    #
    #     return res



