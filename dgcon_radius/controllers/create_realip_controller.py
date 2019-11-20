# -*- coding: utf-8 -*-
import traceback

from odoo import http

from .execute_query import create_connection_realip


class FreeradiusCreateRealIP(http.Controller):
    @http.route('/freeradius/createrealip', auth='public')
    def index(self, **kw):
        """
        Creating user from odoo erp

        Parameters
        ----------
        username : str
            username for the client. This will be needed for PPoE access

        password: str
            password for the client. This also will be needed for PPoE access

        bandwidth: str
            assign bandwidth for the client. Format 10M/20M

        pool: str
            IP pool for the client.

        date: str
            Billing cycle: 30 June 2019 23:59

        Returns
        -------
        str
            returns 'success' if successful, otherwise returns debug data. see create_connection
        """
        result=None
        username = kw['username']
        password = kw['password']
        bandwidth= kw['bandwidth']
        real_ip = kw['real_ip']
        pool = kw['pool']
        date = kw['date']

        try:
            result=create_connection_realip(username, password, bandwidth, real_ip, date)

            if result == 'success':


                http.request.env['dgcon_radius.logs'].sudo().create(
                    {
                        'username': username,
                        'password': password,
                        'bandwidth': bandwidth,
                        'date': date,
                        'message': result,
                        'status': True,
                        'ip_pool': real_ip,
                        'type': 'Create',
                        'radius_error':False
                    }
                )
                return result

            else:
                http.request.env['dgcon_radius.logs'].sudo().create(
                    {
                        'username': username,
                        'password': password,
                        'bandwidth': bandwidth,
                        'date': date,
                        'message': result,
                        'status': False,
                        'ip_pool': real_ip,
                        'type': 'Create',
                        'radius_error': True
                    }
                )
                return result


        except:
            http.request.env['dgcon_radius.logs'].sudo().create(
                {
                    'username': username,
                    'password': password,
                    'bandwidth': bandwidth,
                    'date':date,
                    'message':traceback.format_exc(),
                    'status': False,
                    'ip_pool': real_ip,
                    'type': 'Create',
                    'radius_error': False
                }
            )
            return 'error while executing create_connection: '+traceback.format_exc()


#
# from datetime import datetime
#
# now = datetime.now()
# date_time = now.strftime("%d %B %Y %H:%M")
# print(date_time)