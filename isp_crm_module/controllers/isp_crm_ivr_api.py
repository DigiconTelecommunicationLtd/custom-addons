# -*- coding: utf-8 -*-
from odoo import http

class ISPCRMIVRApi(http.Controller):

    @http.route('/ivr/<string:get_send_data>/', type='json', methods=["GET", "POST"], auth='public', website=True, csrf=False)
    def get_data(self, get_send_data=None, **kw):
        if get_send_data == "get_data":
            try:
                customer_id = kw.get('customer_id')
                customer_name = kw.get('customer_name')
                package_name = kw.get('package_name')

                if customer_id or customer_name:
                    creating_values = {
                        'customer_id': customer_id,
                        'customer_name': customer_name,
                        'package_name': package_name,
                    }
                    ticket_obj = http.request.env['isp_crm_module.ivr_api'].sudo().create(creating_values)
                    success_msg = "Data received successfully"

                    return success_msg
                else:
                    return False
            except:
                return False


        elif get_send_data == "post_data":
            customer_phone = kw.get('customer_phone')
            get_customer = http.request.env['res.partner'].sudo().search([('phone', '=', customer_phone)], limit=1)
            if get_customer:
                send_values = {
                    'customer_id': get_customer.subscriber_id,
                    'customer_name': get_customer.name,
                    'package_name': get_customer.current_package_id.name,
                }
                return send_values
            else:
                return False
        else:
            return False

