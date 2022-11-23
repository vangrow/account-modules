# -*- coding: utf-8 -*-
{
    'name': "Direct Debit Bank Payment",

    'summary': """""",

    'description': """
        This module is used to generate payment/debit files for diferent bank entities:
          
    """,

    'author': "Leonardo Bozzi",
    'website': "http://www.vangrow.ar",

    # for the full list
    'category': 'Account',
    'version': '15.0.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'account',
        'payment',
        'account_payment_partner',
        'partner_ref_unique',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_bank_view.xml',
        'views/direct_debit_file_view.xml',
        'views/response_direct_debit_file_view.xml',
        'wizard/export_direct_debit_wizard.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
