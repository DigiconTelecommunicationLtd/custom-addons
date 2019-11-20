# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError, Warning
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class DashboardTwo(models.Model):
    _name = "mime_sales_report.sales_individual_filter"
    customer = fields.Many2one('res.partner',domain=[('is_potential_customer', '=',False)])



    @api.multi
    def individual_filter(self):
        print('asasddsasda')
        type=None
        if 'MR' in self.customer.subscriber_id:
            type='retail'
        elif 'MS' in self.customer.subscriber_id:
            type='corporate'
        else:
            type = 'sohoandsme'
        return self.env['mime_sales_report.individucal_customer_transient'].get_report(self.customer.id,type)

