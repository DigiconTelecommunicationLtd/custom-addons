# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class User(models.Model):
    _inherit = 'res.users'

    team = fields.One2many('isp_helpdesk.team', 'team_members', string="Team")
    ticket_count = fields.Integer("Tickets", compute='_compute_ticket_count')

    @api.multi
    def _compute_ticket_count(self):
        for user in self:
            user.ticket_count = self.env['isp_helpdesk.ticket'].search_count([('assigned_to', '=', user.id)])