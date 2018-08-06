# -*- coding: utf-8 -*-
{
    'name': "isp crm custom actions",

    'summary': """Extends CRM's power.""",

    'description': """
        Extends CRM's power.
    """,

    'author': "Test Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm', 'sale'],

    # always loaded
    'data': [

        # 'security/ir.model.access.csv',
        'data/delete_previous_states_data.xml',
        'data/default_states_data.xml',
        'views/inherited_views.xml',
        'views/views.xml',
        'views/sequences.xml',
        'views/service_type_views.xml',
        'views/connection_type_views.xml',
        'views/connection_media_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
