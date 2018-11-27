# -*- coding: utf-8 -*-
from odoo import http

from odoo.addons.web.controllers.main import Home
from .base_controller import BaseController
import requests
import json


class PaymentController(BaseController):
    INITIATION_URL = 'https://sandbox.sslcommerz.com/gwprocess/v3/api.php'
    STORE_ID = 'mime5bc41d233a312'
    STORE_NAME = 'testmime24q9'
    STORE_PWD = 'mime5bc41d233a312@ssl'
    DEFAULT_CURRENCY = 'BDT'
    BASE_URL = "http://localhost:8069/"


    def _make_data_dict(self, user_info):
        return {
            'store_id': self.STORE_ID,
            'store_passwd': self.STORE_PWD,
            'total_amount': user_info["amount"],
            'currency': self.DEFAULT_CURRENCY,
            'tran_id': user_info["transaction_id"],
            'success_url': self.BASE_URL + "selfcare/make-payment/success",
            'fail_url': self.BASE_URL + "selfcare/make-payment/failure",
            'cancel_url': self.BASE_URL + "selfcare/make-payment/failure",
            'cus_name': user_info["customer"].name,
            'cus_email': user_info["customer"].email,
            'cus_add1': "",
            'cus_add2': "Dhaka ",
            'cus_city': "Dhaka ",
            'cus_state': "Dhaka ",
            'cus_postcode': "1000 ",
            'cus_country': "Bangladesh ",
            'cus_phone': "01711111111 ",
            'cus_fax': "01711111111 ",
            'ship_name': "Customer Name",
            'ship_add1': "Dhaka ",
            'ship_add2': "Dhaka ",
            'ship_city': "Dhaka ",
            'ship_state': "Dhaka ",
            'ship_postcode': "1000 ",
            'ship_country': "Bangladesh ",
            'multi_card_name': "mastercard, visacard, amexcard ",
        }

    def initiate_session(self, customer, amount, transaction_id):
        user_info = {}
        user_info["customer"] = customer
        user_info["amount"] = amount
        user_info["transaction_id"] = transaction_id

        data = self._make_data_dict(user_info=user_info)
        response = requests.post(url=self.INITIATION_URL, data=data)
        response_content = json.loads(response.content.decode('utf-8'))
        return response_content
