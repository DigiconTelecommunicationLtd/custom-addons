# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ISPCRMAccessRights(models.Model):
    _name = 'isp_crm.access.rights'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)