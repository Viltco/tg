# -*- coding: utf-8 -*-
{
    'name': "pos_payment_domain",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
    ],
    # 'qweb': ['static/src/xml/pos_reciept.xml'],
    'assets': {
        'point_of_sale.assets': [

        ],
        'web.assets_qweb': [
            'pos_receipt/static/src/xml/**/*'
        ]
    },
}