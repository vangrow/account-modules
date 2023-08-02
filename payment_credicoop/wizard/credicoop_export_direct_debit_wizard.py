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
        if self.payment_acquirer_id.provider == 'bccoopdd':  # Debitos Directo Banco Credicoop
            self.credicoop_file_generator()
        return res
        

    def credicoop_file_generator(self):
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
                    'branch_number': invoice.partner_id.bank_ids[0].branch_number,
                    'amount_residual': invoice.amount_residual,
                    'currency_id': invoice.currency_id.id,
                    'imputation_date': self.file_date + BDay(self.imputation_business_days),
                    'document_number': invoice.l10n_latam_document_number,
                    'vat': "0" if not invoice.partner_id.vat else invoice.partner_id.vat,
                    'partner_id': invoice.partner_id.id,
                    'partner_name': invoice.partner_id.name,
                    'partner_country_id': invoice.partner_id.country_id.id,
                    'partner_ref': invoice.partner_id.ref,
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

            # 1 - Empresa - tipo: numérico - long.: 2 - decimales: 0
            data_registry += self.payment_acquirer_id.credicoop_company[:2]
            # 2 - Frecuencia - tipo: alfanumérico - long.: 1 - decimales: 0
            data_registry += self.payment_acquirer_id.credicoop_frequency[:1]
            # 3 - Banco - tipo: numérico - long.: 3 - decimales: 0
            data_registry += self.payment_acquirer_id.credicoop_bank[:3]
            # 4 - Sucursal - tipo: numérico - long.: 3 - decimales: 0
            data_registry += registry[acc_number][invoice]['branch_number'].rjust(3, "0")[:3]
            # 5 - Tipo de Cuenta - tipo: numérico - long.: 1 - decimales: 0
            data_registry += '0' if registry[acc_number][invoice]['account_type'] == 'cc' else '1'
            # 6 - Número de Cuenta - tipo: numérico - long.: 7 - decimales: 0
            data_registry += acc_number.rjust(7, "0")[:7]
            # 7 - Año de Vencimiento - tipo: numérico - long.: 2 - decimales: 0
            data_registry += (self.file_date + BDay(self.imputation_business_days)).strftime("%y")[:2]
            # 8 - Mes/Cuota de Vto. - tipo: numérico - long.: 2 - decimales: 0
            data_registry += (self.file_date + BDay(self.imputation_business_days)).strftime("%y")[:2]
            # 9 - Fecha de Vto. - tipo: numérico - long.: 6 - decimales: 0
            data_registry += (self.file_date + BDay(self.imputation_business_days)).strftime("%d%m%y")[:6]
            # 10 - Turno - tipo: numérico - long.: 3 - decimales: 0
            data_registry += '001'
            # 11 - Identificador - tipo: numérico - long.: 18 - decimales: 0
            data_registry += registry[acc_number][invoice]['partner_ref'].rjust(5, "0")[:5].ljust(18, " ")[:18]
            # 12 - Importe del Débito - tipo: numérico - long.: 11 - decimales: 2
            data_registry += str(int(round(total_registry, 2) * 100)).rjust(11, "0")[:11]
            # 13 - Importe 2 - tipo: numérico - long.: 11 - decimales: 2
            data_registry += '0'.rjust(11, "0")[:11]
            # 14 - Fecha de Pago - tipo: numérico - long.: 6 - decimales: 0
            data_registry += '0'.rjust(6, "0")[:6]
            # 15 - Resultado del Débito - tipo: alfnumérico - long.: 1 - decimales: 0
            data_registry += ' '
            # 16 - Moneda - tipo: alfnumérico - long.: 1 - decimales: 0
            data_registry += 'P'
            # 17 - Tipo de Débito - tipo: alfnumérico - long.: 1 - decimales: 0
            data_registry += 'D'
            # 18 - Filler - tipo: alfanumérico - long.: 11 - decimales: 0
            data_registry += ' '
            data_registry += "\r\n"

        # Direct Debit File
        direct_debit_file = self.env['direct.debit.file']
        filename = "MAIN1" + self.payment_acquirer_id.credicoop_company + \
            '_' + self.file_date.strftime("%d%m") + '.TXT'
        values = {
            'name': filename,
            'date': self.file_date,
            'next_business_days': self.imputation_business_days,
            'count': count,
            'total': total,
            'file': base64.b64encode("\n".join([data_registry[:-1]]).encode('ascii', errors='ignore')),
            'payment_acquirer_id': self.payment_acquirer_id.id,
            'description': self.payment_mode_id.name + ' ' + filename + ' ' + self.file_date.strftime('%d/%m/%Y'),
        }
        ddf = direct_debit_file.create(values)
        