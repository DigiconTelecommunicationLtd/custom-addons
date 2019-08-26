# -*- coding: utf-8 -*-

import string
import random
from datetime import datetime, timedelta
import logging
from passlib.context import CryptContext
from odoo import http
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from odoo.tools import email_split
import base64
import ctypes
from odoo.addons.isp_crm_module.models.radius_integration import *
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
DEFAULT_MONTH_DAYS = 30
DEFAULT_NEXT_MONTH_DAYS = 31
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
INVOICE_PAID_STATUS = 'paid'

OTC_PRODUCT_CODE = 'ISP-OTC'
DEFAULT_PACKAGE_CAT_NAME = 'Packages'
BILLING_GROUP_MAIL = "billing.mime@cg-bd.com"


TD_FLAGS = [
    ('0', 'Pending'),
    ('1', 'Confirmed'),
]

default_crypt_context = CryptContext(
    # kdf which can be verified by the context. The default encryption kdf is
    # the first of the list
    ['pbkdf2_sha512', 'md5_crypt'],
    # deprecated algorithms are still verified as usual, but ``needs_update``
    # will indicate that the stored hash should be replaced by a more recent
    # algorithm. Passlib 1.6 supports an `auto` value which deprecates any
    # algorithm but the default, but Ubuntu LTS only provides 1.5 so far.
    deprecated=['md5_crypt'],
)

class UpdatedServiceRequest(models.Model):
    _inherit =  "isp_crm_module.service_request"

    @api.multi
    def action_make_service_request_done(self):
        print('*********************** user')
        customer = self.customer.id
        check_customer = self.env['res.partner'].search([('id', '=', customer)], limit=1)
        opportunity = self.env['crm.lead']
        if check_customer:
            invoices = self.env['account.invoice'].search([('partner_id', '=', customer)], order="create_date desc",
                                                          limit=1)
            if invoices:
                # if invoices.is_deferred or invoices.state == INVOICE_PAID_STATUS:
                if invoices.is_deferred or invoices.state == INVOICE_PAID_STATUS:
                    self.invoice_state = invoices.state
                    opportunity.action_set_won()
                    opportunity.action_create_new_service_request()

                    for service_req in self:
                        # update the stage of this service request to done
                        cust_password_radius = None
                        last_stage_obj = self.env['isp_crm_module.stage'].search([('name', '=', 'Done')], limit=1)

                        # Deduct quantity from stock.
                        try:
                            for product in service_req.product_line:
                                quantity = product.product_uom_qty
                                get_product = self.env['stock.quant'].search(
                                    [('product_id', '=', product.product_id.id)], order='create_date desc', limit=1)
                                if get_product:
                                    current_stock_quantity = get_product.quantity
                                    if abs(current_stock_quantity) <= 0.0:
                                        raise UserError('Not enough quantity available in stock.')
                                    new_available_quantity = abs(current_stock_quantity) - abs(quantity)
                                    if new_available_quantity:
                                        inventory_name = str(get_product.product_id.display_name) + "-" + str(
                                            datetime.now())
                                        create_inventory = self.env['stock.inventory'].create({
                                            'name': inventory_name,
                                            'filter': 'product',
                                            'product_id': get_product.product_id.id,
                                            'accounting_date': datetime.today(),
                                        }).action_start()
                                        get_inventory = self.env['stock.inventory'].search(
                                            [('name', '=', inventory_name)], order='create_date desc', limit=1)
                                        if get_inventory:
                                            get_inventory_lines = get_inventory.line_ids
                                            for line in get_inventory_lines:
                                                line.update({
                                                    'product_qty': float(abs(new_available_quantity))
                                                })
                                            get_inventory.action_done()
                        except Exception as ex:
                            print(ex)

                        if service_req.is_send_for_bill_date_confirmation:
                            service_req.update({
                                'is_done': True,
                                # 'stage': last_stage_obj.id,
                                'is_send_for_bill_date_confirmation': False,
                                'td_flags': TD_FLAGS[1][0],
                                'mark_done_date': datetime.today()
                            })
                        else:
                            service_req.update({
                                'is_done': True,
                                'stage': last_stage_obj.id,
                                'mark_done_date': datetime.today()
                            })
                        customer = service_req.customer
                        # format sequence number based on lead type
                        get_opportunity = self.env['crm.lead'].search([('partner_id', '=', customer.id)], limit=1)
                        if get_opportunity:
                            if get_opportunity.lead_type == "retail":
                                customer_type = "MR"
                            elif get_opportunity.lead_type == "sohoandsme":
                                customer_type = "MS"
                            else:
                                customer_type = "MC"
                        else:
                            customer_type = "MR" if customer.company_type == 'person' else "MC"
                        sequence = self.env['ir.sequence'].next_by_code('res.partner')
                        sequence_str = customer_type + sequence
                        customer_subs_id = sequence_str
                        cust_password = self._create_random_password(size=DEFAULT_PASSWORD_SIZE)
                        encrypted = "abcd1234"

                        if service_req.billing_start_date and customer_type != "MR":
                            current_package_start_date = service_req.billing_start_date
                        else:
                            current_package_start_date = fields.Date.today()

                        # TODO START CREATE RADIUS

                        # This is only for Retail users
                        if customer_type == 'MR':
                            for productline in service_req.order_line:
                                if productline.product_id.categ_id.name == DEFAULT_PACKAGE_CAT_NAME:
                                    cust_password_radius = self._create_random_password(size=DEFAULT_PASSWORD_SIZE)
                                    result_radius = create_radius_user(customer_subs_id, cust_password_radius,
                                                                       productline.product_id.name,
                                                                       customer._get_package_end_date(
                                                                           fields.Date.today()), customer.id)

                                    if result_radius != 'success':
                                        raise UserError('Radius server issue: ' + result_radius)
                                    else:
                                        # service_activation_date and billing_start_date is not being set for afew user group
                                        # solution 1: updating it with sudo command. Not yet implemented
                                        customer.update({
                                            'is_potential_customer': False,
                                            'subscriber_id': customer_subs_id,
                                            'technical_info_ip': self.ip,
                                            'technical_info_subnet_mask': self.subnet_mask,
                                            'technical_info_gateway': self.gateway,
                                            'description_info': self.description,
                                            'service_activation_date': fields.Date().today(),
                                            'billing_start_date': current_package_start_date,
                                            'ppoeuername': customer_subs_id,
                                            'ppoepassword': cust_password_radius,
                                            'real_ip': self.technical_info_real_ip,
                                            'is_deferred':invoices.is_deferred,
                                        })


                        # Not a retail customer so go as it was before
                        else:
                            customer.update({
                                'is_potential_customer': False,
                                'subscriber_id': customer_subs_id,
                                'technical_info_ip': self.ip,
                                'technical_info_subnet_mask': self.subnet_mask,
                                'technical_info_gateway': self.gateway,
                                'description_info': self.description,
                                'service_activation_date': fields.Date().today(),
                                'billing_start_date': current_package_start_date
                            })
                        # TODO STOP CREATE RADIUS
                        # updating customer's potentiality
                        # customer.update({
                        #     'is_potential_customer' : False,
                        #     'subscriber_id' : customer_subs_id,
                        #     'technical_info_ip' : self.ip,
                        #     'technical_info_subnet_mask' : self.subnet_mask,
                        #     'technical_info_gateway' : self.gateway,
                        #     'description_info' : self.description,
                        #     'service_activation_date' : fields.Date().today(),
                        #     'billing_start_date' : current_package_start_date
                        # })

                        # Create an user
                        user_created = self._create_user(partner=customer, username=customer_subs_id,
                                                         password=cust_password)

                        # # invoice generation
                        # last_invoice                    = self.env['account.invoice'].search([('partner_id', '=', customer.id)], order='create_date desc', limit=1)
                        # last_invoices_inv_lines         = last_invoice[0].invoice_line_ids
                        #
                        # for line in last_invoices_inv_lines:
                        #     try:
                        #         if line.product_id.categ_id.name == DEFAULT_PACKAGE_CAT_NAME:
                        #             package_line = line
                        #
                        #     except UserError as ex:
                        #         print(ex)

                        # sales_order_obj                 = self.env['sale.order'].search([('name', '=', last_invoice.origin)], order='create_date desc', limit=1)
                        current_package_id = customer.invoice_product_id.id
                        current_package_price = customer.invoice_product_price

                        # updating current package info.
                        customer.update_current_bill_cycle_info(
                            customer=customer,
                            start_date=current_package_start_date,
                            product_id=current_package_id,
                            price=current_package_price,
                        )
                        # updating next package info
                        customer.update_next_bill_cycle_info(
                            customer=customer,
                        )

                        # Adding the package change history
                        package_history_obj = self.env['isp_crm_module.customer_package_history'].search([])
                        created_package_history = package_history_obj.set_package_change_history(customer)

                        # updating opportunity
                        # opportunity = service_req.opportunity_id
                        # opportunity.update({
                        #     'color'                             : 10,
                        #     'current_service_request_id'        : service_req.name,
                        #     'current_service_request_status'    : 'Done',
                        # })

                        # Generate Dynamic Invoice and Send in mail.
                        template_obj = self.env['mail.template'].sudo().search(
                            [('name', '=', 'Send_Service_Request_Mail')], limit=1)

                        # showing warning for not setting ip, subnetmask and gateway
                        # if self.ip is False or self.subnet_mask is False or self.gateway is False:
                        #     raise UserError('Please give all the technical information to mark done this ticket.')

                        # Send mail on mark done
                        if customer_type == "MC":
                            pass
                        else:
                            self.env['isp_crm_module.mail'].service_request_send_email(customer.email, customer_subs_id,
                                                                                       cust_password, str(self.ip),
                                                                                       str(self.subnet_mask),
                                                                                       str(self.gateway),
                                                                                       customer_subs_id,
                                                                                       cust_password_radius,
                                                                                       template_obj)
                            # **Sending mail to TD/RM on mark done on New Connection**
                            template_obj_marked_done = self.env['isp_crm_module.mail'].sudo().search(
                                [('name', '=', 'Ticket_Marked_Done')],
                                limit=1)
                            subject_mail = "Service Delivered"
                            # mark_done_email_name = customer.name
                            # mark_done_email_sub_id =
                            self.env['isp_crm_module.mail'].action_ticket_marked_done_email(subject_mail,
                                                                                            customer.assigned_rm.email,
                                                                                            self.name,
                                                                                            customer.name,
                                                                                            customer.subscriber_id,
                                                                                            customer.current_package_id.name,
                                                                                            template_obj_marked_done)
                else:
                    raise UserError(_("This Opportunity's invoice is neither PAID nor DEFERRED."))
            else:
                raise UserError(
                    _("This Opportunity's invoice has not been created yet. Please create the invoice first ."))

        return True

    # SERVICE REQUEST LOST

    #########