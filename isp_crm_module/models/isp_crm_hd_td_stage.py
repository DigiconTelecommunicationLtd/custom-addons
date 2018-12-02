# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HelpdeskTDStage(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.helpdesk_td_stage"
    _description = "Helpdesk TD Stage"
    _order = "create_date desc, id"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    color = fields.Integer()