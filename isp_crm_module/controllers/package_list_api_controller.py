# -*- coding: utf-8 -*-
from odoo import http
class CustomerPackageList(http.Controller):
    @http.route("/customer/package/list/", type='json', auth='user', website=True)
    def customer_package_list(self, **kw):
        packageName = list()
        packageCode = list()
        packagePrice = list()
        packages_list = http.request.env['product.product'].search([])
        for package in packages_list:
            packageName.append(package.name)
            packageCode.append(package.code)
            packagePrice.append(package.lst_price)
        return {
            'user': http.request.env.user,
            'packageName': packageName,
            'packageCode': packageCode,
            'packagePrice': packagePrice,
        }
    @http.route("/api/customer/package/list/", auth='user', methods=["GET"], website=True)
    def customer_package_list_call_api(self, **kw):
        logincode = http.request.httprequest.cookies.get('login_token')
        isloggedin = http.request.env['isp_crm_module.track_login'].search([("logincode", "=", logincode)])
        if len(isloggedin) < 1:
            return http.request.render("isp_crm_module.customer_login")
        else:
            return http.request.render("isp_crm_module.customer_package_list")