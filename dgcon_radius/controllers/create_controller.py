# -*- coding: utf-8 -*-
import traceback

from odoo import http

from .execute_query import create_connection


class FreeradiusCreate(http.Controller):
    @http.route('/freeradius/create', auth='public')
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
        customer_id = kw['customer_id']
        pool = kw['pool']
        date = kw['date']

        try:
            result=create_connection(username, password, bandwidth, pool, date)

            if result == 'success':


                http.request.env['dgcon_radius.logs'].sudo().create(
                    {
                        'username': username,
                        'password': password,
                        'bandwidth': bandwidth,
                        'date': date,
                        'message': result,
                        'status': True,
                        'ip_pool': pool,
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
                        'ip_pool': pool,
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
                    'ip_pool': pool,
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