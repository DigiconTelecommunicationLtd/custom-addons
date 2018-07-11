# -*- coding: utf-8 -*-
{
    'name': "ISP Helpdesk",

    'summary': """Automating the ISP Helpdesk""",

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
    'depends': ['crm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/helpdesk_default_stages.xml',
        'data/helpdesk_default_problems.xml',
        'data/helpdesk_default_solutions.xml',
        'data/helpdesk_default_teams.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/view_stage.xml',
        'views/view_team.xml',
        'views/view_ticket_type.xml',
        'views/view_type_of_subject.xml',
        'views/view_problem.xml',
        'views/view_solution.xml',
        'views/view_ticket.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
