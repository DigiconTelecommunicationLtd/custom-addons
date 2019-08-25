# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class PartnerBinding(models.TransientModel):
    _inherit = 'crm.partner.binding'
    _description = "{Partner binding model overriding while converting a lead to customer."

    action = fields.Selection([
        ('exist', 'Link to an existing customer'),
        ('create', 'Create a new Potential customer'),
        ('nothing', 'Do not link to a customer')
        ], 'Related Customer', required=True)
    # action = fields.Selection([
    #     ('exist', 'Link to an existing customer'),
    #     ('create', 'Create a new Potential customer'),
    # ], 'Related Customer', required=True,default='create')