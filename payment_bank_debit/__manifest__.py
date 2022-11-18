# -*- coding: utf-8 -*-
{
    'name': "Direct Debit Bank Payment",

    'summary': """""",

    'description': """
        This module is used to generate payment/debit files for diferent bank entities:
            - Nuevo Bando de Santa Fe
            - Banco Credicoop Coop. Ltdo.
        
        Configuración:
            - 1) Instalar el módulo
            - 2) Configurar el Método de pago
            - 3) Crear Modo de pago
            - 4) Asignar Modo de pago al cliente
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
        'account_payment_group',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/nbsf_payment_acquirer_view.xml',
        'views/credicoop_payment_acquirer_view.xml',
        'views/direct_debit_file_view.xml',
        'views/res_partner_bank_view.xml',
        'views/response_direct_debit_file_view.xml',
        'wizard/export_direct_debit_wizard.xml',
        'data/nbsf_payment_data.xml',
        'data/credicoop_payment_data.xml',
        
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
