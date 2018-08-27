# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ServiceType(models.Model):
    """Service Type of ISP. Like: Internet, Data, Storage etc"""
    _name = 'isp_crm.service_type'
    _description = "Different type of service type is enlisted here."
    _order = 'name, id'

    name = fields.Char(string="Service Name", required=True, copy=True,)
    short_code = fields.Char(string="Service Short Code", required=True, copy=True,)
    description = fields.Text("Description")
