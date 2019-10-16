# -*- coding: utf-8 -*-
from odoo import http

# class MimeSalesReport(http.Controller):
#     @http.route('/mime_sales_report/mime_sales_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mime_sales_report/mime_sales_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mime_sales_report.listing', {
#             'root': '/mime_sales_report/mime_sales_report',
#             'objects': http.request.env['mime_sales_report.mime_sales_report'].search([]),
#         })

#     @http.route('/mime_sales_report/mime_sales_report/objects/<model("mime_sales_report.mime_sales_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mime_sales_report.object', {
#             'object': obj
#         })