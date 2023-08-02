# -*- coding: utf-8 -*-
{
    'name': "Liquidaciones de Argentina",

    'summary': """Liquidaciones for Argentinean Localization""",

    'description': """
        Comición en Liquidaciones Primarias
            - 
    """,

    'author': "Leonardo Bozzi",
    'website': "http://www.vangrow.ar",

    # for the full list
    'category': 'Accounting/Localizations',
    'version': '15.0.0.2',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
         
    ],

    # always loaded
    'data': [
        'view/account_move_view.xml',
        'report/report_invoice_liquidacion.xml',
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
