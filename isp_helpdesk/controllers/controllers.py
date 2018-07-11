# -*- coding: utf-8 -*-
from odoo import http

# class IspHelpdesk(http.Controller):
#     @http.route('/isp_helpdesk/isp_helpdesk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/isp_helpdesk/isp_helpdesk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('isp_helpdesk.listing', {
#             'root': '/isp_helpdesk/isp_helpdesk',
#             'objects': http.request.env['isp_helpdesk.isp_helpdesk'].search([]),
#         })

#     @http.route('/isp_helpdesk/isp_helpdesk/objects/<model("isp_helpdesk.isp_helpdesk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('isp_helpdesk.object', {
#             'object': obj
#         })