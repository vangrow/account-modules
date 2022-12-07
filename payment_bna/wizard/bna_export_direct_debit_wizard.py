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
        if self.payment_acquirer_id.provider == 'bnadd':  # Debitos Directo Banco de la Nación Argentina
            self.bna_file_generator()
        return res
        

    def bna_file_generator(self):
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
                    'company_name': self.env.user.company_id.name,
                    'date': self.file_date,
                }
            
        
        registry_1 = ''
        # Registro 1
        # 1 - Tipo de Registro - tipo: numérico - long.: 1 - decimales: 0
        registry_1 += '1'
        # 2 - Casa Sucursal - tipo: numérico - long.: 4 - decimales: 0
        registry_1 +=  self.payment_acquirer_id.bna_bank[:4]
        # 3 - Tipo de Cuenta - tipo: numérico - long.: 2 - decimales: 0
        registry_1 +=  self.payment_acquirer_id.bna_acc_type[:2]
        # 4 - Cuenta - tipo: numérico - long.: 10 - decimales: 0
        registry_1 +=  self.payment_acquirer_id.bna_acc_number[:10]
        # 5 - Moneda - tipo: alfanumérico - long.: 1 - decimales: 0
        registry_1 +=  'P'
        # 6 - Identificador - tipo: alfanumérico - long.: 1 - decimales: 0
        registry_1 +=  'E'
        # 7 - Secuencia - tipo: numérico - long.: 4 - decimales: 0
        registry_1 +=  self.file_date.strftime("%m")[:2] + str(self.file_number).rjust(2,"0")[:2]
        # 8 - Fecha imputación - tipo: numérico - long.: 8 - decimales: 0
        registry_1 += (self.file_date + BDay(self.imputation_business_days)).strftime("%Y%m%d")[:8]
        # 9 - Indicador de Empleados BNA - tipo: alfanumérico - long.: 3 - decimales: 0
        registry_1 += 'REE'
        registry_1 += "\r\n"

        # Registro 2
        registry_2 = ''
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

            # 1 - Tipo de Registro - tipo: numérico - long.: 1 - decimales: 0
            registry_2 += '2'
            # 2 - Sucursal Banco Cliente - tipo: numérico - long.: 4 - decimales: 0
            registry_2 += registry[acc_number][invoice]['branch_number'].rjust(4, "0")[:4]
            # 3 - Typo de Cuenta - tipo: alfanumérico - long.: 2 - decimales: 0
            registry_2 += 'CC' if registry[acc_number][invoice]['account_type'] == 'cc' else 'CA'
            # 4 - Cuenta - tipo: numérico - long.: 11 - decimales: 0
            registry_2 += acc_number.rjust(11, "0")[:11]
            # 5 - Importe - tipo: numérico - long.: 15 - decimales: 2
            registry_2 += str(int(round(total_registry, 2) * 100)).rjust(15, "0")[:15]
            # 6 - Fecha de Vencimiento - tipo: numérico - long.: 8 - decimales: 0
            registry_2 += '0'.rjust(8, "0")[:8]
            # 7 - Estado - tipo: numérico - long.: 1 - decimales: 0
            registry_2 += '0'
            # 8 - Motivo de Rechazo - tipo: alfanumérico - long.: 30 - decimales: 0
            registry_2 += ' '.ljust(30, " ")[:30]
            # 9 - Concepto de Débito - tipo: alfanumérico - long.: 10 - decimales: 0
            registry_2 += registry[acc_number][invoice]['company_name'].upper().ljust(10, " ")[:10]
            # 10 - Filler - tipo: alfanumérico - long.: 46 - decimales: 0
            registry_2 += ' '.ljust(46, " ")[:46]
            registry_2 += "\r\n"

        # Registro 3
        registry_3 = ''
        # 1 - Tipo de Registro - tipo: numérico - long.: 1 - decimales: 0
        registry_3 += '3'
        # 2 - Total a Debitar - tipo: numérico - long.: 15 - decimales: 2
        registry_3 += str(int(round(total, 2) * 100)).rjust(15, "0")[:15]
        # 3 - Cantidad de Registros - tipo: numérico - long.: 6 - decimales: 0
        registry_3 +=  str(count).rjust(6, "0")[:6]
        # 4 - Total Débitos no aplicados - tipo: numérico - long.: 15 - decimales: 2
        registry_3 += '0'.rjust(15, "0")[:15]
        # 4 - Cantidad de Registros no aplicados - tipo: numérico - long.: 6 - decimales: 0
        registry_3 += '0'.rjust(6, "0")[:6]
        # 5 - Filler - tipo: alfanumérico - long.: 85 - decimales: 0
        registry_3 += ' '.ljust(85, " ")[:85]
        #registry_3 += "\r\n"

        # Direct Debit File
        direct_debit_file = self.env['direct.debit.file']
        filename = "BNA" + self.payment_acquirer_id.company_id.name + \
            '-' + self.file_date.strftime("%d%m%y") + '.txt'
        values = {
            'name': filename,
            'date': self.file_date,
            'next_business_days': self.imputation_business_days,
            'count': count,
            'total': total,
            'file': base64.b64encode("\n".join([registry_1 + registry_2 + registry_3]).encode('ascii', errors='ignore')),
            'payment_acquirer_id': self.payment_acquirer_id.id,
            'description': self.payment_mode_id.name + ' ' + filename + ' ' + self.file_date.strftime('%d/%m/%Y'),
        }
        ddf = direct_debit_file.create(values)
        