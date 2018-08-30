# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError

from . import isp_crm_service_req_stage_model

_logger = logging.getLogger(__name__)


class ServiceRequestOpportunity(models.Model):
    _name = "isp_crm_module.service_request"
    _inherit = 'crm.lead'
    _description = "Service Requests"
    _order = "priority desc,activity_date_deadline,id desc"

    stage_id = fields.Many2one('isp_crm_module.stage', string='Stage', track_visibility='onchange', index=True,
                               domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]",
                               group_expand='_read_group_stage_ids', default=lambda self: self._default_stage_id())
    tag_ids = fields.Many2many('crm.lead.tag', 'crm_lead_tag_rel', 'lead_id', 'tag_id', string='Tags',
                               help="Classify and analyze your lead/opportunity categories like: Training, Service")
    color = fields.Integer('Color Index', default=0)