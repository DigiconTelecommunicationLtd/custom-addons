# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import re
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from . import isp_crm_service_request_model


DEFAULT_PROBLEM = "There are some Problem"
INVOICE_PAID_STATUS = 'paid'
DEFAULT_PACKAGE_CAT_NAME = 'Packages'

CUSTOMER_TYPE = [
    ('retail', _('Retail')),
    ('corporate', _('Corporate')),
]

class Opportunity(models.Model):
    _inherit = 'crm.lead'
    _description = "Team of ISP CRM Opportunity."

    opportunity_seq_id = fields.Char('ID', required=True, index=True, copy=False, default='New', readonly=True)
    current_service_request_id = fields.Char(string='Service Request ID', readonly=True, required=False)
    current_service_request_status = fields.Char(string='Service Request ID', readonly=True, required=False)
    is_service_request_created = fields.Boolean("Is Service Request Created", default=False)
    tagged_product_ids = fields.Many2many('product.product', 'crm_lead_product_rel', 'lead_id', 'product_id', string='Products', help="Classify and analyze your lead/opportunity according to Products : Unlimited Package etc")
    emergency_contact_name = fields.Char(string='Emergency Contact Name', required=False)
    is_customer_deferred = fields.Boolean("Is Customer Deferred", default=False)
    invoice_state = fields.Char('Invoice State')
    referred_by = fields.Many2one('res.partner', string='Referred By')
    assigned_rm = fields.Many2one('res.users', string='RM')
    lead_type = fields.Selection(CUSTOMER_TYPE, string='Type', required=False,  help="Lead and Opportunity Type")


    def get_opportunity_address_str(self, opportunity):
        address_str = ""
        if len(opportunity) > 0:
            address_str = ", ".join([
                opportunity.street or '',
                opportunity.street2 or '',
                opportunity.city or '',
                opportunity.state_id.name or '',
                opportunity.zip or '',
                opportunity.country_id.name or '',
            ])
        return address_str

    @api.multi
    def action_set_won(self):
        for lead in self:
            # TODO Arif: `invoice_status` will be added later. Now checking status will be `confirm_sale`
            sale_confirmed = False

            # Check if invoice is paid .
            customer = self.partner_id.id
            if customer:
                check_customer = self.env['res.partner'].search([('id', '=', customer)], limit=1)
                if check_customer:
                    invoices = self.env['account.invoice'].search([('partner_id', '=', customer)], order="create_date desc", limit=1)
                    if invoices:
                        if invoices.is_deferred or invoices.state == INVOICE_PAID_STATUS:
                            self.invoice_state = invoices.state
                            super(Opportunity, lead).action_set_won()
                        else:
                            raise UserError(_("This Opportunity's invoice is neither paid nor deferred."))
                    else:
                        raise UserError(_("This Opportunity's invoice has not been created yet. Please create the invoice first ."))
                else:
                    raise UserError(_("Customer not found."))
            else:
                raise UserError(_("Customer not found."))
        return True

    @api.onchange('email_from')
    def onchange_email(self):
        if self.email_from:
            if len(self.email_from) < 256:
                if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9_-]+\.[a-zA-Z0-9-]+([\.]?[a-zA-Z0-9-])*$", self.email_from) == None:
                    raise UserError(_('Please Enter a Valid Email Address!'))
            else:
                raise UserError(_('Email Address is too long!'))

    @api.onchange('mobile')
    def onchange_mobile(self):
        if self.mobile:
            if len(self.mobile) < 15:
                if re.match("^[+]*([0-9]+-)*[0-9]+$", self.mobile) == None:
                    raise UserError(_('Please Enter a Valid Mobile Number!'))
            else:
                raise UserError(_('Mobile number is too long!'))

    @api.onchange('phone')
    def onchange_phone(self):
        if self.phone:
            if len(self.phone) < 15:
                if re.match("^([0-9]+-)*[0-9]+$", self.phone) == None:
                    raise UserError(_('Please Enter a Valid Phone Number!'))
            else:
                raise UserError(_('Phone number is too long!'))

    @api.onchange('assigned_rm')
    def onchange_assigned_rm(self):
        """
        If user changes RM , it will reflect in customer form.
        :return:
        """
        if self.assigned_rm:
            customer = self.partner_id.id
            if customer:
                check_customer = self.env['res.partner'].search([('id', '=', customer)])
                if check_customer:
                    for cust in check_customer:
                        cust.write({
                            'assigned_rm': self.assigned_rm.id,
                        })

    @api.onchange('lead_type')
    def onchange_lead_type(self):
        """
        If user changes Lead Type in opportunity form, then change Lead Type to all related sale orders of the customer of that opportunity .
        :return:
        """
        if self.lead_type:
            customer = self.partner_id.id
            if customer:
                check_customer = self.env['res.partner'].search([('id', '=', customer)], limit=1)
                if check_customer:
                    get_sales_order_of_the_customer = self.env['sale.order'].search([('partner_id', '=', check_customer.id)])
                    if get_sales_order_of_the_customer:
                        for order in get_sales_order_of_the_customer:
                            order.update({
                                'lead_type': str(self.lead_type),
                            })

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        values = self._onchange_stage_id_values(self.stage_id.id)
        if values['probability'] == 100:
            for lead in self:
                # TODO Arif: `invoice_status` will be added later. Now checking status will be `confirm_sale`
                sale_confirmed = False

                # Check if invoice is paid .
                customer = self.partner_id.id
                if customer:
                    check_customer = self.env['res.partner'].search([('id', '=', customer)], limit=1)
                    if check_customer:
                        invoices = self.env['account.invoice'].search([('partner_id', '=', customer)],
                                                                      order="date_invoice desc", limit=1)
                        if invoices:
                            if invoices.is_deferred or invoices.state == INVOICE_PAID_STATUS:
                                self.update(values)
                            else:
                                raise UserError(_("This Opportunity's invoice is neither paid nor deferred."))
                        else:
                            raise UserError(_(
                                "This Opportunity's invoice has not been created yet. Please create the invoice first ."))
                    else:
                        raise UserError(_("Customer not found."))
                else:
                    raise UserError(_("Customer not found."))
        else:
            self.update(values)

    @api.model
    def create(self, vals):
        if vals.get('opportunity_seq_id', 'New') == 'New':
            sequence_id = self.env['ir.sequence'].next_by_code('crm.lead') or '/'
            vals['opportunity_seq_id'] = sequence_id

        if (not vals.get('email_from')) and (not vals.get('phone')) and (not vals.get('mobile')):
            raise Warning(_('Please Provide any of this Email, Phone or Mobile'))

        if vals.get('email_from'):
            check_customer_email = self.env['res.partner'].search([('email', '=', vals.get('email_from'))], limit=1)
            if check_customer_email:
                raise Warning(_('Email should be unique'))
        if vals.get('phone'):
            check_customer_phone = self.env['res.partner'].search([('phone', '=', vals.get('phone'))], limit=1)
            if check_customer_phone:
                raise Warning(_('Phone Number should be unique'))
        if vals.get('mobile'):
            check_customer_mobile = self.env['res.partner'].search([('mobile', '=', vals.get('mobile'))], limit=1)
            if check_customer_mobile:
                raise Warning(_('Mobile Number should be unique'))

        return super(Opportunity, self).create(vals)

    @api.multi
    def action_create_new_service_request(self):
        res = {}
        for opportunity in self:
            first_stage = self.env['isp_crm_module.stage'].search([], order="sequence asc")[0]
            service_req_obj = self.env['isp_crm_module.service_request'].search([])
            confirmed_sale_order_id = ""
            sale_order_line_obj = ""
            for order in opportunity.order_ids:
                if order.state == 'sale':
                    confirmed_sale_order_id = order.id
                    sale_order_line_obj = self.env['sale.order.line'].search([('order_id', '=', confirmed_sale_order_id)])
                    break

            last_invoice = self.env['account.invoice'].search([('partner_id', '=', opportunity.partner_id.id)],
                                                              order='create_date asc', limit=1)
            last_invoices_inv_lines = last_invoice[0].invoice_line_ids
            package_line = ""
            for line in last_invoices_inv_lines:
                try:
                    if line.product_id.categ_id.name == DEFAULT_PACKAGE_CAT_NAME:
                        package_line = line

                except UserError as ex:
                    print(ex)

            try:
                if package_line.product_id:
                    service_req_data = {
                        'problem': str(opportunity.partner_id.name) + ' - ' + str(package_line.product_id.name) or '',
                        'stage': first_stage.id,
                        'customer': opportunity.partner_id.id,
                        'customer_email': opportunity.email_from,
                        'customer_mobile': opportunity.mobile,
                        'customer_phone': opportunity.phone,
                        'opportunity_id': opportunity.id,
                        'confirmed_sale_order_id': confirmed_sale_order_id,
                        'customer_address': self.get_opportunity_address_str(opportunity=opportunity),
                        'tagged_product_ids': [(6, None, opportunity.tagged_product_ids.ids)],
                    }
                else:
                    raise UserError('No packages under package catagory')
                    # service_req_data = {
                    #     'problem' : str(opportunity.partner_id.name) + ' - ' + "No product under package catagory" or '',
                    #     'stage' : first_stage.id,
                    #     'customer' : opportunity.partner_id.id,
                    #     'customer_email' : opportunity.email_from,
                    #     'customer_mobile' : opportunity.mobile,
                    #     'customer_phone' : opportunity.phone,
                    #     'opportunity_id': opportunity.id,
                    #     'confirmed_sale_order_id': confirmed_sale_order_id,
                    #     'customer_address': self.get_opportunity_address_str(opportunity=opportunity),
                    #     'tagged_product_ids': [(6, None, opportunity.tagged_product_ids.ids)],
                    # }
            except Exception as ex:
                raise UserError(ex)

            created_service_req_obj = service_req_obj.create(service_req_data)
            if len(sale_order_line_obj) > 0:
                for sale_order_line in sale_order_line_obj:
                    sale_order_line.update({
                        'service_request_id' : created_service_req_obj.id
                    })
            opportunity.update({
                'color' : 2,
                'current_service_request_id' : created_service_req_obj.name,
                'current_service_request_status' : 'Processing',
                'is_service_request_created' : True
            })
        return True



