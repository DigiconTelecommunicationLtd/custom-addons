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

#0 added
#1 changed
#2 deleted
#4 unchanged

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
    #internal_notes = fields.Text(string="Internal Notes", track_visibility='onchange')
    internal_notes = fields.Html(string="Internal Notes", track_visibility='onchange')
    # technical_info_real_ip = fields.Char(string='Real IP Address')
    # is_real_ip = fields.Boolean(compute='_compute_show_hide')
    #
    # @api.one
    # def _compute_show_hide(self):
    #     self.is_real_ip = False
    #     for product in self.tagged_product_ids:
    #         for attribute in product.attribute_line_ids:
    #             if 'real' in attribute.display_name.lower() and 'ip' in attribute.display_name.lower().lower():
    #                 self.is_real_ip = True
    @api.multi
    def write(self, vals):
        print("from write*****************************************************************")
        print("before",self.product_line)
        print("after", vals)
        if 'product_line' in vals:
            for lines in vals['product_line']:
                print('lines',lines)
                if lines[0]==1:
                    if 'product_uom_qty' in lines[2]:
                        current_quantity=lines[2]['product_uom_qty']
                        self.update_product_quantity(lines[1],current_quantity)

                    else:
                        print('2nd')
                        self.delete_product_quantity(lines[1])
                        self.add_product_quantity(lines[1], 1)

                elif lines[0]==0:
                    product_id = lines[2]['product_id']
                    product_uom_qty = lines[2]['product_uom_qty']
                    print('inside',product_id,product_uom_qty)
                    self.add_product_quantity(product_id,product_uom_qty)

                elif lines[0]==2:
                    self.delete_product_quantity(lines[1])

        res = super(UpdatedServiceRequest, self).write(vals)

        return res

    def update_product_quantity(self,product_id,current_quantity):

        new_available_quantity = None
        quantity = None
        product_line_data=self.env['isp_crm_module.product_line'].search([('id', '=', product_id)], limit=1)
        print("present_quantity", current_quantity)
        # print("past_quantity", product_line_data.product_uom_qty)
        prev_quantity = float(product_line_data.product_uom_qty)
        print("past_quantity", prev_quantity)
        get_product = self.env['stock.quant'].search(
            [('product_id', '=', product_line_data.product_id.id)], order='create_date desc', limit=1)
        print("quantity",get_product)
        if get_product:

            current_stock_quantity = get_product.product_tmpl_id.qty_available
            print("current stock before change", current_stock_quantity)
            # if abs(current_stock_quantity) <= 0.0:
            #     raise UserError('Not enough quantity available in stock.')

            if abs(prev_quantity) > abs(current_quantity):
                quantity = abs(prev_quantity) - abs(current_quantity)
                print("barse", quantity)
                new_available_quantity = abs(current_stock_quantity) + abs(quantity)
                print("barse stock",new_available_quantity)
            elif abs(current_quantity) > abs(prev_quantity):
                quantity = abs(current_quantity) - abs(prev_quantity)
                print("komse",quantity)
                new_available_quantity = abs(current_stock_quantity) - abs(quantity)
                print("komse stock", new_available_quantity)

            if new_available_quantity < 0.0:
                raise UserError('Not enough quantity available in stock.')
            self.update_stock_quantity(new_available_quantity, get_product.product_id.id)


    def add_product_quantity(self,product_id,quantity):
        print('in add product')
        new_available_quantity = None
        get_product = self.env['stock.quant'].search(
            [('product_id', '=', product_id)], order='create_date desc', limit=1)

        if get_product:
            print(get_product)
            current_stock_quantity = get_product.product_tmpl_id.qty_available
            print('current stock quantity',current_stock_quantity)
            print('komse',quantity)
            if abs(current_stock_quantity) <= 0.0:
                raise UserError('Not enough quantity available in stock.')
            elif quantity > abs(current_stock_quantity):
                raise UserError('Not enough quantity available in stock.')
            else:
                new_available_quantity = abs(current_stock_quantity) - abs(quantity)

            if new_available_quantity < 0.0:
                raise UserError('Not enough quantity available in stock.')
            print('new stock',new_available_quantity)
            self.update_stock_quantity(new_available_quantity, get_product.product_id.id)

    def delete_product_quantity(self,product_id):
        print('in delete product')
        print('product')
        new_available_quantity = None
        product_line_data = self.env['isp_crm_module.product_line'].search([('id', '=', product_id)], limit=1)
        print('quantity',product_line_data.product_uom_qty)
        get_product = self.env['stock.quant'].search(
            [('product_id', '=', product_line_data.product_id.id)], order='create_date desc', limit=1)
        if get_product:
            print(get_product)
            current_stock_quantity = get_product.product_tmpl_id.qty_available
            print('current_stock_quantity',current_stock_quantity)
            new_available_quantity = abs(current_stock_quantity) + abs(product_line_data.product_uom_qty)
            print(new_available_quantity)
            self.update_stock_quantity(new_available_quantity, get_product.product_id.id)


    @api.multi
    def update_stock_quantity(self,new_available_quantity,product_id):
        print('new_avilable_quantity',new_available_quantity)
        print('product_id', product_id)
        get_product = self.env['stock.quant'].search(
            [('product_id', '=', product_id)], order='create_date desc', limit=1)
        print('get_product',get_product)
        if get_product:
            inventory_name = str(get_product.product_id.display_name) + "-" + str(
                datetime.now())
            create_inventory = self.env['stock.inventory'].create({
                'name': inventory_name,
                'filter': 'product',
                'product_id': product_id,
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




    @api.multi
    def action_make_service_request_done(self):
        print('*********************** user')
        customer = self.customer.id
        check_customer = self.env['res.partner'].search([('id', '=', customer)], limit=1)
        opportunity = self.env['crm.lead']
        print('customer',customer)
        print('opportunity', opportunity)
        today_new = datetime.now() + timedelta(hours=6)
        today = today_new.date()

        if check_customer:
            invoices = self.env['account.invoice'].search([('partner_id', '=', customer)], order="create_date desc",
                                                          limit=1)
            print('invoices', invoices)
            if invoices:
                # if invoices.is_deferred or invoices.state == INVOICE_PAID_STATUS:
                real_ip = False
                product_name = None
                real_ip_subtotal = 0.0
                reaL_ip_original = 0.0
                if invoices.is_deferred or invoices.state == INVOICE_PAID_STATUS:
                    self.invoice_state = invoices.state
                    opportunity.action_set_won()
                    opportunity.action_create_new_service_request()

                    for service_req in self:
                        # condition to check real ip
                        for productline in service_req.order_line:
                            if 'real' in productline.product_id.name.lower() and 'ip' in productline.product_id.name.lower():
                                if  self.technical_info_real_ip == False or  len(self.technical_info_real_ip)==0:
                                    raise UserError('Real IP found in order line. Please fill up REAL IP section in technical info')
                        # update the stage of this service request to done

                        cust_password_radius = None
                        last_stage_obj = self.env['isp_crm_module.stage'].search([('name', '=', 'Done')], limit=1)

                        # Deduct quantity from stock.
                        # try:
                        #     for product in service_req.product_line:
                        #         quantity = product.product_uom_qty
                        #         get_product = self.env['stock.quant'].search(
                        #             [('product_id', '=', product.product_id.id)], order='create_date desc', limit=1)
                        #         if get_product:
                        #             current_stock_quantity = get_product.quantity
                        #             if abs(current_stock_quantity) <= 0.0:
                        #                 raise UserError('Not enough quantity available in stock.')
                        #             new_available_quantity = abs(current_stock_quantity) - abs(quantity)
                        #             if new_available_quantity:
                        #                 inventory_name = str(get_product.product_id.display_name) + "-" + str(
                        #                     datetime.now())
                        #                 create_inventory = self.env['stock.inventory'].create({
                        #                     'name': inventory_name,
                        #                     'filter': 'product',
                        #                     'product_id': get_product.product_id.id,
                        #                     'accounting_date': datetime.today(),
                        #                 }).action_start()
                        #                 get_inventory = self.env['stock.inventory'].search(
                        #                     [('name', '=', inventory_name)], order='create_date desc', limit=1)
                        #                 if get_inventory:
                        #                     get_inventory_lines = get_inventory.line_ids
                        #                     for line in get_inventory_lines:
                        #                         line.update({
                        #                             'product_qty': float(abs(new_available_quantity))
                        #                         })
                        #                     get_inventory.action_done()
                        # except Exception as ex:
                        #     print(ex)

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
                        print('service_req.customer',customer)
                        # format sequence number based on lead type
                        get_opportunity = self.env['crm.lead'].search([('partner_id', '=', customer.id)], limit=1)
                        print('get_opportunity', get_opportunity)
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
                        print('customer_type', customer_type)
                        if customer_type == 'MR':

                            result_radius = False
                            for productline in service_req.order_line:
                                if productline.product_id.categ_id.name == DEFAULT_PACKAGE_CAT_NAME:
                                    cust_password_radius = self._create_random_password(size=DEFAULT_PASSWORD_SIZE)
                                    #make sure real ip does not hit radius
                                    if 'real' in productline.product_id.name.lower() and 'ip' in productline.product_id.name.lower():
                                        real_ip = True
                                        real_ip_subtotal = productline.price_subtotal
                                        reaL_ip_original = productline.product_id.list_price
                                    else:
                                        product_name = productline.product_id.name


                            print('real_ip',real_ip)
                            print('product', product_name)
                            if real_ip!= True:
                                result_radius = create_radius_user(customer_subs_id, cust_password_radius,
                                                                   product_name,
                                                                   customer._get_package_end_date(
                                                                       fields.Date.today()), customer.id)

                            else:
                                #real ip process
                                result_radius= create_radius_user_real_ip(customer_subs_id,cust_password_radius,product_name,customer._get_package_end_date(
                                                                       fields.Date.today()),self.technical_info_real_ip.strip())


                            if result_radius != 'success':
                                raise UserError('Radius server issue: ' + result_radius)
                            else:
                                # service_activation_date and billing_start_date is not being set for afew user group
                                # solution 1: updating it with sudo command. Not yet implemented
                                # today_new = datetime.now() + timedelta(hours=6)
                                # today = today_new.date()
                                customer.sudo().update({
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
                                    'real_ip_subtotal':real_ip_subtotal,
                                     'has_real_ip':real_ip,
                                    'reaL_ip_original':reaL_ip_original,
                                    'is_deferred':invoices.is_deferred,
                                    'isp_invoice_id':invoices.id,
                                    'is_existing_user':False,
                                    'new_customer_date':today.strftime(DEFAULT_DATE_FORMAT)
                                })


                        # Not a retail customer so go as it was before
                        else:
                            customer.sudo().update({
                                'is_potential_customer': False,
                                'subscriber_id': customer_subs_id,
                                'technical_info_ip': self.ip,
                                'technical_info_subnet_mask': self.subnet_mask,
                                'technical_info_gateway': self.gateway,
                                'description_info': self.description,
                                'service_activation_date': fields.Date().today(),
                                'billing_start_date': current_package_start_date,
                                'isp_invoice_id': invoices.id,
                                'is_deferred': invoices.is_deferred,
                                'is_existing_user': False,
                                'new_customer_date': today.strftime(DEFAULT_DATE_FORMAT)

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
                        #code to fix service request to customer carry forward
                        customer.update({
                            'comment': self.internal_notes
                        })

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
                        if customer_type == "MC" or customer_type == "MS":
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
    @api.onchange('stage')
    def stage_onchange(self):
        value = self.stage.name
        sequence = self.stage.sequence
        if value == 'Done':
            raise UserError('System does not allow you to drag record unless mark done is confirmed by action.')
        if value == 'Bill Date Confirmation':
            raise UserError('System does not allow you to drag record unless it is send by action.')
        elif value == 'Queue':
            raise UserError('System does not allow you to drag record to queue stage.')
        elif value == 'New':
            raise UserError('System does not allow you to drag record to new stage.')
        elif value == 'Mark Lost':
            raise UserError('System does not allow you to drag record to mark lost stage.')
        elif self._origin.is_done:
            raise UserError(
                'System does not allow you to change stage once it is marked done.')

