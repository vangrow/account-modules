# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

import datetime
import base64


class ResponseDirectDebitFile(models.Model):
    _inherit = "response.direct.debit.file"
    _description = 'response.direct.debit.file'

    def action_post(self):
        res = super(ResponseDirectDebitFile, self).action_post()
        if self.payment_acquirer_id.provider == 'bccoopdd':  # Debitos Directo Banco Credicoop
            self.credicoop_file_process()
        return res

    def credicoop_file_process(self):
        file_string = base64.b64decode(self.file).decode('utf-8').split('\n')

        # Registro Datos
        payment_ok = 0
        total_ok = 0.0
        payment_ko = 0
        for data_registry in file_string:

            # 1 - Empresa - tipo: numérico - long.: 2 - decimales: 0
            # 2 - Frecuencia - tipo: alfanumérico - long.: 1 - decimales: 0
            # 3 - Banco - tipo: numérico - long.: 3 - decimales: 0
            # 4 - Sucursal - tipo: numérico - long.: 3 - decimales: 0
            branch_number = data_registry[6:9]
            # 5 - Tipo de Cuenta - tipo: numérico - long.: 1 - decimales: 0
            # 6 - Número de Cuenta - tipo: numérico - long.: 7 - decimales: 0
            acc_number = data_registry[10:17]
            # 7 - Año de Vencimiento - tipo: numérico - long.: 2 - decimales: 0
            # 8 - Mes/Cuota de Vto. - tipo: numérico - long.: 2 - decimales: 0
            # 9 - Fecha de Vto. - tipo: numérico - long.: 6 - decimales: 0
            # 10 - Turno - tipo: numérico - long.: 3 - decimales: 0
            # 11 - Identificador - tipo: numérico - long.: 18 - decimales: 0
            vat = data_registry[30:48]
            # 12 - Importe del Débito - tipo: numérico - long.: 11 - decimales: 2
            amount = float(data_registry[48:59])/100
            # 13 - Importe 2 - tipo: numérico - long.: 11 - decimales: 2
            # 14 - Fecha de Pago - tipo: numérico - long.: 6 - decimales: 0
            # 15 - Resultado del Débito - tipo: alfnumérico - long.: 1 - decimales: 0

            
            raise ValidationError("Test: %s"%(amount))
            """
            
            
            # 15 - Resultado del Débito - tipo: alfnumérico - long.: 1 - decimales: 0
            data_registry += ' '
            # 16 - Moneda - tipo: alfnumérico - long.: 1 - decimales: 0
            data_registry += 'P'
            # 17 - Tipo de Débito - tipo: alfnumérico - long.: 1 - decimales: 0
            data_registry += 'D'
            # 18 - Filler - tipo: alfanumérico - long.: 11 - decimales: 0

            # 1 - Sistema - tipo: numérico - long.: 2 - decimales: 0
            # 2 - Reservado - tipo: numérico - long.: 4 - decimales: 0
            # 3 - CBU - tipo: numérico - long.: 22 - decimales: 0
            acc_number = data_registry[6:28].lstrip('0')
            # 4 - Código de operación - tipo: numérico - long.: 2 - decimales: 0
            # 5 - Importe - tipo: numérico - long.: 14 - decimales: 3
            amount = float(data_registry[30:44])/1000
            # 6 - Fecha imputación - tipo: numérico - long.: 8 - decimales: 0
            # 7 - Número de comprobante - tipo: numérico - long.: 10 - decimales: 0
            # 8 - CUIT/CUIL/DNI/DOC - tipo: numérico - long.: 11 - decimales: 0
            vat = data_registry[62:73].lstrip('0')
            # 9 - Denominación de cuenta - tipo: alfanumérico - long.: 16 - decimales: 0
            # 10 - Referencia Unívoca débito - tipo: alfanumérico - long.: 15 - decimales: 0
            # 11 - Reverso - tipo: alfanumérico - long.: 1 - decimales: 0
            # 12 - Trace Original - tipo: alfanumérico - long.: 15 - decimales: 0
            # 13 - Destino del Débito - tipo: numérico - long.: 2 - decimales: 0
            system = data_registry[120:122]
            # 14 - Código de Rechazo - tipo: numérico - long.: 3 - decimales: 0
            reject_code = data_registry[122:125]
            # 15 - Descripción de R - tipo: alfanumérico - long.: 30 - decimales: 0
            reject_message = data_registry[125:155].strip()

            if reject_code == '000' and reject_message == 'ACEPTADO':
                # Paymen Transaction
                res_partner_bank_id = self.env['res.partner.bank'].search(
                    [('acc_number', '=', acc_number)])
                payment_transaction_id = self.env['payment.transaction'].search([
                    ('acquirer_id', '=', self.payment_acquirer_id.id),
                    ('partner_id', '=', res_partner_bank_id.partner_id.id),
                    ('acquirer_reference', '=', res_partner_bank_id.acc_number)
                ])
                
                payment_transaction_id._set_done()
                payment_transaction_id._reconcile_after_done()
                total_ok += amount
                payment_ok += 1
                
            else:
                payment_ko += 1
            """            
        self.payment_count_ok = payment_ok
        self.payment_count_ko = payment_ko
        self.total_ok = total_ok
        self.state = 'posted'
