# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ConnectionType(models.Model):
    """Connection Type of ISP. Like: Dedicated, Shared, Others etc"""
    _name = 'isp_crm.connection_type'
    _description = "Different type of connections are enlisted here."
    _order = 'name, id'

    name = fields.Char(string="Connection Name", required=True, copy=True,)
    short_code = fields.Char(string="Connection Short Code", required=True, copy=True,)
    description = fields.Text("Description")
