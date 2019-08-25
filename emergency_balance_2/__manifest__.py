# -*- coding: utf-8 -*-
{
    'name': "emergency_balance_2",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['isp_crm_module','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/create_ticket.xml',
        'views/emergency_balance.xml',
        'views/approval_balance.xml',
        'views/rejected_balance.xml',
        'views/update_isp_crm_customer_view.xml',
        'views/update_invoice_form.xml',
        'views/paid_balance.xml',
        'views/menu.xml',
        'views/views.xml',
        'views/templates.xml',
        'templates/email_templates.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}