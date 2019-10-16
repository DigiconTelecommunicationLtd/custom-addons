# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError, Warning
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

FILTER_TYPE=[
    ('last_paid_date','Last Payment Date')
]
CUSTOMER_TYPE = [
    ('retail', 'Retail'),
    ('corporate', 'Corporate'),
    ('sohoandsme', 'SOHO and SME')
]
SUB_TYPE = [
    ('new', 'New'),
    ('existing', 'Existing')
]

class DashboardOne(models.Model):
    _name = "mime_sales_report.sales_filter"

    from_date = fields.Date('From', required=True)
    to_date = fields.Date('To', required=True)


    customer_type = fields.Selection(CUSTOMER_TYPE, string='Customer Type', required=True, help="Customer type",
                                   default='retail')
    # sub_type = fields.Selection(SUB_TYPE, string='Type', required=True, help="type",
    #                                  default='new')
    @api.multi
    def filter(self):
        print("You click finish")
        print(str(self.from_date))
        print(str(self.to_date))
        tree_view_id=self.env.ref('mime_sales_report.mime_sales_report_new_customer').ids
        #form_view_id = self.env.ref('dgcon_radius.dgcon_radius_dgcon_radius_logs_view_form').ids
        print(str(tree_view_id))
        from_date_obj = datetime.strptime(self.from_date, DEFAULT_DATE_FORMAT)
        to_date_obj = datetime.strptime(self.to_date, DEFAULT_DATE_FORMAT)

        if from_date_obj > to_date_obj:
            raise UserError('From date must be less than To date')

        #print(str(self.env.ref('dgcon_radius_dgcon_radius_logs_tree').id))
        # return {
        #     'name': 'Title',
        #     'view_type':'tree',
        #     'view_mode': 'tree',
        #     'view_id':'dgcon_radius_dgcon_radius_logs_tree',
        #     'res_model': 'dgcon_radius.logs',
        #     'type':'ir.actions_act_window',
        #     'res_id': False,
        #     'target': 'current'
        # ### in domain pass ids if you want to show only filter data else it will display all data of that model.
        # }
        # domain=[]
        # domain.append(('subscriber_id', '!=', 'New'))
        # if self.filter_type == 'last_paid_date':
        #     domain.append(('current_package_end_date','>=',str(self.from_date)))
        #     domain.append(('current_package_end_date', '<=', str(self.to_date)))
        #     domain.append(('opportunity_ids.lead_type', '=', self.customer_type))
        # print(domain)
        #last_paid_date = ('past_paid_date','&gt;=',str(self.from_date))
        domain=[]
        retail =('lead_type','=',self.customer_type)

        filtered_customers = None
        domain.append(retail)
        data = ('date_maturity', '>=', str(self.from_date))
        domain.append(data)
        data = ('date_maturity', '<=', str(self.to_date))
        domain.append(data)
        data = ('credit', '!=', 0)
        domain.append(data)
        # if self.sub_type == 'existing':
        #
        #      data=('billing_start_date', '<=', str(self.from_date))
        #      domain.append(data)
        #      data = ('current_package_end_date', '>=', str(self.to_date))
        #      domain.append(data)
        #
        #      data = ('date_maturity', '>=', str(self.from_date))
        #      domain.append(data)
        #      data = ('date_maturity', '<=', str(self.to_date))
        #      domain.append(data)
        #
        #      data = ('credit', '!=', 0)
        #      domain.append(data)
        #
        # else:
        #     pass
        #     data =('billing_start_date', '<=', str(self.to_date))
        #     domain.append(data)
        #     data = ('billing_start_date', '>=', str(self.from_date))
        #     domain.append(data)
        #
        #     data = ('date_maturity', '>=', str(self.from_date))
        #     domain.append(data)
        #     data = ('date_maturity', '<=', str(self.to_date))
        #     domain.append(data)
        #
        #     data = ('credit', '!=', 0)
        #     domain.append(data)

        filtered_customers=self.env['mime_sales_report.new_customer_transient'].search(domain)
        print(len(filtered_customers))
        # return {
        #     'name': 'Customer Dashboard',
        #     'view_mode': 'tree',
        #     'views': [(tree_view_id, 'tree')],
        #     'res_model': 'mime_sales_report.new_customer_transient',
        #     'type': 'ir.actions.act_window',
        #     'target': 'current',
        #     'domain':domain
        #
        # }
        return self.env['mime_sales_report.new_customer_transient'].get_report(str(self.from_date),str(self.to_date),self.customer_type)
        # docargs={}
        # report=self.env['report'].render('hr_izracun_place.report_my_report', docargs)
        # print(">>>>>>", report)

        #report_obj.render('obe_reports_hec.report_student_on_probation', docargs)
