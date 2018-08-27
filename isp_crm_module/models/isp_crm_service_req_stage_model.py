# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ServiceRequestStage(models.Model):
    """
    Stages of service requests
    """
    _name = 'isp_crm_module.stage'
    _inherit = 'crm.stage'
    _description = "Stage of Service Request"
    _rec_name = 'name'
    _order = "sequence, name, id"

    is_service_req_stage = models.BooleanField("Is Service Request Object")


