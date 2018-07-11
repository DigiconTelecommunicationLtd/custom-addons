# -*- coding: utf-8 -*-
from odoo import http

# class IspCrm(http.Controller):
#     @http.route('/isp_crm/isp_crm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/isp_crm/isp_crm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('isp_crm.listing', {
#             'root': '/isp_crm/isp_crm',
#             'objects': http.request.env['isp_crm.isp_crm'].search([]),
#         })

#     @http.route('/isp_crm/isp_crm/objects/<model("isp_crm.isp_crm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('isp_crm.object', {
#             'object': obj
#         })