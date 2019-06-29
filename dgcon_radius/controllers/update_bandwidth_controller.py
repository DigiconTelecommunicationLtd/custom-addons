# -*- coding: utf-8 -*-
import traceback
from odoo import http
from .execute_query import update_connection



class FreeradiusUpdateBandwitdh(http.Controller):
    @http.route('/freeradius/update_bandwidth', auth='public')
    def index(self, **kw):
        """
        Creating user from odoo erp

        Parameters
        ----------
        username : str
            username for the client. This will be needed for PPoE access

        bandwidth: str
            assign bandwidth for the client. Format 10M/10M

        update_package: str
            name of the updated package

        Returns
        -------
        str
            returns 'success' if successful, otherwise returns debug data. see update_connection
        """
        result=None
        username = kw['username']
        bandwidth = kw['bandwidth']
        update_package = kw['update_package']
        current_package = kw['current_package']
        print(username,bandwidth,update_package,current_package)

        try:
            result=update_connection(username, bandwidth, update_package)
            print('result'+result)
            if result == 'success':
                http.request.env['dgcon_radius.logs'].sudo().create(
                    {
                        'username': username,
                        'bandwidth': bandwidth,
                        'message': result,
                        'ip_pool':current_package,
                        'status': True,
                        'type': 'Update',
                        'update_package':update_package,
                        'radius_error': False
                    }
                )
                return result

            else:
                http.request.env['dgcon_radius.logs'].sudo().create(
                    {
                        'username': username,
                        'bandwidth': bandwidth,
                        'ip_pool':current_package,
                        'message': result,
                        'status': False,
                        'type': 'Update',
                        'update_package': update_package,
                        'radius_error': True
                    }
                )
                return result

        except:
            http.request.env['dgcon_radius.logs'].sudo().create(
                {
                    'username': username,
                    'bandwidth': bandwidth,
                    'message': traceback.format_exc(),
                    'status': False,
                    'type': 'Update',
                    'update_package': update_package,
                    'radius_error': False
                }
            )
            return 'error while executing update_connection: '+traceback.format_exc()

