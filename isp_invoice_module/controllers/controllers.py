# -*- coding: utf-8 -*-
from odoo import http

# class IspInvoiceModule(http.Controller):
#     @http.route('/isp_invoice_module/isp_invoice_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/isp_invoice_module/isp_invoice_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('isp_invoice_module.listing', {
#             'root': '/isp_invoice_module/isp_invoice_module',
#             'objects': http.request.env['isp_invoice_module.isp_invoice_module'].search([]),
#         })

#     @http.route('/isp_invoice_module/isp_invoice_module/objects/<model("isp_invoice_module.isp_invoice_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('isp_invoice_module.object', {
#             'object': obj
#         })