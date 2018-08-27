# -*- coding: utf-8 -*-
from odoo import http

# class IspCrmModule(http.Controller):
#     @http.route('/isp_crm_module/isp_crm_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/isp_crm_module/isp_crm_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('isp_crm_module.listing', {
#             'root': '/isp_crm_module/isp_crm_module',
#             'objects': http.request.env['isp_crm_module.isp_crm_module'].search([]),
#         })

#     @http.route('/isp_crm_module/isp_crm_module/objects/<model("isp_crm_module.isp_crm_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('isp_crm_module.object', {
#             'object': obj
#         })