# -*- coding: utf-8 -*-
from odoo import http
import string
import random
import uuid
from passlib.context import CryptContext

default_crypt_context = CryptContext(
    # kdf which can be verified by the context. The default encryption kdf is
    # the first of the list
    ['pbkdf2_sha512', 'md5_crypt'],
    # deprecated algorithms are still verified as usual, but ``needs_update``
    # will indicate that the stored hash should be replaced by a more recent
    # algorithm. Passlib 1.6 supports an `auto` value which deprecates any
    # algorithm but the default, but Ubuntu LTS only provides 1.5 so far.
    deprecated=['md5_crypt'],
)

class CustomerLoginController(http.Controller):

    @http.route("/customer/login/", type='json', auth='user', website=True)
    def customer_login(self, **kw):
        success_msg = 'Login unsuccessful ! Incorrect login or password given'

        # Fetch input json data sent from js

        subscriber_id = kw.get('Login')
        password = kw.get('Password')
        encrypted_password = self._crypt_context().encrypt(password)

        logincode = ''
        customer_list = http.request.env['isp_crm_module.login'].search([])

        for customer in customer_list:
            isLegitUser = self._crypt_context().verify_and_update(password, customer.password)
            print(isLegitUser[0])
            if customer.subscriber_id == subscriber_id and isLegitUser[0]:
                success_msg = "Successfully logged in"

                # chars = string.ascii_uppercase + string.digits
                # logincode = ''.join(random.choice(chars) for _ in range(15))
                # logincode = http.request.httprequest.cookies.get('login_token')
                logincode = uuid.uuid4()

                print("Login code generated")

                creating_values = {
                    'logincode': logincode,
                    'subscriber_id': subscriber_id,
                    'password': encrypted_password,
                }

                track_login = http.request.env['isp_crm_module.track_login'].create(creating_values)
                print("Login track record created")

                break

        return {

            'success_msg': success_msg,
            'logincode':logincode

        }


    def _crypt_context(self):
        """ Passlib CryptContext instance used to encrypt and verify
        passwords. Can be overridden if technical, legal or political matters
        require different kdfs than the provided default.

        Requires a CryptContext as deprecation and upgrade notices are used
        internally
        """
        return default_crypt_context

    @http.route("/api/customer/login/", auth='user', methods=["GET"], website=True)
    def customer_login_api(self, **kw):
        return http.request.render("isp_crm_module.customer_login")