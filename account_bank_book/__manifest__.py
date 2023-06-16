# -*- coding: utf-8 -*-
{
    'name': "Account Bank Book",

    'summary': """""",

    'description': """
        This module is for bank book
            - 
    """,

    'author': "Leonardo Bozzi",
    'website': "http://www.vangrow.ar",

    # for the full list
    'category': 'Network Device Manage',
    'version': '15.0.0.2',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'account',
        'account_reports',
    ],

    # always loaded
    'data': [
        'views/account_bank_book_config_view.xml',
        'views/account_bank_book_view.xml',
        'wizard/account_move_line_search_wizard.xml',
        'wizard/account_move_line_found_wizard.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

     # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
