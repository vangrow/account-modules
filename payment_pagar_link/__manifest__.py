# -*- coding: utf-8 -*-
{
    'name': "Pagar Link Bank Payment",

    'summary': """""",

    'description': """
        This module is used to generate payment files for diferent bank entities:
            - Red Link Pagar
        
        Configuración:
            - 1) Instalar el módulo
            - 2) Configurar el Método de pago
            - 3) Crear los Modos de pago
            - 4) Asignar Modo de pago al cliente
    """,

    'author': "Leonardo Bozzi",
    'website': "http://www.vangrow.ar",

    # for the full list
    'category': 'Account',
    'version': '15.0.0.2',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'account',
        'payment',
        'payment_bank_debit',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/red_link_pagar_payment_acquirer_view.xml',
        'data/pagar_link_payment_data.xml',
        
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
