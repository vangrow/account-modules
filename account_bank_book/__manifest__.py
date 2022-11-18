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
    'version': '1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'account',
        
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_bank_book_view.xml',
        'views/res_config_settings_view.xml',
        'wizard/account_move_line_search_wizard.xml',
        'wizard/account_move_line_found_wizard.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

     # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
