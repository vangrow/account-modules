# -*- coding: utf-8 -*-
{
    'name': "Ret/Per de Argentina",

    'summary': """Reporting for Argentinean Localization""",

    'description': """
        Reportes de Retenciones/Percepciones Sufridas
            - 
    """,

    'author': "Leonardo Bozzi",
    'website': "http://www.vangrow.ar",

    # for the full list
    'category': 'Accounting/Localizations/Reporting',
    'version': '15.0.0.2',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'l10n_ar',
        'account_reports',   
    ],

    # always loaded
    'data': [
        'data/account_financial_report_withholding.xml',
        'report/account_ar_withholding_line_view.xml',
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
