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



    # TODO-Arif: give a name field in this place
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

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('isp_crm_module.service_request') or '/'
        return super(ServiceRequest, self).create(vals)

    # @api.model
    # def read_group(self,
    #                domain,
    #                fields,
    #                groupby,
    #                offset=0,
    #                limit=None,
    #                orderby=False,
    #                lazy=True):
    #     """ Override read_group to always display all stages. """
    #     if groupby and groupby[0] == "stage":
    #         # Default result structure
    #         stages = [('new', _('New')), ('assign', _('Assigned')),
    #                   ('evaluate', _('Evaluating')), ('done', _('Done')),
    #                   ('cancel', _('Cancel'))]
    #         read_group_all_stages = [{
    #             '__context': {
    #                 'group_by': groupby[1:]
    #             },
    #             '__domain':
    #                 domain + [('stage', '=', stage_value)],
    #             'stage':
    #                 stage_value,
    #             'stage_count':
    #                 0,
    #         } for stage_value, stage_name in stages]
    #         # Get standard results
    #         read_group_res = super(ServiceRequest, self).read_group(
    #                 domain,
    #                 fields,
    #                 groupby,
    #                 offset=offset,
    #                 limit=limit,
    #                 orderby=orderby)
    #         # Update standard results with default results
    #         result = []
    #         for stage_value, stage_name in stages:
    #             res = filter(lambda x: x['stage'] == stage_value,
    #                          read_group_res)
    #             if not res:
    #                 res = filter(lambda x: x['stage'] == stage_value,
    #                              read_group_all_stages)
    #             res[0]['stage'] = [stage_value, stage_name]
    #             result.append(res[0])
    #         return result
    #     else:
    #         return super(ServiceRequest, self).read_group(
    #                 domain,
    #                 fields,
    #                 groupby,
    #                 offset=offset,
    #                 limit=limit,
    #                 orderby=orderby)