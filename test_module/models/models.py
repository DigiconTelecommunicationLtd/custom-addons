# -*- coding: utf-8 -*-

from odoo import models, fields, api

states = [
    ('state_1', 'state 1'),
    ('state_2', 'state 2'),
    ('state_3', 'state 3'),
]

class TestModule(models.Model):
    _name = 'test_module.test'

    name = fields.Char("Name")
    state = fields.Selection(states, string="States", )