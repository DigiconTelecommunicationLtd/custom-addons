# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskStage(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_stage"
    _description = "Helpdesk Stage"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    color = fields.Integer()