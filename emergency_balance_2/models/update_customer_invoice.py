# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
from datetime import datetime, timezone, timedelta, date
from odoo.exceptions import Warning, UserError

DEFAULT_PACKAGES_CATEGORY_NAME = 'Packages'
REQUIRE_APPROVAL = 1
APPROVED = 2
NEED_APPROVAL = 3
class UpdateCustomerInvoice(models.Model):
    _inherit = "account.invoice"
    require_approval = fields.Boolean(string='approval?',
                             track_visibility='onchange',default=False)
    approval_reason = fields.Char(string='reason')
    status = fields.Integer(default=2)
    @api.onchange('date_due')
    def date_due_thing(self):
        for record in self:
            if record.is_deferred == True:
                if str(record.date_due)!= 'False':
                    due_date_obj = datetime.strptime(record.date_due, DEFAULT_DATE_FORMAT)
                else:
                    if record.is_deferred == True:
                        raise UserError(_('Please Enter a Valid Due Date!'))
                today_new = datetime.now() + timedelta(hours=6)
                #diff =abs((due_date_obj - today_new).days)
                diff =(due_date_obj - today_new).days
                diff = diff + 1
                if diff > 10:
                   record.status = REQUIRE_APPROVAL
                else:
                    record.status = APPROVED
                print(today_new)
                print (due_date_obj)
                print(str(record.status))
                # modified_date_obj = due_date_obj + timedelta(days=1, hours=6)
                # record.new_next_start_date = modified_date_obj.strftime(DEFAULT_DATE_FORMAT)
                # print(record.date_due)


    @api.one
    def review_for_defer(self):
        for record in self:
            record.status = NEED_APPROVAL
            print(record.status)
            template_obj_new_service_request = self.env['emergency_balance.mail'].sudo().search(
                [('name', '=', 'new_reminder_for_deferred_approval_mail')],
                limit=1)

            product_name=str(record.invoice_line_ids[0].product_id.name)
            product_price =record.invoice_line_ids[0].quantity * record.invoice_line_ids[0].price_unit

            line = record.invoice_line_ids[0]
            price_subtotal = line.quantity * line.price_unit
            discount = (price_subtotal * line.discount) / 100
            price_subtotal = price_subtotal - discount

            due_date_obj = datetime.strptime(record.date_due, DEFAULT_DATE_FORMAT)
            modified_date_obj = due_date_obj + timedelta(days=1, hours=6)
            number_of_days = (modified_date_obj - datetime.now()).days


            self.env['emergency_balance.mail'].action_send_defer_review_email(str(record.name),
                                                                 record.partner_id.name,
                                                                 product_name,
                                                                 str(price_subtotal),
                                                                 str(record.approval_reason),
                                                                 str(number_of_days),
                                                                 template_obj_new_service_request
                                                                 )


    @api.one
    def approve_defer(self):
        for record in self:
            record.status = APPROVED
            print(record.status)

    @api.multi
    def action_invoice_paid(self):
        # Updating the package change info
        if self.payment_service_id.id == self.PAYMENT_SERVICE_TYPE_ID:
            last_package_change_obj = self.env['isp_crm_module.change_package'].sudo().search(
                [('customer_id', '=', self.partner_id.id)], order='create_date desc', limit=1)
            if last_package_change_obj:
                last_package_change_obj.update({
                    'state': 'invoice_paid',
                    'is_invoice_paid': True
                })

        for line in self.invoice_line_ids:
            print('******from action paid**********', line.product_id.categ_id.name, line.quantity)
            if line.product_id.categ_id.name=='OFC':
                print('******from action paid**********',line.product_id.categ_id.name,line.quantity)
                self.add_product_quantity(line.product_id.id, line.quantity)

                # get_product = self.env['stock.quant'].search(
                #     [('product_id', '=', line.product_id.id)], order='create_date desc', limit=1)
                # print(get_product)
                # current_stock_quantity = get_product.product_tmpl_id.qty_available
                # print('current stock quantity', current_stock_quantity)


        super(UpdateCustomerInvoice, self).action_invoice_paid()
        return True

    # @api.model
    # def create(self, vals):
    #     #TODO:FIX THIS FOR ONLY STOCKABLE
    #     print("from invoice create*****************************************************************")
    #     print("before", self.invoice_line_ids)
    #     print("after", vals['invoice_line_ids'])
    #     if 'invoice_line_ids' in vals:
    #         for lines in vals['invoice_line_ids']:
    #             print(lines)
    #             if lines[0] == 1:
    #                 current_quantity = lines[2]['quantity']
    #
    #                 self.update_product_quantity(lines[1], current_quantity)
    #
    #             elif lines[0] == 0:
    #                 product_id = lines[2]['product_id']
    #                 product_uom_qty = lines[2]['quantity']
    #                 print('inside', product_id, product_uom_qty)
    #                 self.add_product_quantity(product_id, product_uom_qty)
    #
    #             elif lines[0] == 2:
    #                 self.delete_product_quantity(lines[1])
    #
    #     return super(UpdateCustomerInvoice, self).create(vals)


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

            if new_available_quantity <= 0.0:
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


