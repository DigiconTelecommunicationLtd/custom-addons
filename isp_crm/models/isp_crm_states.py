# -*- coding: utf-8 -*-

from odoo import models, fields, api

class IspCRMStates(models.Model):
    _inherit = 'crm.lead'

    is_state_done = fields.Boolean(string='Is State Done', compute='_is_state_done')

    @api.multi
    def _is_state_done(self):
        return True
