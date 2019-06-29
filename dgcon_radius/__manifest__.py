# -*- coding: utf-8 -*-
{
    'name': "dgcon_radius",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Digicon",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.5',

    # any module necessary for this one to work correctly
    'depends': ['base','isp_crm_module'],
    'external_dependencies': {
        'python': [
            'sqlalchemy',
            'paramiko',
        ],
    },
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/radius_addition.xml',
        'views/views.xml',
        'views/logs.xml',
        'views/menu.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}