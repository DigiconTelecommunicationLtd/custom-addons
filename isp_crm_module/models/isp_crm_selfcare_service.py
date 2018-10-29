# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PaymentService(models.Model):
    """
    Model for different type of Problems.
    """
    _name = "isp_crm_module.selfcare_payment_service"
    _description = "Type of Services for payment in selfcare."
    _rec_name = 'name'
    _order = "name, id"

    name = fields.Char('Service Name', required=True, translate=True)
