# -*- coding: utf-8 -*-
import string
import random
import uuid
import json
from datetime import datetime, timedelta
from odoo import http
from odoo.tools.translate import _
from odoo.exceptions import UserError
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
    DEFAULT_FORGET_PASSWORD_ROUTE = "/selfcare/forget/password"
    DEFAULT_PRODUCT_CATEGORY = "Package"
    DEFAULT_PROFILE_CHANGE_NAME = "Profile Change"
    DEFAULT_JOURNAL_NAME = "Bank"
    DEFAULT_PARTNER_TYPE = "customer"
    DEFAULT_RECEIVE_MONEY_PAYMENT_TYPE = "inbound"
    DEFAULT_PAYMENT_METHOD_TYPE = "inbound"
    DEFAULT_PAYMENT_METHOD_CODE = "manual"
    DEFAULT_INVOICE_STATE = "open"
    DEFAULT_CHANGE_FROM = "immediately"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d"
    SERVICE_TYPE_ID_LIST = [1,8]
    PAYMENT_SERVICE_TYPE_ID = 8
    ITEMS_PER_PAGE = 10


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
        success_msg = ''
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                request.params['login_success'] = True
                redirect = self.DEFAULT_LOGIN_REDIRECT
                return self._login_redirect(uid=uid, redirect=redirect)
            request.uid = old_uid
            context['error'] = _("Wrong login/password")
        context['success_msg'] = _(success_msg)
        return request.render(template, context)

    @http.route('/selfcare/forget/password/', auth='public', methods=["GET", "POST"], website=True, csrf=False)
    def selfcare_forget_password(self, **kw):
        """
        Action to do when user clicks on forget password button.
        :param kw:
        :return:
        """
        # Get the template of the form.
        template      = "isp_crm_module.template_selfcare_forget_password_main"
        context       = {}
        success_msg   = ''
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            login   = request.params['login']
            if login == "New":
                raise UserError('Invalid data provided. Please provide a valid id or email address.')
            check_user = request.env['res.partner'].sudo().search(['|', ('email', '=', str(login)), ('subscriber_id', '=', str(login))], limit=1)
            # Check if user exist.
            if check_user:
                # Get the template of the mail.
                template_obj = request.env['mail.template'].sudo().search(
                    [('name', '=', 'Send_Reset_Password_Link')],
                    limit=1)
                if template_obj:
                    email_to = check_user.email
                    if email_to:
                        request.env['isp_crm_module.mail'].send_reset_password_link_email(check_user, email_to, template_obj)
                        success_msg = 'Reset Password Link sent successfully. Please check your email.'
                    else:
                        context['error'] = _('Could not find any email address for this user.')
                else:
                    context['error'] = _('Mail template not found.')
            else:
                context['error'] = _('No user found with that ID.')
        context['success_msg'] = _(success_msg)
        return request.render(template, context)

    @http.route('/selfcare/reset/password/<string:variable>', auth='public', methods=["GET", "POST"], website=True, csrf=False)
    def selfcare_reset_password(self, **kw):
        """
        Password reset action to perform after user clicks on the reset password link from his/her mail.
        :param kw:
        :return:
        """
        template    = 'isp_crm_module.template_selfcare_reset_password_main'
        login_template = 'isp_crm_module.template_selfcare_login_main'
        context     = {}
        success_msg = ''
        url = "http://localhost:8069"+str(request.httprequest.full_path).split("?")[0]
        check_link = request.env['isp_crm_module.temporary_links'].sudo().search([('link', '=', url)], limit=1)
        if check_link:
            pass
        else:
            context['error'] = _('Invalid reset password link provided')
            return request.render(login_template, context)
        if request.httprequest.method == 'POST':
            if check_link:
                check_user = request.env['res.users'].sudo().search([('partner_id', '=', check_link.name.id)], limit=1)
                if check_user:
                    new_password         = request.params['new_password']
                    confirm_new_password = request.params['confirm_new_password']
                    if new_password == confirm_new_password :
                        check_user._set_password(new_password)
                        success_msg = 'Successfully reset password'
                        context['success_msg'] = _(success_msg)
                        return request.render(login_template, context)
                    else:
                        context['error'] = _("Could not reset password.")
                else:
                    context['error'] = _("User not found.")
            else:
                context['error'] = _("Reset password link is invalid")
        context['success_msg'] = _(success_msg)
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
                invoice_number = False
                invoice_ids = False
                data = dict(request.params)
                session_id = request.session['payment_session_id']
                customer_id = request.session['customer_id']
                invoice_id = request.session['invoice_id']  if ('invoice_id' in request.session) else False
                if invoice_id:
                    # get invoice object and properties
                    invoice_obj = request.env['account.invoice'].sudo().search([('id', '=', invoice_id)], limit=1)
                    invoice_number = invoice_obj.number
                    invoice_ids = invoice_obj.ids

                # customer object
                customer_obj = request.env['res.partner'].sudo().search([('id', '=', customer_id)], limit=1)
                # get journal id
                journal_obj = request.env['account.journal'].sudo().search([('name', '=', self.DEFAULT_JOURNAL_NAME)], limit=1)
                # get payment_method id
                payment_method_obj = request.env['account.payment.method'].sudo().search(
                        [('code', '=', self.DEFAULT_PAYMENT_METHOD_CODE), ('payment_type', '=', self.DEFAULT_PAYMENT_METHOD_TYPE)], limit=1)
                # register payment
                payment_obj = request.env['account.payment'].sudo().search([])

                # TODO (Arif) : Add other info in this reponse of payments
                created_payment_obj = payment_obj.create({
                    'payment_method_id' : payment_method_obj.id,
                    'payment_type' : self.DEFAULT_RECEIVE_MONEY_PAYMENT_TYPE,
                    'partner_type' : self.DEFAULT_PARTNER_TYPE,
                    'partner_id' : customer_id,
                    'amount' : float(data['amount']),
                    'communication' : invoice_number if invoice_number else None,
                    'journal_id' : journal_obj.id,
                    'invoice_ids': [(6, 0, invoice_ids)] if invoice_ids else None,
                })
                # make payment
                if invoice_id:
                    created_payment_obj.action_validate_invoice_payment()
                else:
                    created_payment_obj.post()

                today = datetime.today()
                customers_current_package_end_date_obj = datetime.strptime(customer_obj.current_package_end_date, self.DEFAULT_DATE_FORMAT)

                if today > customers_current_package_end_date_obj:
                    start_date = today.strftime(self.DEFAULT_DATE_FORMAT)
                    # update the bill cycle
                    updated_customer_info = customer_obj.update_current_bill_cycle_info(customer=customer_obj,
                                                                                        start_date=start_date)
                    updated_customer_info = customer_obj.update_next_bill_cycle_info(customer=customer_obj,
                                                                                     start_date=start_date)


            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            context['user'] = logged_in_user
        # removing invoice from sesssion
        # del request.session['invoice_id'] if invoice_id else None
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
                transaction_id = service_type + "_" + amount
                base_url = request.httprequest.url_root
                if int(service_type) in self.SERVICE_TYPE_ID_LIST:
                    invoice_number = request.params["invoice_number"]
                    invoice_id = request.params["invoice_id"]
                    request.session['invoice_id'] = invoice_id
                    invoice_obj = request.env['account.invoice'].search(
                            [('id', '=', invoice_id), ('state', '=', 'open')], limit=1)
                    amount = invoice_obj.amount_total
                    transaction_id = invoice_obj.number

                response_content = self.initiate_session(base_url=base_url, customer=logged_in_user, amount=amount, transaction_id=transaction_id)
                if response_content['status'] == "SUCCESS":
                    template = "isp_crm_module.template_selfcare_user_make_payment"
                    request.session['customer_id'] = logged_in_user.partner_id.id
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

    @http.route(["/selfcare/ticket/list/", "/selfcare/ticket/list/page/<int:page>"], methods=["GET"], website=True)
    def selfcare_ticket_list(self, page=1, **kw):
        context = {}
        content_header = "Tickets List"
        template = "isp_crm_module.template_selfcare_login_main"
        template_name = True

        if self._redirect_if_not_login(req=request):
            template = "isp_crm_module.template_selfcare_user_ticket_list"
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            ticket_obj = request.env['isp_crm_module.helpdesk']
            domain = [('customer', '=', logged_in_user.partner_id.id)]



            tickets_list_count = ticket_obj.sudo().search_count(domain)
            pager = request.website.pager(
                url="/selfcare/ticket/list/",
                total=tickets_list_count,
                page=page,
                step=self.ITEMS_PER_PAGE
            )
            tickets_list = ticket_obj.sudo().search(
                    domain, order='create_date desc',
                    limit=self.ITEMS_PER_PAGE, offset=pager['offset'])

        context['user'] = logged_in_user
        context['full_name'] = logged_in_user.name.title()
        context['customer_id'] = logged_in_user.subscriber_id
        context['content_header'] = content_header
        context['tickets'] = tickets_list
        context['pager'] = pager

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
        context         = {}
        content_header  = "Packages List"
        template        = "isp_crm_module.template_selfcare_login_main"
        template_name   = True
        products        = []

        if self._redirect_if_not_login(req=request):
            template        = "isp_crm_module.template_selfcare_user_package_list"
            user_id         = request.env.context.get('uid')
            logged_in_user  = request.env['res.users'].sudo().browse(user_id)
            product_cat_obj = request.env['product.category'].sudo().search([('name', '=', self.DEFAULT_PRODUCT_CATEGORY)], limit=1)
            products        = request.env['product.product'].sudo().search([('categ_id', '=', product_cat_obj.id)])
            description     = ""
            success_msg     = ""
            active_from     = ""
            if request.httprequest.method == 'POST':
                package_obj             = request.env['product.product'].sudo().search([('id', '=', package_id)])
                post_data               = request.params
                pack_change_problem_obj = request.env['isp_crm_module.helpdesk_problem'].sudo().search([('name', 'like', 'Package Change')], limit=1)

                description = "Change the plan \nFrom : " + logged_in_user.partner_id.current_package_id.name + "\nTo : " + package_obj.name

                if post_data['change_package_from'] == self.DEFAULT_CHANGE_FROM:
                    description += "\nFrom Date : " + post_data['date']
                    active_from  = post_data['date']
                else:
                    description += "\nFrom Next Bill Cycle."
                    active_from  = logged_in_user.partner_id.next_package_start_date



                ticket_type_obj = request.env['isp_crm_module.helpdesk_type'].sudo().search([('name', 'like', 'Package Change')], limit=1)
                ticket_obj = request.env['isp_crm_module.helpdesk'].sudo().search([])
                created_ticket = ticket_obj.create({
                    'customer'      : logged_in_user.partner_id.id,
                    'type'          : ticket_type_obj.id,
                    'problem'       : pack_change_problem_obj.id,
                    'description'   : description,
                })

                # Creating a Package change obj
                package_change_obj = request.env['isp_crm_module.change_package'].sudo().search([])
                created_package_change = package_change_obj.create({
                    'ticket_ref'        : created_ticket.name,
                    'customer_id'       : logged_in_user.partner_id.id,
                    'from_package_id'   : logged_in_user.partner_id.current_package_id.id,
                    'to_package_id'     : package_obj.id,
                    'active_from'       : active_from
                })

                # TODO (Arif) : Have to create a customer invoice status object upon discussion with alam bro

                success_msg = "Your Package change request Successfully enlisted."

        context['csrf_token']       = request.csrf_token()
        context['user']             = logged_in_user
        context['partner']          = logged_in_user.partner_id
        context['full_name']        = logged_in_user.name.title()
        context['customer_id']      = logged_in_user.subscriber_id
        context['content_header']   = content_header
        context['products']         = products
        context['success_msg']      = success_msg

        return json.dumps({
            "response" : True
        })

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

    @http.route("/selfcare/get-invoice/<int:service_type_id>", auth='user', type='http', website=True)
    def selfcare_get_customer_invoice(self, service_type_id, **kw):

        context = {}
        content_header = ""
        customer_obj = request.env['account.invoice']
        user_id = request.env.context.get('uid')
        logged_in_user = request.env['res.users'].sudo().browse(user_id)
        invoice_obj = request.env['account.invoice'].search([
                ('partner_id', '=', logged_in_user.partner_id.id),
                ('state', '=', self.DEFAULT_INVOICE_STATE),
                ('payment_service_id', '=', service_type_id),
            ],
            order='create_date desc',
            limit=1
        )

        context['customer_id'] = logged_in_user.partner_id.id
        context['invoice'] = {
            'id'                : invoice_obj.id,
            'name'              : invoice_obj.name,
            'number'            : invoice_obj.number,
            'amount_total'      : invoice_obj.amount_total,
            'in_service_type'   : True if int(service_type_id) in self.SERVICE_TYPE_ID_LIST else False
        }
        return json.dumps(context)

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

    @http.route("/selfcare/change/password", methods=["GET", "POST"], website=True)
    def selfcare_change_password(self, **kw):
        """
        Change password of a user .
        :param kw:
        :return: view for change_password
        """
        context         = {}
        success_msg     = ''
        content_header  = "Change Password"
        template        = "isp_crm_module.template_selfcare_login_main"
        template_name   = True
        logged_in_user  = ""

        if self._redirect_if_not_login(req=request):
            template        = "isp_crm_module.template_selfcare_change_user_password"
            user_id         = request.env.context.get('uid')
            logged_in_user  = request.env['res.users'].sudo().browse(user_id)

            if request.httprequest.method == 'POST':
                old_password            = request.params['old_password']
                new_password            = request.params['new_password']
                confirm_new_password    = request.params['confirm_new_password']

                find_user               = request.env['res.users'].sudo()._login('isp_crm_customer_profile', logged_in_user.login,
                                                                   old_password)

                if new_password == old_password:
                    if find_user:
                        context['error'] = _("New Password is same as Old Password.")
                    else:
                        context['error'] = _("Old Password does not match .")
                elif new_password == confirm_new_password:
                    if find_user:
                        logged_in_user._set_password(new_password)
                        request.session.logout(keep_db=True)
                        redirect = self.DEFAULT_LOGIN_ROUTE
                        return request.redirect(redirect)
                    else:
                        context['error'] = _("Old Password does not match .")
                else:
                    context['error']            = _("Confirm Password does not match with New Password .")
                    context['csrf_token']       = request.csrf_token()
                    context['user']             = logged_in_user
                    context['full_name']        = logged_in_user.name.title()
                    context['customer_id']      = logged_in_user.subscriber_id
                    context['content_header']   = content_header
                    return request.render(template, context)

        context['csrf_token']       = request.csrf_token()
        context['user']             = logged_in_user
        context['full_name']        = logged_in_user.name.title()
        context['customer_id']      = logged_in_user.subscriber_id
        context['content_header']   = content_header

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
