# -*- coding: utf-8 -*-
import traceback
from odoo import http
from .execute_query import update_bandwitdh_expiry_real_ip


class FreeradiusExpiryUpdateExpiryRealIp(http.Controller):
    @http.route('/freeradius/update_expiry_bandwidth_real_ip', auth='public')
    def index(self, **kw):
        """
        Update expiry date

        Parameters
        ----------
        username : str
            username of the user

        bandwidth: str
            assign bandwidth for the client. Format 10M/10M

        expirydate : str
            Billing cycle

        package: str
            name of the updated package

        Returns
        -------
             returns 'success' if successful, otherwise returns debug data.
        """

        username=kw['username']
        expirydate=kw['expirydate']
        bandwidth=kw['bandwidth']
        package=kw['package']
        print(bandwidth)
        print(package)
        try:
            result = update_bandwitdh_expiry_real_ip(username,expirydate,bandwidth,package)
            if result == 'success':
                http.request.env['dgcon_radius.logs'].sudo().create(
                    {
                        'username': username,
                        'message': result,
                        'bandwidth': bandwidth,
                        'status': True,
                        'update_package': package,
                        'date':expirydate,
                        'type': 'Expiry',
                        'radius_error': False
                    })
                return result

            else:
                http.request.env['dgcon_radius.logs'].sudo().create(
                    {
                        'username': username,
                        'message': result,
                        'bandwidth': bandwidth,
                        'status': False,
                        'date': expirydate,
                        'update_package': package,
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
                    'bandwidth': bandwidth,
                    'update_package': package,
                    'type': 'Expiry',
                    'date': expirydate,
                    'radius_error': False
                }
            )
            return 'error while executing update_expiry_connection: ' + traceback.format_exc()