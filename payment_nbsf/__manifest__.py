# -*- coding: utf-8 -*-
{
    'name': "Nuevo Banco de Santa Fe Direct Debit Bank Payment",

    'summary': """""",

    'description': """
        This module is used to generate payment/debit files for bank entity:
            - Nuevo Bando de Santa Fe
        
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
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/nbsf_payment_acquirer_view.xml',
        'data/nbsf_payment_data.xml',        
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
