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


class SelfcareController(Home):

    DEFAULT_LOGIN_REDIRECT = "/selfcare"
    DEFAULT_LOGIN_ROUTE = "/selfcare/login"
    DEFAULT_LOGOUT_ROUTE = "/selfcare/logout"

    def _redirect_if_not_login(self, req):
        if req.env.context.get('uid') is None:
            redirect = self.DEFAULT_LOGIN_ROUTE
            return request.redirect(redirect)
        return True



    def _login_redirect(self, uid, redirect=None):
        if not redirect and not request.env['res.users'].sudo().browse(uid).has_group('base.group_user'):
            return request.redirect(self.DEFAULT_LOGIN_ROUTE)
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

    @http.route('/selfcare/logout', methods=["GET"], auth="none", website=True)
    def logout(self):
        request.session.logout(keep_db=True)
        redirect = self.DEFAULT_LOGIN_ROUTE
        return request.redirect(redirect)

    @http.route("/selfcare", auth='public', methods=["GET"], website=True)
    def selfcare_home(self, **kw):
        context = {}
        full_name = ""
        customer_id = ""
        image = ""
        img_url = ""

        template = "isp_crm_module.template_selfcare_login_main"
        if self._redirect_if_not_login(req=request):
            user_id = request.env.context.get('uid')
            logged_in_user = request.env['res.users'].sudo().browse(user_id)
            template = "isp_crm_module.template_selfcare_main_layout"
            context['user'] = logged_in_user
            context['full_name'] = logged_in_user.name.title()
            context['customer_id'] = logged_in_user.subscriber_id
            context['image'] = logged_in_user.image
            img_url = '/web/content/%s' % logged_in_user.image
            context['img_url'] = img_url

        return request.render(template, context)