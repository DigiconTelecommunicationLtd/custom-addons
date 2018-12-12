# -*- coding: utf-8 -*-

from datetime import datetime
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
            if customer.current_package_id.id != customer.next_package_id.id:
                # Update Last Package's end date
                last_package_history_obj = package_history_obj.search([
                        ('customer_id', '=', customer.id),
                        ('package_id', '=', customer.current_package_id.id),
                    ],
                    order='create_date desc',
                    limit=1
                )
                last_package_history_obj.update({
                    'end_date' : today,
                })
                # Create new Package History
                return self.create_new_package_history(customer=customer)
        else:
            # Creates Package history if the current customer has no package history
            return self.create_new_package_history(
                customer        = customer,
                package         = customer.current_package_id,
                start_date      = customer.current_package_start_date,
                price           = customer.current_package_price,
                original_price  = customer.current_package_original_price,
            )