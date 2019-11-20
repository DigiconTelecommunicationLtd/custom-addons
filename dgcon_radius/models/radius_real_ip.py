# -*- coding: utf-8 -*-

from odoo import models, fields, api

class dgcon_real_ip_radius(models.Model):
    _inherit = 'isp_crm_module.service_request'
    technical_info_real_ip=fields.Char(string='Real IP Address')
    is_real_ip = fields.Boolean()

    # @api.one
    # def _compute_show_hide(self):
    #     self.is_real_ip = False
    #     for product in self.tagged_product_ids:
    #         for attribute in product.attribute_line_ids:
    #             if 'real' in attribute.display_name.lower() and 'ip' in attribute.display_name.lower().lower():
    #                 self.is_real_ip = True





class dgcon_real_ip_radius_res_partner(models.Model):
    _inherit = 'res.partner'
    real_ip = fields.Char(string='Real IP Address')
    has_real_ip = fields.Boolean(default=False)
    real_ip_subtotal = fields.Float(default=0.0)
    reaL_ip_original =fields.Float(default=0.0)
