# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, _


class CustomerPackageHistory(models.Model):
    """Saves the customer Package history"""
    _name = 'isp_crm_module.customer_package_history'
    _description = "Customer Package history"
    _order = "create_date desc, name, id"

    name = fields.Char("Name", default='', required=False)
    customer_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)],
                               track_visibility='onchange')
    package_id = fields.Many2one('product.product', string='Package', domain=[('sale_ok', '=', True)],
                                      change_default=True, ondelete='restrict')
    start_date = fields.Date('Package Start Date', default=None)
    end_date = fields.Date('Package End Date', default=None)
    price = fields.Float("Package's Price", required=True,
                                      digits=dp.get_precision('Product Price'), default=0.0)
    original_price = fields.Float("Package's Original Price", required=True,
                                               digits=dp.get_precision('Product Price'), default=0.0)


    def create_new_package_history(self, customer, package=None, start_date=None, price=None, original_price=None):
        """
        Returns created package history according to given customer and package info
        :param customer: customer obj
        :param package: package obj
        :param start_date: start date of the package
        :param price: price of the package
        :param original_price: original price of the package
        :return: package history object
        """

        if original_price or customer.next_package_original_price !=0:
            if original_price !=0:
                pass
            else:
                original_price = customer.invoice_product_original_price
        else:
            # sale_order_lines = customer.next_package_sales_order_id.order_line
            # original_price = 0.0
            # for sale_order_line in sale_order_lines:
            #     discount = (sale_order_line.discount * sale_order_line.price_subtotal) / 100.0
            #     original_price_sale_order_line = sale_order_line.price_subtotal + discount
            #     original_price = original_price + original_price_sale_order_line
            original_price = customer.invoice_product_original_price

        if package:
            original_price = package.list_price
        package_history_obj = self.env['isp_crm_module.customer_package_history']
        # Create new Package history for next package
        new_package_history = package_history_obj.create({
            'customer_id': customer.id,
            'package_id': package.id if package else customer.next_package_id,
            'start_date': start_date if start_date else customer.next_package_start_date,
            'price': price if price else customer.next_package_price,
            'original_price': original_price if original_price else customer.next_package_original_price,
        })
        return new_package_history

    def set_package_change_history(self, customer):
        """
        Sets package changes history for a customer
        :param customer: Customer for whom the package history has to create
        :return: package history object
        """
        today = datetime.today().strftime('%Y-%m-%d')
        package_history_obj = self.env['isp_crm_module.customer_package_history']
        customer_package_history_count = package_history_obj.search_count([
            ('customer_id', '=', customer.id),
        ])
        if customer_package_history_count > 0:
            # Get Last Package change request of the customer
            package_change_req = self.env['isp_crm_module.change_package'].search([
                        ('customer_id', '=', customer.id),
                    ],
                    order='create_date desc',
                    limit=1
                )
            tomorrow = date.today() + timedelta(days=1)
            active_date = 1
            # Check if any package change request has been made recently.
            if package_change_req:
                package_change_req_active_date = datetime.strptime(package_change_req.active_from, "%Y-%m-%d").date()
                active_date = package_change_req_active_date - tomorrow
                active_date = int(abs(active_date.days))
            if active_date == 0 or customer.current_package_id.id != customer.next_package_id.id:
                # Update Last Package's end date
                last_package_history_obj = package_history_obj.search([
                        ('customer_id', '=', customer.id),
                        # ('package_id', '=', customer.current_package_id.id),
                    ],
                    order='create_date desc',
                    limit=1
                )
                last_package_history_obj.update({
                    'end_date' : today,
                })
                # Create new Package History
                if active_date == 0 and package_change_req:
                    return self.create_new_package_history(customer=customer, package=package_change_req.to_package_id, start_date= str(datetime.strptime(package_change_req.active_from, "%Y-%m-%d").date()))
                else:
                    return self.create_new_package_history(customer=customer)
        else:
            # sale_order_lines = customer.current_package_sales_order_id.order_line
            # original_price = 0.0
            # for sale_order_line in sale_order_lines:
            #     discount = (sale_order_line.discount * sale_order_line.price_subtotal)/100.0
            #     original_price_sale_order_line = sale_order_line.price_subtotal + discount
            #     original_price = original_price + original_price_sale_order_line
            original_price = customer.invoice_product_original_price
            # Creates Package history if the current customer has no package history
            return self.create_new_package_history(
                customer        = customer,
                package         = customer.current_package_id,
                start_date      = customer.current_package_start_date,
                price           = customer.current_package_price,
                original_price  = original_price,
            )