# -*- coding: utf-8 -*-
{
    'name': "APTYS Sale Purchase",

    'summary': """
        This module add features inside sale and purchase""",

    'author': "ArkeUp",
    'website': "https://www.arkeup.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_purchase','aptys_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml'
    ],
    'license': 'LGPL-3',
}
