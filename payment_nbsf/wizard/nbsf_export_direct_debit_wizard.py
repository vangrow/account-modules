# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

import datetime
from pandas.tseries.offsets import BDay
import base64
from uuid import uuid4
import logging
_logger = logging.getLogger(__name__)


class ExportDirectDebitWizard(models.TransientModel):
    _inherit = 'export.direct.debit.wizard'
    _description = "export.direct.debit.wizard"

   
    def file_save(self):
        res = super(ExportDirectDebitWizard, self).file_save()
        if self.payment_acquirer_id.provider == 'nbsfdd':  # Debitos Directo Nuevo Banco de Santa Fe
            self.nbsf_file_generator()
        return res
        

    def nbsf_file_generator(self):
        # Registro Datos
        registry = {}
        total = 0.0
        count = 0

        for invoice_id in self._context['active_ids']:
            invoice = self.env['account.move'].search(
                [('id', '=', invoice_id)])
            if invoice.state == 'posted' and invoice.partner_id.customer_payment_mode_id == self.payment_mode_id:
                if not invoice.partner_id.bank_ids:
                    raise UserError("Error: El cliente %s de la factura %s no tiene una cuanta bancaria asociada!!!"%(invoice.partner_id.name, invoice.name))
                acc_number = invoice.partner_id.bank_ids[0].acc_number
                if acc_number not in registry:
                    registry[acc_number] = {}
                registry[acc_number]['%s' % (invoice_id)] = {
                    'account_type': invoice.partner_id.bank_ids[0].account_type,
                    'amount_residual': invoice.amount_residual,
                    'currency_id': invoice.currency_id.id,
                    'imputation_date': self.file_date + BDay(self.imputation_business_days),
                    'document_number': invoice.l10n_latam_document_number,
                    'vat': "0" if not invoice.partner_id.vat else invoice.partner_id.vat,
                    'partner_id': invoice.partner_id.id,
                    'partner_name': invoice.partner_id.name,
                    'partner_country_id': invoice.partner_id.country_id.id,
                    'company_name': self.env.user.company_id.name,
                    'date': self.file_date,
                }

        data_registry = ''
        for acc_number in registry:
            total_registry = 0.0
            invoice_ids = []

            for invoice in registry[acc_number]:
                invoice_ids.append(invoice)
                total_registry = total_registry + \
                    registry[acc_number][invoice]['amount_residual']

            # Paymen Transaction
            payment_transaction = self.env['payment.transaction']
            values = {
                'amount': total_registry,
                'acquirer_id': self.payment_acquirer_id.id,
                'acquirer_reference': acc_number,
                'currency_id': registry[acc_number][invoice]['currency_id'],
                'reference': str(uuid4()),
                'partner_id': registry[acc_number][invoice]['partner_id'],
                'partner_country_id': registry[acc_number][invoice]['partner_country_id'],
                'invoice_ids': [(6, 0, invoice_ids)],
                'state': 'pending',
            }
            pt = payment_transaction.create(values)

            total = total + total_registry
            count += 1
            # 1 - Sistema - tipo: numérico - long.: 2 - decimales: 0
            data_registry += '00' if registry[acc_number][invoice]['account_type'] == 'cc' else '01'
            # 2 - Reservado - tipo: numérico - long.: 4 - decimales: 0
            data_registry += '0000'
            # 3 - CBU - tipo: numérico - long.: 22 - decimales: 0
            data_registry += acc_number.rjust(22, "0")[:22]
            # 4 - Código de operación - tipo: numérico - long.: 2 - decimales: 0
            data_registry += '01'
            # 5 - Importe - tipo: numérico - long.: 14 - decimales: 3
            data_registry += str(int(round(total_registry, 3)
                                 * 1000)).rjust(14, "0")[:14]
            # 6 - Fecha imputación - tipo: numérico - long.: 8 - decimales: 0
            data_registry += (self.file_date +
                              BDay(self.imputation_business_days)).strftime("%Y%m%d")[:8]
            # 7 - Número de comprobante - tipo: numérico - long.: 10 - decimales: 0
            data_registry += "0".rjust(10, "0")[:10]
            # 8 - CUIT/CUIL/DNI/DOC - tipo: numérico - long.: 11 - decimales: 0
            data_registry += registry[acc_number][invoice]['vat'].rjust(11, "0")[
                :11]
            # 9 - Denominación de cuenta - tipo: alfanumérico - long.: 16 - decimales: 0
            data_registry += registry[acc_number][invoice]['partner_name'].upper().ljust(16, " ")[
                :16]
            # 10 - Referencia Unívoca débito - tipo: alfanumérico - long.: 15 - decimales: 0
            data_registry += registry[acc_number][invoice]['company_name'].upper().ljust(15, " ")[
                :15]
            # 11 - Reverso - tipo: alfanumérico - long.: 1 - decimales: 0
            data_registry += " "
            # 12 - Trace Original - tipo: alfanumérico - long.: 15 - decimales: 0
            data_registry += " ".rjust(15, " ")[:15]
            # 13 - Uso interno - tipo: alfanumérico - long.: 105 - decimales: 0
            data_registry += " ".rjust(105, " ")[:105]
            data_registry += "\r\n"

        header = ''
        # Registro Cabecera
        # 1 - Cabecera - tipo: numérico - long.: 4 - decimales: 0
        header += self.payment_acquirer_id.nbsf_header[:4]
        # 2 - Empresa - tipo: numérico - long.: 4 - decimales: 0
        header += self.payment_acquirer_id.nbsf_company[:4]
        # 3 - Convenio - tipo: numérico - long.: 4 - decimales: 0
        header += self.payment_acquirer_id.nbsf_agreedment[:4]
        # 4 - Fecha de Archivo - tipo: numérico - long.: 8 - decimales: 0
        header += self.file_date.strftime("%Y%m%d")[:8]
        # 5 - Número de archivo - tipo: numérico - long.: 6 - decimales: 0
        header += "000001"
        # 6 - Monto - sumatoria - tipo: numérico - long.: 14 - decimales: 3
        header += str(int(round(total, 3)*1000)).rjust(14, "0")[:14]
        # 7 - Cantidad de regiatros - tipo: numérico - long.: 6 - decimales: 0
        header += str(count).rjust(6, "0")[:6]
        # 8 - Servicio - tipo: alfanumérico - long.: 10
        header += "CUOTAS".ljust(10, " ")[:10]
        # 9 - Espacio libre - tipo: alfanumérico - long.: 10
        header += " ".ljust(10, " ")[:10]
        # 10 - Fecha tope de presentación - tipo: numérico - long.: 8 - decimales: 0
        header += self.file_date.strftime("%Y%m%d")[:8]
        # 11 - Uso interno - tipo: alfanumérico - long.: 151
        header += ''.ljust(151, " ")[:151]
        header += "\r\n"

        # Direct Debit File
        direct_debit_file = self.env['direct.debit.file']
        filename = "NBSF" + self.payment_acquirer_id.nbsf_company + \
            '-' + self.file_date.strftime("%d%m%y") + '.txt'
        values = {
            'name': filename,
            'date': self.file_date,
            'next_business_days': self.imputation_business_days,
            'count': count,
            'total': total,
            'file': base64.b64encode("\n".join([header + data_registry]).encode('ascii')),
            'payment_acquirer_id': self.payment_acquirer_id.id,
            'description': self.payment_mode_id.name + ' ' + filename + ' ' + self.file_date.strftime('%d/%m/%Y'),
        }
        ddf = direct_debit_file.create(values)
