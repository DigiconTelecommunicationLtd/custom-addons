# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
import random
import string

class TemporaryLinks(models.Model):
    _name = 'isp_crm_module.temporary_links'
    _description = "ISP CRM TEMPORARY LINKS"
    _rec_name = 'name'
    _order = "create_date desc, name, id"


    name = fields.Many2one('res.partner', default=False, required=False, string='User')
    link = fields.Char('Link')

    def randomString(self,stringLength):
        """Generate a random string of fixed length """
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))


