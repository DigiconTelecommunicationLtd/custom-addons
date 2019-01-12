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
    'depends': ['crm', 'sale_management', 'account_invoicing', 'hr', 'website', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/default_hd_stages_data.xml',
        'data/default_stages_data.xml',
        'data/default_payment_service_data.xml',
        # 'data/default_account_data.xml',
        'data/default_hd_complexity_level.xml',
        'data/default_hd_problems.xml',
        'data/default_ticket_types.xml',
        'views/views.xml',
        'views/isp_crm_problem_views.xml',
        'views/isp_crm_solution_views.xml',
        'views/isp_crm_stage_views.xml',
        'views/isp_crm_team_views.xml',
        'views/isp_crm_service_request_views.xml',
        'views/templates.xml',
        'views/isp_crm_opportunity_views.xml',
        'views/isp_crm_customer_views.xml',
        'views/isp_crm_change_package_views.xml',
        'template/isp_crm_mail_template/isp_crm_hd_mail_template.xml',
        'template/isp_crm_mail_template/isp_crm_service_request_mail_template.xml',
        'views/isp_crm_hd_menu_list.xml',
        'views/isp_crm_hd_type.xml',
        'views/isp_crm_hd_problem.xml',
        'views/isp_crm_hd_stage_views.xml',
        'views/isp_crm_hd_ticket_complexity_views.xml',
        'views/isp_crm_hd_solution_views.xml',
        'views/isp_crm_hd_tasks_views.xml',
        'views/isp_crm_hd_ticket_history.xml',
        'views/isp_crm_hd_td_type.xml',
        'views/isp_crm_hd_td_problem.xml',
        'views/isp_crm_hd_td_stage_views.xml',
        'views/isp_crm_hd_td_ticket_complexity_views.xml',
        'views/isp_crm_hd_td_solution_views.xml',
        'views/isp_crm_hd_td_tasks_views.xml',
        'views/isp_crm_hd_td_ticket_history.xml',
        'views/isp_crm_hd_views.xml',
        'views/isp_crm_hd_td_views.xml',
        'views/isp_crm_cron_job_views.xml',
        'views/isp_crm_invoice_views.xml',
        'views/isp_crm_customer_invoice_status_views.xml',
        'views/isp_crm_package_history_views.xml',
        'views/isp_crm_payment_views.xml',
        'views/isp_crm_menulist_views.xml',
        'views/isp_crm_notify_user.xml',
        'views/isp_crm_customer_quotation.xml',
        'views/isp_crm_register_payment_validate_form.xml',
        'template/new_ticket_page.xml',
        'template/customer_profile_ticket.xml',
        'template/customer_profile/customer_profile.xml',
        'template/customer_login/customer_login_api.xml',
        'template/customer_packages/customer_packages_list_api.xml',
        'template/selfcare_layout_templates.xml',
        'template/selfcare_login_templates.xml',
        'template/selfcare_forget_password_templates.xml',
        'template/isp_crm_mail_template/isp_crm_cron_job_receipt_attachment_template.xml',
        'template/isp_crm_mail_template/isp_crm_forget_password_mail_template.xml',
        'template/isp_crm_corporate_customer_quotation_template.xml',
        'data/default_stages_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
# -*- coding: utf-8 -*-
