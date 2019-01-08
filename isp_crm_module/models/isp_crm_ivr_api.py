# -*- coding: utf-8 -*-

from odoo import api, fields, models

class IVRApi(models.Model):
    """
    Model for ivr api.
    """
    _name = "isp_crm_module.ivr_api"
    _description = "IVR Api module"

    customer_id = fields.Char('Customer ID')
    customer_name = fields.Char('Customer Name')
    package_name = fields.Char('Package Name')