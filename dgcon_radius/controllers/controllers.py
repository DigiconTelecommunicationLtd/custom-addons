# -*- coding: utf-8 -*-
from odoo import http

# class DgconRadius(http.Controller):
#     @http.route('/dgcon_radius/dgcon_radius/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dgcon_radius/dgcon_radius/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dgcon_radius.listing', {
#             'root': '/dgcon_radius/dgcon_radius',
#             'objects': http.request.env['dgcon_radius.dgcon_radius'].search([]),
#         })

#     @http.route('/dgcon_radius/dgcon_radius/objects/<model("dgcon_radius.dgcon_radius"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dgcon_radius.object', {
#             'object': obj
#         })