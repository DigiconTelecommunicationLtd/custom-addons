# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ConnectionMedia(models.Model):
    """Connection Media of ISP. Like: Fiber, Wireless, UTP Others"""
    _name = 'isp_crm.connection_media'
    _description = "Different media of connection are enlisted here."
    _order = 'name, id'

    name = fields.Char(string="Connection Media", required=True, copy=True,)
    short_code = fields.Char(string="Short Code", required=True, copy=True,)
    description = fields.Text("Description")
