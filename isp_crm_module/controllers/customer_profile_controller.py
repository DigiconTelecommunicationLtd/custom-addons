# -*- coding: utf-8 -*-
from odoo import http

class CustomerProfile(http.Controller):

    @http.route("/customer/profile/", type='json', auth='user', website=True)
    def customer_profile_show(self, **kw):

        customer_list = http.request.env['res.partner'].search([("id", "=", http.request.env.user[0].id)])


        name = customer_list.name
        is_potential_customer = customer_list.is_potential_customer

        return {

            'user': http.request.env.user,
            'name': name,
            'is_potential_customer': is_potential_customer,

        }

    @http.route("/api/customer/profile/", auth='user', methods=["GET"], website=True)
    def customer_profile_api(self, **kw):
        return http.request.render("isp_crm_module.customer_profile_show")