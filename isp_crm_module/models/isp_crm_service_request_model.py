# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

AVAILABLE_PRIORITIES = [
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
]



class ServiceRequest(models.Model):
    """
    Model for different type of service_requests.
    """
    _name = "isp_crm_module.service_request"
    _description = "Service Request To be solved."
    _rec_name = 'name'
    _order = "create_date desc, name, id"

    @api.depends('product_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for service_request in self:
            amount_untaxed = 0.00
            for line in service_request.product_line:
                amount_untaxed += line.price_subtotal
            service_request.update({
                'amount_total': amount_untaxed,
            })

    name = fields.Char('Request Name', required=True, index=True, copy=False, default='New')
    problem = fields.Many2one('isp_crm_module.problem', string="Problem", required=True, translate=True)
    description = fields.Text('Description')
    stage = fields.Many2one('isp_crm_module.stage', string="Stage")
    assigned_to = fields.Many2one('res.users', string="Assigned To")
    customer = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)])
    customer_email = fields.Char(related='customer.email', store=True)
    customer_mobile = fields.Char(string="Mobile", related='customer.mobile', store=True)
    customer_company = fields.Char(string="Company", related='customer.parent_id.name', store=True)
    team = fields.Many2one('isp_crm_module.team', string="Team", realated="isp_crm_module.assigned_to")
    team_leader = fields.Many2one('res.users', string="Team Leader",)
    project = fields.Many2one('project.project', string="Project")
    priority = fields.Selection(AVAILABLE_PRIORITIES, string="Priority")
    close_date = fields.Datetime('Close Date', readonly=True, default=None)
    is_service_request_closed = fields.Boolean('Is Service Request Closed', default=False) # TODO-Arif: add a compute field for close date
    solutions = fields.Many2many('isp_crm_module.solution', string="Solutions")
    color = fields.Integer()
    is_done = fields.Boolean("Is Done", default=False)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',  readonly=True,
                                   help="Pricelist for Service Request.")
    currency_id = fields.Many2one("res.currency", related='pricelist_id.currency_id', string="Currency", readonly=True)
    product_line = fields.One2many('isp_crm_module.product_line', 'service_request_id', string='Product Lines', copy=True, auto_join=True)

    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   track_visibility='always')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.service_request') or '/'
        return super(ServiceRequest, self).create(vals)
