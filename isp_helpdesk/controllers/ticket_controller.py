# -*- coding: utf-8 -*-
from odoo import http

class TicketController(http.Controller):

    @http.route("/ticket/", auth='user', methods=["GET"], website=True)
    def ticket_list(self, **kw):
        tickets_list = http.request.env['isp_helpdesk.ticket'].search([("customer", "=", http.request.env.user[0].id)])
        return http.request.render("isp_helpdesk.template_ticket_list",
                                   {"user": http.request.env.user, "tickets": tickets_list})

    @http.route("/ticket/create/", auth='user', methods=["GET", "POST"], website=True)
    def ticket_create(self, **kw):
        success_msg = ''
        if http.request.httprequest.method == "POST":
            problem = http.request.params['problem']
            description = http.request.params['description']
            customer = http.request.env.user[0].id
            creating_values = {
                'problem' : problem,
                'description' : description,
                'customer' : customer,
            }
            ticket_obj = http.request.env['isp_helpdesk.ticket'].create(creating_values)
            success_msg = "Ticket Has been created Successfully."
        problems = http.request.env['isp_helpdesk.problem'].search([])
        values = {
            "user": http.request.env.user,
            "problems": problems,
            "success_msg": success_msg
        }
        return http.request.render("isp_helpdesk.template_ticket_create", values)
