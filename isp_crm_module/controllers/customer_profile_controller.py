# -*- coding: utf-8 -*-
from odoo import http

class CustomerProfile(http.Controller):

    @http.route("/customer/profile/", type='json', auth='user', website=True)
    def customer_profile_show(self, **kw):

        customer_list = http.request.env['res.partner'].search([("id", "=", http.request.env.user[0].id)])

        subscriber_id = customer_list.subscriber_id
        name = customer_list.name
        is_potential_customer = customer_list.is_potential_customer
        father = customer_list.father
        mother = customer_list.mother
        birthday = customer_list.birthday
        gender = customer_list.gender
        identifier_name = customer_list.identifier_name
        identifier_phone = customer_list.identifier_phone
        identifier_mobile = customer_list.identifier_mobile
        identifier_nid = customer_list.identifier_nid
        service_type = customer_list.service_type.name
        connection_type = customer_list.connection_type.name
        connection_media = customer_list.connection_media.name
        connection_status = customer_list.connection_status
        bill_cycle_date = customer_list.bill_cycle_date
        total_installation_charge = customer_list.total_installation_charge
        package_id = customer_list.package_id.name

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