# -*- coding: utf-8 -*-
from odoo import http

class CustomerProfileTicket(http.Controller):

    @http.route("/customer/profile/ticket/", type='json', auth='user', website=True)
    def ticket_list(self, **kw):
        problemName = list()
        problemDescription = list()
        problemStage = list()
        tickets_list = http.request.env['isp_crm_module.service_request'].search([("customer", "=", http.request.env.user[0].id)])

        for ticket in tickets_list:
            problemName.append(ticket.problem)
            problemDescription.append(ticket.description)
            problemStage.append(ticket.stage.name)

        return {

            'user': http.request.env.user,
            'problemName': problemName,
            'problemDescription': problemDescription,
            'problemStage': problemStage,

        }

    @http.route("/call/api/customer/profile/ticket/", auth='user', methods=["GET"], website=True)
    def ticket_list_call_api(self, **kw):
        return http.request.render("isp_crm_module.template_ticket_list")



    @http.route("/customer/profile/ticket/create/", type='json', auth='user', website=True)
    def ticket_create(self, **kw):
        success_msg = ''

        # Fetch input json data sent from js

        problem = kw.get('problem')
        description = kw.get('description')
        print(problem)
        customer = http.request.env.user[0].id
        stage = http.request.env['isp_crm_module.stage'].search(
            [("sequence", "=", 1)])
        creating_values = {
            'problem': problem,
            'description': description,
            'customer': customer,
            'stage': stage[0].id,
        }
        ticket_obj = http.request.env['isp_crm_module.service_request'].create(creating_values)
        success_msg = "Ticket Has been created Successfully."

        return {

            'success_msg': success_msg

        }

    @http.route("/call/api/customer/profile/ticket/create/", auth='user', methods=["GET"], website=True)
    def ticket_create_call_api(self, **kw):
        success_msg = ''
        problems = http.request.env['isp_crm_module.problem'].search([])
        values = {
            "user": http.request.env.user,
            "problems": problems,
            'success_msg': success_msg,
        }
        return http.request.render("isp_crm_module.template_ticket_create", values)
