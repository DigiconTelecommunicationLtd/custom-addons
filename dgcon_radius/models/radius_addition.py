# -*- coding: utf-8 -*-

from odoo import models, fields, api

class dgcon_customer_radius(models.Model):
     _inherit = 'res.partner'

     ppoeuername = fields.Char(string='PPoE Username')
     ppoepassword = fields.Char(string='PPoE Password')

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100