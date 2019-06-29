# -*- coding: utf-8 -*-
from odoo import http
from .execute_query import execute,DISCONNECT

#FOR REFERENCE ONLY
class FreeradiusDisconnect(http.Controller):
    @http.route('/freeradius/disconnect', auth='public')
    def index(self, **kw):
        """Update radreply and set bandwidth to 1k/k
            :param username
        """
        username = kw['username']
        status, data = execute(DISCONNECT.format(username))

        if status:
            return 'success'
        else:
            return str(data)
