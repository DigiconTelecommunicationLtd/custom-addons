# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CustomerLogin(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.login"
    _description = "Login module for customer profile"

    name = fields.Char('Name', required=True, translate=True)
    subscriber_id = fields.Char('Subcriber ID', required=True, translate=True)
    password = fields.Char('Password', required=True, translate=True)