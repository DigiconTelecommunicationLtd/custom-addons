# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timezone
states = [
    ('state_1', 'state 1'),
    ('state_2', 'state 2'),
    ('state_3', 'state 3'),
]

class TestModuleModel(models.Model):
    _name = 'test_module.test'

    name = fields.Char("Name")
    state = fields.Selection(states, string="States", )

    @api.model
    def test_cron_method(self):
        print(self.env['res.partner'].search([])[0].name)
        return True