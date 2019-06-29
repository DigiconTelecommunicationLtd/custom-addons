# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Dgconlogs(models.Model):
    """
    Dgcon logs
    This model will be used to store the logs

    """
    _name = 'dgcon_radius.logs'

    username = fields.Char()
    password = fields.Char()
    bandwidth = fields.Char()
    ip_pool = fields.Char()
    date = fields.Char()
    message = fields.Text()
    status = fields.Boolean()
    radius_error = fields.Boolean()
    type = fields.Char()
    update_package =fields.Char()
    update_expiry = fields.Char()