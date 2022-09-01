# -*- coding: utf-8 -*-

{
    'name': 'Item Request by Employees/Users',
    'version': '14.0.0.1',
    'summary': """This module allow your employees/users to create Item Request.""",
    'description': """
    Item Request
    """,
    'author': 'None.',
    'website': 'http://www.example.com',
    'depends': ['stock', 'hr', 'purchase'],
    'data': [
        'security/security.xml',
        # 'security/multi_company_security.xml',
        'security/ir.model.access.csv',
        'data/purchase_requisition_sequence.xml',
        'data/employee_purchase_approval_template.xml',
        'data/confirm_template_material_purchase.xml',
        'report/purchase_requisition_report.xml',
        'views/purchase_requisition_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_department_view.xml',
        'views/stock_picking_view.xml',
    ],
}