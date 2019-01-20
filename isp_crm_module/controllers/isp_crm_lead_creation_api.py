# -*- coding: utf-8 -*-
from odoo import http
import re
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError

class ISPCRMLeadCreationApi(http.Controller):

    @http.route('/create/lead/', type='json', methods=["POST"], auth='public', website=True, csrf=False)
    def create_lead(self, **kw):
        try:
            package_name = kw.get('package_name')
            lead_name = kw.get('lead_name')
            lead_mobile_number = kw.get('lead_mobile_number')
            lead_email = kw.get('lead_email')
            message = kw.get('message')

            if package_name and lead_name and lead_mobile_number and lead_email and message:

                sequence_id = http.request.env['ir.sequence'].sudo().next_by_code('crm.lead') or '/'

                check_customer_email = http.request.env['res.partner'].sudo().search([('email', '=', lead_email)],
                                                                      limit=1)
                if check_customer_email:
                    return 'Email should be unique'

                check_customer_mobile = http.request.env['res.partner'].sudo().search([('mobile', '=', lead_mobile_number)],
                                                                       limit=1)
                if check_customer_mobile:
                    return 'Mobile Number should be unique'

                product = http.request.env['product.product'].sudo().search([('name', '=', package_name)], limit=1)
                creating_values = {
                    'opportunity_seq_id': sequence_id,
                    'tagged_product_ids': product,
                    'name': lead_name,
                    'mobile': lead_mobile_number,
                    'email_from': lead_email,
                    'description': message,
                }

                ticket_obj = http.request.env['crm.lead'].sudo().create(creating_values)
                success_msg = "Data received and lead created successfully"

                return success_msg
            else:
                return False
        except Exception as ex:
            return ex

