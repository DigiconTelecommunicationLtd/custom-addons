# -*- coding: utf-8 -*-

from odoo import models, fields, api

class dgcon_radreply(models.Model):
     _name = 'dgcon_radius.radcheck'
     username = fields.Char()
     attribute = fields.Char()
     op = fields.Char()
     value = fields.Char()
