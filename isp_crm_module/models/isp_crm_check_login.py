# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CustomerLoginTrack(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.track_login"
    _description = "Login module for customer profile"

    logincode = fields.Char('Login Code', required=True, translate=True)
    subscriber_id = fields.Char('Subcriber ID', required=True, translate=True)
    password = fields.Char('Password', required=True, translate=True)