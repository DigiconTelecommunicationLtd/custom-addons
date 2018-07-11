# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

class Team(models.Model):
    _name = 'isp_helpdesk.team'
    _description = "Teamn of ISP HelpDesk."
    _rec_name = 'name'
    _order = "name, id"


    name = fields.Char('Team Name', translate=True)
    is_default_team = fields.Boolean(string='Is Default Team',
        help='By enabling this the corresponding team will be the default team.')
    leader = fields.Many2one('res.users', string='Leader', ondelete='set null',
        help='Leader of a team.')
    team_members = fields.Many2many('res.users', string='Team Members', ondelete='set null',
        help='Members of the team.')


