# -*- coding: utf-8 -*-
{
    'name': "mime_sales_report",

    'summary': """
        Custom sales report module for MIME ISP""",

    'description': """
        Custom sales report module for MIME ISP
    """,

    'author': "MIME",
    'website': "https://mimebd.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['isp_crm_module'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'wizards/new_customer.xml',
        'wizards/filter.xml',
        'views/menu.xml',
        'views/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}