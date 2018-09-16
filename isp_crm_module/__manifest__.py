{
    'name': "isp_crm_module",

    'summary': """
        Extend's CRM power and adds new features""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/views.xml',
        'views/isp_crm_problem_views.xml',
        'views/isp_crm_solution_views.xml',
        'views/isp_crm_stage_views.xml',
        'views/isp_crm_team_views.xml',
        'views/isp_crm_service_request_views.xml',
        'views/templates.xml',
        'views/isp_crm_opportunity_views.xml',
        'views/isp_crm_customer_views.xml',
        'views/isp_crm_menulist_views.xml',
        'views/isp_crm_cron_job_views.xml',
        'data/default_stages_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
