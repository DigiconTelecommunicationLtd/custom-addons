# -*- coding: utf-8 -*-
import traceback
from odoo import http
from .execute_query import update_expiry


class FreeradiusUpdateExpiry(http.Controller):
    @http.route('/freeradius/update_expiry', auth='public')
    def index(self, **kw):
        """
        Update expiry date

        Parameters
        ----------
        username : str
            username of the user

        date: str
            new expiry date of user: 30 June 2019 23:59

        Returns
        -------
             returns 'success' if successful, otherwise returns debug data.
        """
        username = kw['username']
        date = kw['date']
        try:
            result = update_expiry(username, date)
            if result == 'success':
                http.request.env['dgcon_radius.logs'].sudo().create(
                    {
                        'username': username,
                        'message': result,
                        'status': True,
                        'date':date,
                        'type': 'Expiry',
                        'radius_error': False
                    })
                return result

            else:
                http.request.env['dgcon_radius.logs'].sudo().create(
                    {
                        'username': username,
                        'message': result,
                        'status': False,
                        'date': date,
                        'type': 'Expiry',
                        'radius_error': True

                    })
                return result

        except:
            http.request.env['dgcon_radius.logs'].sudo().create(
                {
                    'username': username,
                    'message': traceback.format_exc(),
                    'status': False,
                    'type': 'Expiry',
                    'date': date,
                    'radius_error': False
                }
            )
            return 'error while executing update_connection: ' + traceback.format_exc()
