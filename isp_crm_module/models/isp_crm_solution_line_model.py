# -*- coding: utf-8 -*-

import string
import random
from datetime import datetime, timedelta


from odoo import api, fields, models, _
from odoo.exceptions import Warning


AVAILABLE_PRIORITIES = [
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
]

DEFAULT_STATES = [
    ('new', 'New'),
    ('core', 'Core'),
    ('transmission', 'Transmission'),
    ('done', 'Done'),
]

DEFAULT_PASSWORD_SIZE = 8

OTC_PRODUCT_CODE = 'ISP-OTC'

class SolutionLine(models.Model):
    """
    Model for different type of service_requests.
    """
    _name = "isp_crm_module.solution_line"
    _description = "Service Request Solutions and their status."
    _rec_name = 'name'
    _order = "create_date desc, name, id"

    service_request_id = fields.Many2one('isp_crm_module.service_request', string="Service Request", required=True)
    solution_id = fields.Many2one('isp_crm_module.solution', string="Solution", required=True, translate=True)
    name = fields.Text('Description', required=False)
    assigned_to_id = fields.Many2one('res.users', string="Assigned To")
    is_done = fields.Boolean("Is Done", default=False)

