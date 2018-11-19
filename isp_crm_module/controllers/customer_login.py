# -*- coding: utf-8 -*-
import string
import random
import uuid
from odoo import http
from odoo.tools.translate import _
from passlib.context import CryptContext
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response
from odoo.addons.web.controllers.main import Home
from .payment_controller import PaymentController


class SelfcareController(PaymentController):

    DEFAULT_SERVER_LOC = "http://localhost:8069"
    DEFAULT_LOGIN_REDIRECT = "/selfcare"
    DEFAULT_LOGIN_ROUTE = "/selfcare/login"
    DEFAULT_LOGOUT_ROUTE = "/selfcare/logout"
    DEFAULT_PRODUCT_CATEGORY = "Package"
    DEFAULT_PROFILE_CHANGE_NAME = "Profile Change"

    def _redirect_if_not_login(self, req):
        if req.env.context.get('uid') is None:
            redirect = self.DEFAULT_LOGOUT_ROUTE
            return req.redirect(redirect)
        return True

    def _login_redirect(self, uid, redirect=None):
        if not redirect and not request.env['res.users'].sudo().browse(uid):
            return request.redirect(self.DEFAULT_LOGOUT_ROUTE)
        return request.redirect(redirect)

    @http.route("/selfcare/login", auth='public', methods=["GET", "POST"], website=True, csrf=False)
    def selfcare_login(self, **kw):
        template = "isp_crm_module.template_selfcare_login_main"
        context = {}
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                request.params['login_success'] = True
                redirect = self.DEFAULT_LOGIN_REDIRECT
                return self._login_redirect(uid=uid, redirect=redirect)
            request.uid = old_uid
            context['error'] = _("Wrong login/password")

        return request.render(template, context)

    @http.route('/selfcare/logout', methods=["GET"], auth="public", website=True)
    def logout(self):
        request.session.logout(keep_db=True)
        redirect = self.DEFAULT_LOGIN_ROUTE
        return request.redirect(redirect)


    @http.route("/selfcare/profile", auth='user', methods=["GET"], website=True)
    def selfcare_profile(self, **kw):
        context = {}
        content_header = "User Profile"

        template = "isp_crm_module.template_selfcare_login_main"
        if self._redirect_if_not_login(req=request):
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            template = "isp_crm_module.template_selfcare_user_profile"
            context['user'] = logged_in_user
            context['full_name'] = logged_in_user.name.title()
            context['customer_id'] = logged_in_user.subscriber_id
            context['image'] = logged_in_user.image
            context['content_header'] = content_header

        return request.render(template, context)

    @http.route("/selfcare/make-payment/success", auth='user', methods=["GET", "POST"], website=True, csrf=False)
    def selfcare_payment_success(self, **kw):
        context = {}
        content_header = "Success"
        template = "isp_crm_module.template_selfcare_user_make_payment_success"
        template_name = True

        if self._redirect_if_not_login(req=request):
            if request.httprequest.method == 'POST':
                data = request.params
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            context['user'] = logged_in_user

        context['content_header'] = content_header
        return request.render(template, context)

    @http.route("/selfcare/make-payment/failure", auth='user', methods=["GET", "POST"], website=True, csrf=False)
    def selfcare_payment_failure(self, **kw):
        context = {}
        content_header = "Failure"
        template = "isp_crm_module.template_selfcare_user_make_payment_failure"
        template_name = True

        if self._redirect_if_not_login(req=request):
            if request.httprequest.method == 'POST':
                data = request.params
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            context['user'] = logged_in_user

        context['content_header'] = content_header
        return request.render(template, context)

    @http.route("/selfcare/payment", auth='user', methods=["GET", "POST"], website=True, csrf=False)
    def selfcare_payment(self, **kw):
        context = {}
        content_header = "User Payment"
        template = "isp_crm_module.template_selfcare_login_main"
        template_name = True

        if self._redirect_if_not_login(req=request):
            template = "isp_crm_module.template_selfcare_user_payment"
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)

            if request.httprequest.method == 'POST':
                amount = request.params["amount"]
                service_type = request.params["service_type"]
                response_content = self.initiate_session(customer=logged_in_user, amount=amount, transaction_id="12345")
                if response_content['status'] == "SUCCESS":
                    template = "isp_crm_module.template_selfcare_user_make_payment"
                    request.session['payment_session_id'] = response_content['sessionkey']
                    context['cards'] = response_content["desc"]
                    context['redirect_gateway'] = response_content["redirectGatewayURL"]

                    amex_card = {
                        "name" : "Amex Cards",
                        "img_src" : "/isp_crm_module/static/src/assets/images/amex.png",
                        "gateway_link" : response_content["redirectGatewayURL"] + response_content["gw"]["amex"],
                    }

                    visa_card = {
                        "name": "Visa Cards",
                        "img_src": "/isp_crm_module/static/src/assets/images/visa.png",
                        "gateway_link": response_content["redirectGatewayURL"] + response_content["gw"]["visa"],
                    }

                    master_card = {
                        "name": "Master Cards",
                        "img_src": "/isp_crm_module/static/src/assets/images/master.png",
                        "gateway_link": response_content["redirectGatewayURL"] + response_content["gw"]["master"],
                    }

                    mobile_banking = {
                        "name": "Mobile Banking",
                        "img_src": "/isp_crm_module/static/src/assets/images/mobilebanking.png",
                        "gateway_link": response_content["redirectGatewayURL"] + response_content["gw"]["mobilebanking"],
                    }


                    context['gateway_list'] = [amex_card, visa_card, master_card, mobile_banking]

                    # TODO (Arif): take the pic from the local and fit it on the gateway list.
                    # TODO (Arif) : redirect to the gateway list page.
                    template_name = False
                    # return request.redirect(response_content["redirectGatewayURL"] + response_content["gw"]["mobilebanking"])


            context['user'] = logged_in_user
            context['full_name'] = logged_in_user.name.title()
            context['customer_id'] = logged_in_user.subscriber_id
            context['image'] = logged_in_user.image
            context['content_header'] = content_header
            context['template_name'] = template_name
            context['service_list'] = request.env['isp_crm_module.selfcare_payment_service'].sudo().search([])


        return request.render(template, context)

    @http.route("/selfcare/ticket/create", methods=["GET", "POST"], website=True)
    def selfcare_ticket_create(self, **kw):
        context = {}
        success_msg = ''
        content_header = "Create a Ticket"
        template = "isp_crm_module.template_selfcare_login_main"
        template_name = True

        if self._redirect_if_not_login(req=request):
            template = "isp_crm_module.template_selfcare_user_ticket_create"
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            problems = request.env['isp_crm_module.helpdesk_problem'].sudo().search([])
            if request.httprequest.method == 'POST':
                problem_id = request.params['problem_id']
                description = request.params['description']

                ticket_obj = request.env['isp_crm_module.helpdesk'].sudo().search([])
                created_ticket = ticket_obj.create({
                    'customer' : logged_in_user.partner_id.id,
                    'problem' : problem_id,
                    'description' : description,
                })
                success_msg = "Your Ticket has been Created Successfully"
                #TODO (Arif): Sending mail and other things according to SRS

        context['csrf_token'] = request.csrf_token()
        context['user'] = logged_in_user
        context['full_name'] = logged_in_user.name.title()
        context['customer_id'] = logged_in_user.subscriber_id
        context['content_header'] = content_header
        context['problems_list'] = problems
        context['success_msg'] = success_msg

        return request.render(template, context)

    @http.route("/selfcare/ticket/list", methods=["GET"], website=True)
    def selfcare_ticket_list(self, **kw):
        context = {}
        content_header = "Tickets List"
        template = "isp_crm_module.template_selfcare_login_main"
        template_name = True

        if self._redirect_if_not_login(req=request):
            template = "isp_crm_module.template_selfcare_user_ticket_list"
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            tickets_list = request.env['isp_crm_module.helpdesk'].sudo().search([('customer', '=', logged_in_user.partner_id.id)])

        context['user'] = logged_in_user
        context['full_name'] = logged_in_user.name.title()
        context['customer_id'] = logged_in_user.subscriber_id
        context['content_header'] = content_header
        context['tickets'] = tickets_list

        return request.render(template, context)

    @http.route("/selfcare/change-package", methods=["GET"], website=True)
    def selfcare_change_package_get(self, **kw):
        """
        Creates tickets for changing the plans
        :param kw:
        :return: view for showing the plans list
        """
        context = {}
        content_header = "Packages List"
        template = "isp_crm_module.template_selfcare_login_main"
        template_name = True
        products = []

        if self._redirect_if_not_login(req=request):
            template = "isp_crm_module.template_selfcare_user_package_list"
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            product_cat_obj = request.env['product.category'].sudo().search(
                    [('name', '=', self.DEFAULT_PRODUCT_CATEGORY)], limit=1)
            products = request.env['product.product'].sudo().search([('categ_id', '=', product_cat_obj.id)])
            description = ""
            success_msg = ""

        context['csrf_token'] = request.csrf_token()
        context['user'] = logged_in_user
        context['partner'] = logged_in_user.partner_id
        context['full_name'] = logged_in_user.name.title()
        context['customer_id'] = logged_in_user.subscriber_id
        context['content_header'] = content_header
        context['products'] = products
        context['success_msg'] = success_msg

        return request.render(template, context)


    @http.route("/selfcare/change-package/<int:package_id>", methods=["POST"], website=True)
    def selfcare_change_package(self, package_id=None, **kw):
        context = {}
        content_header = "Packages List"
        template = "isp_crm_module.template_selfcare_login_main"
        template_name = True
        products = []

        if self._redirect_if_not_login(req=request):
            template = "isp_crm_module.template_selfcare_user_package_list"
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            product_cat_obj = request.env['product.category'].sudo().search([('name', '=', self.DEFAULT_PRODUCT_CATEGORY)], limit=1)
            products = request.env['product.product'].sudo().search([('categ_id', '=', product_cat_obj.id)])
            description = ""
            success_msg = ""
            if request.httprequest.method == 'POST':
                package_obj = request.env['product.product'].sudo().search([('id', '=', package_id)])
                pack_change_problem_obj = request.env['isp_crm_module.helpdesk_problem'].sudo().search([('name', 'like', 'Package Change')], limit=1)

                description = "Change the plan \nFrom : " + logged_in_user.partner_id.current_package_id.name + "\nTo : " + package_obj.name
                ticket_type_obj = request.env['isp_crm_module.helpdesk_type'].sudo().search([('name', 'like', 'Package Change')], limit=1)
                ticket_obj = request.env['isp_crm_module.helpdesk'].sudo().search([])
                created_ticket = ticket_obj.create({
                    'customer': logged_in_user.partner_id.id,
                    'type': ticket_type_obj.id,
                    'problem': pack_change_problem_obj.id,
                    'description': description,
                })
                success_msg = "Your Package change request Successfully enlisted."

        context['csrf_token'] = request.csrf_token()
        context['user'] = logged_in_user
        context['partner'] = logged_in_user.partner_id
        context['full_name'] = logged_in_user.name.title()
        context['customer_id'] = logged_in_user.subscriber_id
        context['content_header'] = content_header
        context['products'] = products
        context['success_msg'] = success_msg

        return request.render(template, context)

    @http.route("/selfcare/profile/update", methods=["GET", "POST"], website=True)
    def selfcare_profile_update(self, **kw):
        context = {}
        success_msg = ''
        content_header = "Update Your Profile"
        template = "isp_crm_module.template_selfcare_login_main"
        template_name = True

        if self._redirect_if_not_login(req=request):
            template = "isp_crm_module.template_selfcare_user_profile_update"
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            problems = request.env['isp_crm_module.helpdesk_problem'].sudo().search([('name', '=', self.DEFAULT_PROFILE_CHANGE_NAME)])
            if request.httprequest.method == 'POST':
                problem_id = request.params['problem_id']
                description = request.params['description']

                ticket_obj = request.env['isp_crm_module.helpdesk'].sudo().search([])
                created_ticket = ticket_obj.create({
                    'customer': logged_in_user.partner_id.id,
                    'problem': problem_id,
                    'description': description,
                })
                success_msg = "Profile Update Ticket has been Created."
                # TODO (Arif): Sending mail and other things according to SRS

        context['csrf_token'] = request.csrf_token()
        context['user'] = logged_in_user
        context['full_name'] = logged_in_user.name.title()
        context['customer_id'] = logged_in_user.subscriber_id
        context['content_header'] = content_header
        context['problems_list'] = problems
        context['success_msg'] = success_msg

        return request.render(template, context)

    @http.route("/selfcare", methods=["GET"], website=True)
    def selfcare_home(self, **kw):
        context = {}
        content_header = "Hellllooooo Template"

        template = "isp_crm_module.template_selfcare_login_main"
        if self._redirect_if_not_login(req=request):
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            template = "isp_crm_module.template_selfcare_main_layout"
            context['user'] = logged_in_user
            context['full_name'] = logged_in_user.name.title()
            context['customer_id'] = logged_in_user.subscriber_id
            context['image'] = logged_in_user.image
            context['content_header'] = content_header

        return request.render(template, context)