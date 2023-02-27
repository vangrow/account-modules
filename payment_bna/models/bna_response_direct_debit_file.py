# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

import datetime
import base64

import logging
_logger = logging.getLogger(__name__)


class ResponseDirectDebitFile(models.Model):
    _inherit = "response.direct.debit.file"
    _description = 'response.direct.debit.file'

    def action_post(self):
        res = super(ResponseDirectDebitFile, self).action_post()
        if self.payment_acquirer_id.provider == 'bnadd':  # Debitos Directo Banco Nación
            self.bna_file_process()
        return res

    def bna_file_process(self):
        file_string = base64.b64decode(self.file).decode('utf-8','ignore').split('\n')

        # Registro Cabecera
        # 1 - Fecha de Archivo - tipo: alfanumérico - long.: 8 - decimales: 0
        self.date = datetime.datetime.strptime(
            file_string[0][8:16], "%y-%m-%d")
        # 2 - Monto - sumatoria - tipo: numérico - long.: 14 - decimales: 3
        # 3 - Cantidad de regiatros - tipo: numérico - long.: 6 - decimales: 0
        if "CANT.DEBITOS APLICADOS" in file_string[-4:][0]:
            count_ok = int(file_string[-4:][0][24:33])
            total_ok = float(
                file_string[-4:][0][60:88].replace('.', '').replace(',', ''))/100
            count_ko = int(file_string[-3:][0][24:33])
            total_ko = float(
                file_string[-3:][0][60:88].replace('.', '').replace(',', ''))/100

            count_reversed = int(file_string[-2:][0][24:33])
            total_reversed = float(
                file_string[-2:][0][60:88].replace('.', '').replace(',', ''))/100

            self.total = total_ok + total_ko + total_reversed
            self.count = count_ok + count_ko + count_reversed

        # Registro Datos
        payment_ok = 0
        total_ok = 0.0
        payment_ko = 0
        for data_registry in file_string[1:]:
            # 1 - Casa Sucursal - tipo: numérico - long.: 4 - decimales: 0
            if data_registry[0:4].isnumeric():
                branch_number = str(int(data_registry[0:4]))
                # 3 - Tipo de Cuenta - tipo: numérico - long.: 2 - decimales: 0
                acc_type = data_registry[5:7]
                # 4 - Cuenta - tipo: numérico - long.: 10 - decimales: 0
                acc_number = data_registry[10:21]
                # 5 - Importe -
                amount = float(data_registry[36:55].replace(
                    '.', '').replace(',', ''))/100
                # 6 - Observación
                reject_code = data_registry[56:86].replace(' ', '')
                if reject_code == '':
                    # Payment Transaction
                    # res_partner_bank_id = self.env['res.partner.bank'].search(
                    #    [('acc_number', '=', acc_number)])
                    payment_transaction_id = self.env['payment.transaction'].search([
                        ('acquirer_id', '=', self.payment_acquirer_id.id),
                        #('partner_id', '=', res_partner_bank_id.partner_id.id),                        
                        ('state', '=', 'pending'),
                        '|',('acquirer_reference', '=', acc_number),
                        ('acquirer_reference', '=', acc_number.lstrip('0'))
                    ])
                    
                    if payment_transaction_id:
                        payment_transaction_id._set_done()
                        payment_transaction_id._reconcile_after_done()
                        total_ok += amount
                        payment_ok += 1
                    else:
                        payment_ko += 1

                else:
                    # Payment Transaction
                    payment_transaction_id = self.env['payment.transaction'].search([
                        ('acquirer_id', '=', self.payment_acquirer_id.id),
                        #('partner_id', '=', res_partner_bank_id.partner_id.id),
                        ('state', '=', 'pending'),
                        '|',('acquirer_reference', '=', acc_number),
                        ('acquirer_reference', '=', acc_number.lstrip('0'))
                    ])
                    _logger.info("Test: %s -- %s" %
                                 (acc_number, payment_transaction_id))

                    payment_transaction_id._set_canceled(
                        state_message='Rechazo: ' + reject_code)
                    payment_ko += 1

        self.payment_count_ok = payment_ok
        self.payment_count_ko = payment_ko
        self.total_ok = total_ok
        self.state = 'posted'
