# -*- coding: utf-8 -*-
{
    'name': "APTYS APP",

    'summary': """
        This module install all needed modules""",

    'author': "ArkeUp",
    'website': "https://www.arkeup.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': -100,

    # any module necessary for this one to work correctly
    'depends': ['crm', 'account_accountant', 'project', 'documents', 'timesheet_grid', 'stock', 'helpdesk', 'hr',
    'aptys_sale_purchase'],
    'application': True,
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': True,
}
