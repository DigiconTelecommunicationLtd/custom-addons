# -*- coding: utf-8 -*-



from ast import literal_eval
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import Warning, UserError
import re
import odoo.addons.decimal_precision as dp


class CustomerInvoice(models.Model):
    """Inherits res.partner and adds Customer info in partner form"""
    _name = 'isp_crm_module.customer_invoice_status'
    _description = "Showing the list of Customer and current month's Invoice status."
    _rec_name = 'name'
    _order = "create_date desc, name, id"

    name = fields.Char('Name', required=True, index=True, copy=False, default='New')
    # customer info
    customer_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)],
                               track_visibility='onchange',)
    # customer_subs_id = fields.Char(compute="_compute_package_info", string="ID")
    # customer_name = fields.Char(related='customer_id.name', store=True, string="Name")
    customer_email = fields.Char(related='customer_id.email', store=True, string="Email")
    customer_mobile = fields.Char(string="Mobile", related='customer_id.mobile', store=True)
    customer_phone = fields.Char(string="Phone", related='customer_id.phone', store=True)
    customer_company = fields.Char(string="Company", related='customer_id.parent_id.name', store=True)
    customer_current_package_id = fields.Many2one(compute="_compute_package_info", string="Package ID")
    customer_current_package_name = fields.Char(compute="_compute_package_info", string="Package")
    customer_current_package_start_date = fields.Date(related='customer_id.current_package_start_date', store=True, string="Start date")
    customer_current_package_end_date = fields.Date(related='customer_id.current_package_end_date', store=True, string="End Date")
    customer_current_package_price = fields.Float(related="customer_id.current_package_price", store=True, string="Price")
    customer_current_package_original_price = fields.Float(related="customer_id.current_package_original_price", store=True, string="Original Price")
    customer_active_status= fields.Selection(related="customer_id.active_status", store=True, string="Active Status")


    def _compute_package_info(self):
        for record in self:
            # record.customer_subs_id = self.customer_id.subscriber_id
            # record.active_status = record.customer_id.active_status
            record.customer_current_package_id = record.customer_id.current_package_id.id
            record.customer_current_package_name = record.customer_id.current_package_id.name
            record.customer_current_package_start_date =record.customer_id.current_package_start_date
            record.customer_current_package_end_date = record.customer_id.current_package_end_date
            record.customer_current_package_price = record.customer_id.current_package_price
            record.customer_current_package_original_price = record.customer_id.current_package_original_price