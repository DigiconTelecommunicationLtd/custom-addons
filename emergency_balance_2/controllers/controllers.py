# -*- coding: utf-8 -*-
from odoo import http

# class EmergencyBalance2(http.Controller):
#     @http.route('/emergency_balance_2/emergency_balance_2/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/emergency_balance_2/emergency_balance_2/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('emergency_balance_2.listing', {
#             'root': '/emergency_balance_2/emergency_balance_2',
#             'objects': http.request.env['emergency_balance_2.emergency_balance_2'].search([]),
#         })

#     @http.route('/emergency_balance_2/emergency_balance_2/objects/<model("emergency_balance_2.emergency_balance_2"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('emergency_balance_2.object', {
#             'object': obj
#         })