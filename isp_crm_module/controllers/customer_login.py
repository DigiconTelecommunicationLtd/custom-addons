# -*- coding: utf-8 -*-
import string
import random
import uuid
from odoo import http
from odoo.tools.translate import _
from passlib.context import CryptContext
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response





class SelfcareController(http.Controller):
    DEFAULT_LOGIN_REDIRECT = "/selfcare"


    def _login_redirect(self, redirect=None):
        if redirect is None:
            redirect = self.DEFAULT_LOGIN_REDIRECT
        request.redirect(redirect)

    @http.route("/selfcare/login", auth='public', methods=["GET", "POST"], website=True, csrf=False)
    def selfcare_login(self, **kw):
        template = "isp_crm_module.template_selfcare_login_main"
        context = {}
        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                request.params['login_success'] = True
                return http.redirect_with_hash(self._login_redirect())
            request.uid = old_uid
            context['error'] = _("Wrong login/password")

        return request.render(template, context)

    @http.route("/selfcare", auth='public', methods=["GET"], website=True)
    def selfcare_home(self, **kw):
        context = {}
        msg = ""
        full_name = ""
        template = "isp_crm_module.template_selfcare_login_main"

        if request.env.context.get('uid') is None:
            msg = "Not Logged In..."
        else:
            msg = "Logged In..."
            user_id = request.env.context.get('uid')
            full_name = user_id
            template = "isp_crm_module.template_selfcare_main_layout"

        context['msg'] = msg
        context['full_name'] = full_name
        return request.render(template, context)