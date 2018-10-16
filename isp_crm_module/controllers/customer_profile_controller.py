# -*- coding: utf-8 -*-
from odoo import http

class CustomerProfile(http.Controller):

    @http.route("/customer/profile/", type='json', auth='user', website=True)
    def customer_profile_show(self, **kw):

        getlogincode = http.request.httprequest.cookies.get('login_token')
        getcustomer = http.request.env['isp_crm_module.track_login'].search([("logincode", "=", getlogincode)])
        customer_list = http.request.env['res.partner'].search([("subscriber_id", "=", getcustomer.subscriber_id)])

        subscriber_id = customer_list[0].subscriber_id
        name = customer_list[0].name
        is_potential_customer = customer_list[0].is_potential_customer
        father = customer_list[0].father
        mother = customer_list[0].mother
        birthday = customer_list[0].birthday
        gender = customer_list[0].gender
        identifier_name = customer_list[0].identifier_name
        identifier_phone = customer_list[0].identifier_phone
        identifier_mobile = customer_list[0].identifier_mobile
        identifier_nid = customer_list[0].identifier_nid
        service_type = customer_list[0].service_type.name
        connection_type = customer_list[0].connection_type.name
        connection_media = customer_list[0].connection_media.name
        connection_status = customer_list[0].connection_status
        bill_cycle_date = customer_list[0].bill_cycle_date
        total_installation_charge = customer_list[0].total_installation_charge
        package_id = customer_list[0].package_id.name

        return {
            'user': http.request.env.user,
            'subscriber_id':subscriber_id,
            'name': name,
            'is_potential_customer': is_potential_customer,
            'father':father,
            'mother':mother,
            'birthday':birthday,
            'gender':gender,
            'identifier_name':identifier_name,
            'identifier_phone':identifier_phone,
            'identifier_mobile':identifier_mobile,
            'identifier_nid':identifier_nid,
            'service_type':service_type,
            'connection_type':connection_type,
            'connection_media':connection_media,
            'connection_status':connection_status,
            'bill_cycle_date':bill_cycle_date,
            'total_installation_charge':total_installation_charge,
            'package_id':package_id,
        }

    @http.route("/api/customer/profile/", auth='user', methods=["GET"], website=True)
    def customer_profile_api(self, **kw):
        logincode = http.request.httprequest.cookies.get('login_token')
        isloggedin = http.request.env['isp_crm_module.track_login'].search([("logincode", "=", logincode)])

        if len(isloggedin) < 1:
            return http.request.render("isp_crm_module.customer_login")
        else:
            return http.request.render("isp_crm_module.customer_profile_show")