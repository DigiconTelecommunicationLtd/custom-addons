# -*- coding: utf-8 -*-
from odoo import http

class CustomerProfileTicket(http.Controller):

    @http.route("/customer/profile/ticket/", auth='user', methods=["GET"], website=True)
    def ticket_list(self, **kw):
        tickets_list = http.request.env['isp_crm_module.service_request'].search([("customer", "=", http.request.env.user[0].id)])
        return http.request.render("isp_crm_module.template_ticket_list",
                                   {"user": http.request.env.user, "tickets": tickets_list})

    @http.route("/customer/profile/ticket/create/", auth='user', methods=["GET", "POST"], website=True)
    def ticket_create(self, **kw):
        success_msg = ''
        if http.request.httprequest.method == "POST":
            problem = http.request.params['problem']
            problemname = http.request.env['isp_crm_module.problem'].search(
                [("id", "=", problem)])
            description = http.request.params['description']
            customer = http.request.env.user[0].id
            stage = http.request.env['isp_crm_module.stage'].search(
                [("sequence", "=", 1)])
            creating_values = {
                'problem' : problemname[0].name,
                'description' : description,
                'customer' : customer,
                'stage': stage[0].id,
            }
            ticket_obj = http.request.env['isp_crm_module.service_request'].create(creating_values)
            success_msg = "Ticket Has been created Successfully."
        problems = http.request.env['isp_crm_module.problem'].search([])
        values = {
            "user": http.request.env.user,
            "problems": problems,
            "success_msg": success_msg
        }
        return http.request.render("isp_crm_module.template_ticket_create", values)
