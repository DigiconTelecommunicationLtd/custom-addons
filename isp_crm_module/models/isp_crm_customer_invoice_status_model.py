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
    customer_current_package_start_date = fields.Date(compute="_compute_package_info", string="Start date")
    customer_current_package_end_date = fields.Date(compute="_compute_package_info", string="End Date")
    customer_current_package_price = fields.Float(compute="_compute_package_info", string="Price")
    customer_current_package_original_price = fields.Float(compute="_compute_package_info", string="Original Price")

    # invoice info
    invoice_id = fields.Many2one('account.invoice', string="Invoice", track_visibility='onchange', )
    invoice_number = fields.Char(related='invoice_id.number', store=True, string="Number")
    invoice_amount_total = fields.Float(compute="_compute_invoice_attributes", string="Amount")
    invoice_date_invoice = fields.Date(related='invoice_id.date_invoice', store=True, string="Date Invoiced")
    invoice_date_due = fields.Date(related='invoice_id.date_due', store=True, string="Due Date")
    invoice_state = fields.Char(compute="_compute_invoice_attributes", string="Status")

    def _compute_package_info(self):
        for record in self:
            # record.customer_subs_id = self.customer_id.subscriber_id
            record.customer_current_package_id = record.customer_id.current_package_id.id
            record.customer_current_package_name = record.customer_id.current_package_id.name
            record.customer_current_package_start_date =record.customer_id.current_package_start_date
            record.customer_current_package_end_date = record.customer_id.current_package_end_date
            record.customer_current_package_price = record.customer_id.current_package_price
            record.customer_current_package_original_price = record.customer_id.current_package_original_price

    def _compute_invoice_attributes(self):
        for record in self:
            record.invoice_amount_total = record.invoice_id.amount_total
            record.invoice_state = record.invoice_id.state