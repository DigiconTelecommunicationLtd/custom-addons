# -*- coding: utf-8 -*-
from odoo import http

from odoo.addons.web.controllers.main import Home
from .base_controller import BaseController
import requests
import json

try:
    from .local_settings import *
except ImportError:
    pass


class PaymentController(BaseController):
    # INITIATION_URL = 'https://sandbox.sslcommerz.com/gwprocess/v3/api.php'
    # STORE_ID = 'mime5bc41d233a312'
    # STORE_NAME = 'testmime24q9'
    # STORE_PWD = 'mime5bc41d233a312@ssl'
    # DEFAULT_CURRENCY = 'BDT'
    # BASE_URL = "http://103.117.192.76:8069/"

    # INITIATION_URL = 'https://securepay.sslcommerz.com/gwprocess/v3/api.php'
    # STORE_ID = 'digicontelecommunicationltdlive'
    # STORE_NAME = 'DIGICONTELECOLTD'
    # STORE_PWD = '5C173EC20E6A527353'
    # DEFAULT_CURRENCY = 'BDT'
    # BASE_URL = "http://103.117.192.76:8069/"
    #

    def _make_data_dict(self, base_url, customer, amount, transaction_id):
        return {
            'store_id': STORE_ID,
            'store_passwd': STORE_PWD,
            'total_amount': amount,
            'currency': DEFAULT_CURRENCY,
            'tran_id': transaction_id,
            'success_url': base_url + "selfcare/make-payment/success",
            'fail_url': base_url + "selfcare/make-payment/failure",
            'cancel_url': base_url + "selfcare/make-payment/failure",
            'cus_name': customer.name,
            'cus_email': customer.email,
            'cus_add1': customer.street if customer.street else "",
            'cus_add2': customer.street2 if customer.street2 else "",
            'cus_city': customer.city if customer.city else "",
            'cus_state': customer.state_id.name if customer.state_id else "",
            'cus_postcode': customer.zip if customer.zip else "",
            'cus_country': customer.country_id.name if customer.country_id else "",
            'cus_phone': customer.mobile if customer.mobile else "",
            'cus_fax': customer.phone if customer.phone else "",
            # 'multi_card_name': "mastercard, visacard, amexcard ",
        }

    def initiate_session(self, base_url, customer, amount, transaction_id):
        data = self._make_data_dict(base_url=base_url, customer=customer, amount=amount, transaction_id=transaction_id)
        response = requests.post(url=INITIATION_URL, data=data)
        response_content = json.loads(response.content.decode('utf-8'))
        return response_content