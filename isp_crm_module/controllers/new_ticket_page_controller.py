# -*- coding: utf-8 -*-
from odoo import http

class NewTicketPage(http.Controller):

    @http.route("/ticket/", auth='user', methods=["GET"], website=True)
    def ticket_list(self, **kw):
        logincode = http.request.httprequest.cookies.get('login_token')
        isloggedin = http.request.env['isp_crm_module.track_login'].search([("logincode", "=", logincode)])

        if len(isloggedin) < 1:
            return http.request.render("isp_crm_module.customer_login")
        else:
            tickets_list = http.request.env['isp_crm_module.service_request'].search([("customer", "=", http.request.env.user[0].id)])
            return http.request.render("isp_crm_module.isp_crm_template_ticket_list",
                                       {"user": http.request.env.user, "tickets": tickets_list})

    @http.route("/ticket/create/", auth='user', methods=["GET", "POST"], website=True)
    def ticket_create(self, **kw):
        success_msg = ''
        if http.request.httprequest.method == "POST":
            problem = http.request.params['problem']
            description = http.request.params['description']
            customer = http.request.env.user[0].id
            stage = http.request.env['isp_crm_module.stage'].search([("sequence", "=", 1)])
            creating_values = {
                'problem': problem,
                'description': description,
                'customer': customer,
                'is_helpdesk_ticket': True,
                'stage':stage[0].id,
            }
            ticket_obj = http.request.env['isp_crm_module.service_request'].create(creating_values)
            success_msg = "Ticket Has been created Successfully."
        problems = http.request.env['isp_crm_module.problem'].search([])
        values = {
            "user": http.request.env.user,
            "problems": problems,
            "success_msg": success_msg
        }
        logincode = http.request.httprequest.cookies.get('login_token')
        isloggedin = http.request.env['isp_crm_module.track_login'].search([("logincode", "=", logincode)])

        if len(isloggedin) < 1:
            return http.request.render("isp_crm_module.customer_login")
        else:
            return http.request.render("isp_crm_module.isp_crm_new_ticket", values)