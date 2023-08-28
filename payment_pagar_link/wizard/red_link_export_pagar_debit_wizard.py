# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

import re
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
        if self.payment_acquirer_id.provider == 'rlpagar':  # Debitos Red Link Pagar
            self.red_link_pagar_refresh_file_generator()
        return res

    def red_link_pagar_refresh_file_generator(self):
        # Registro Datos
        registry = {}
        total = 0.0
        count = 0

        for invoice_id in self._context['active_ids']:
            invoice = self.env['account.move'].search(
                [('id', '=', invoice_id)])

            if invoice.state == 'posted' and invoice.partner_id.customer_payment_mode_id == self.payment_mode_id:
                if not invoice.partner_id.vat:
                    raise UserError("Error: El cliente %s de la factura %s no tiene DNI o CUIT asociado!!!" % (
                        invoice.partner_id.name, invoice.name))
                vat_number = invoice.partner_id.vat
                if vat_number not in registry:
                    registry[vat_number] = {}

                registry[vat_number]['%s' % (invoice_id)] = {
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

        refresh_initial_registry = ''
        # Refresh Registro Inicial
        # 1 - Identificación del registro - tipo: alfanumérico - long.: 13 - decimales: 0
        refresh_initial_registry += "HRFACTURACION"[:13]
        # 2 - Código de Ente - tipo: alfanumérico - long.: 3 - decimales: 0
        refresh_initial_registry += self.payment_acquirer_id.red_link_company[:3]
        # 3 - Fecha de Proceso - tipo: numérico - long.: 6 - decimales: 0
        refresh_initial_registry += self.file_date.strftime("%y%m%d")[:6]
        # 4 - Lote - tipo: numérico - long.: 5 - decimales: 0
        refresh_initial_registry += str(self.file_number).rjust(5, "0")[:5]
        # 5 - Filler - tipo: alfanumérico - long.: 104 - decimales: 0
        refresh_initial_registry += ' '.ljust(104, " ")[:104]
        refresh_initial_registry += "\r\n"

        refresh_data_registry = ''

        # Refresh Registro de Datos
        for vat_number in registry:
            total_registry = 0.0
            invoice_ids = []

            for invoice in registry[vat_number]:
                invoice_ids.append(invoice)
                total_registry = total_registry + \
                    registry[vat_number][invoice]['amount_residual']

            # Paymen Transaction
            payment_transaction = self.env['payment.transaction']
            values = {
                'amount': total_registry,
                'acquirer_id': self.payment_acquirer_id.id,
                'acquirer_reference': vat_number,
                'currency_id': registry[vat_number][invoice]['currency_id'],
                'reference': str(uuid4()),
                'partner_id': registry[vat_number][invoice]['partner_id'],
                'partner_country_id': registry[vat_number][invoice]['partner_country_id'],
                'invoice_ids': [(6, 0, invoice_ids)],
                'state': 'pending',
            }
            pt = payment_transaction.create(values)

            total = total + total_registry
            count += 1
            # 1 - Identificador de Deuda - tipo: numérico - long.: 5 - decimales: 0
            refresh_data_registry += '0' + self.file_date.strftime("%m%y")[:4]
            # 2 - Identificador de Concepto - tipo: numérico - long.: 3 - decimales: 0
            refresh_data_registry += '1'.rjust(3, "0")[:3]
            # 3 - Identificador de usuario - tipo: numérico - long.: 19 - decimales: 0
            vat = re.sub('[^0-9]+', '', registry[vat_number][invoice]['vat'])
            refresh_data_registry += vat.rjust(11, "0").ljust(19, " ")[:19]
            # 4 - Fecha primer venc. - tipo: numérico - long.: 6 - decimales: 0
            refresh_data_registry += (self.file_date + BDay(
                self.imputation_business_days)).strftime("%y%m%d")[:6]
            # 5 - Importe primer venc. - tipo: numérico - long.: 12 - decimales: 2
            refresh_data_registry += str(int(round(total_registry, 3)
                                         * 100)).rjust(12, "0")[:12]
            # 6 - Fecha segundo venc. - tipo: numérico - long.: 6 - decimales: 0
            refresh_data_registry += "0".rjust(6, "0")[:6]
            # 7 - Importe segundo venc. - tipo: numérico - long.: 12 - decimales: 2
            refresh_data_registry += "0".rjust(12, "0")[:12]
            # 8 - Fecha tercer venc. - tipo: numérico - long.: 6 - decimales: 0
            refresh_data_registry += "0".rjust(6, "0")[:6]
            # 9 - Importe tercer venc. - tipo: numérico - long.: 12 - decimales: 2
            refresh_data_registry += "0".rjust(12, "0")[:12]
            # 10 - Discrecional - tipo: alfanumérico - long.: 50 - decimales: 0
            refresh_data_registry += " ".rjust(50, " ")[:50]
            refresh_data_registry += "\r\n"

        refresh_final_registry = ''
        # Refresh Registro Final
        # 1 - Identificación del registro - tipo: alfanumérico - long.: 13 - decimales: 0
        refresh_final_registry += "TRFACTURACION"[:13]
        # 2 - Cantidad de registros - tipo: numérico - long.: 8 - decimales: 0
        refresh_final_registry += str(count + 2).rjust(8, "0")[:8]
        # 3 - Total primer venc. - tipo: numérico - long.: 16 - decimales: 2
        refresh_final_registry += str(int(round(total, 3)
                                      * 100)).rjust(18, "0")[:18]
        # 4 - Total segundo venc. - tipo: numérico - long.: 16 - decimales: 2
        refresh_final_registry += "0".rjust(18, "0")[:18]
        # 5 - Total tercer venc. - tipo: numérico - long.: 16 - decimales: 2
        refresh_final_registry += "0".rjust(18, "0")[:18]
        # 6 - Filler - tipo: alfanumérico - long.: 56 - decimales: 0
        refresh_final_registry += ' '.ljust(56, " ")[:56]
        refresh_final_registry += "\r\n"

        # Direct Debit File
        direct_debit_file = self.env['direct.debit.file']
        month = f'{int(self.file_date.strftime("%m")):x}'
        filename = "P" + self.payment_acquirer_id.red_link_company[:3] + str(
            self.file_number) + month.upper() + self.file_date.strftime("%d") + '.txt'

        # Control Registro Inicial
        control_initial_registry = ''
        # 1 - Identificación del registro - tipo: alfanumérico - long.: 9 - decimales: 0
        control_initial_registry += "HRPASCTRL"[:9]
        # 2 - Fecha de Generación - tipo: numérico - long.: 8 - decimales: 0
        control_initial_registry += self.file_date.strftime("%Y%m%d")[:8]
        # 3 - Código de Ente - tipo: alfanumérico - long.: 3 - decimales: 0
        control_initial_registry += self.payment_acquirer_id.red_link_company[:3]
        # 4 - Nombre Archivo - tipo: alfanumérico - long.: 8 - decimales: 0
        control_initial_registry += filename[:8]
        # 5 - Longitud del Archivo - tipo: numérico - long.: 8 - decimales: 0
        control_initial_registry += str(
            len(refresh_initial_registry+refresh_data_registry+refresh_final_registry)).rjust(10, "0")[:10]
        # 6 - Filler - tipo: alfanumérico - long.: 56 - decimales: 0
        control_initial_registry += ' '.ljust(37, " ")[:37]
        control_initial_registry += "\r\n"

        # Control Registro Datos
        control_data_registry = ''
        # 1 - Identificación de datos - tipo: alfanumérico - long.: 5 - decimales: 0
        control_data_registry += "LOTES"[:5]
        # 2 - Lote - tipo: numérico - long.: 5 - decimales: 0
        control_data_registry += str(self.file_number).rjust(5, "0")[:5]
        # 3 - Cantidad de registros del Lote - tipo: numérico - long.: 8 - decimales: 0
        control_data_registry += str(count + 2).rjust(8, "0")[:8]
        # 4 - Importe primer vencimiento - tipo: numérico - long.: 18 - decimales: 2
        control_data_registry += str(int(round(total, 3)
                                     * 100)).rjust(18, "0")[:18]
        # 5 - Importe segundo vencimiento - tipo: numérico - long.: 18 - decimales: 2
        control_data_registry += "0".rjust(18, "0")[:18]
        # 6 - Importe tercer vencimiento - tipo: numérico - long.: 18 - decimales: 2
        control_data_registry += "0".rjust(18, "0")[:18]
        # 7 - Filler - tipo: alfanumérico - long.: 3 - decimales: 0
        control_data_registry += ' '.ljust(3, " ")[:3]
        control_data_registry += "\r\n"

        # Control Registro Final
        control_final_registry = ''
        # 1 - Identificación de fin - tipo: alfanumérico - long.: 5 - decimales: 0
        control_final_registry += "FINAL"[:5]
        # 2 - Cantidad total de registros - tipo: numérico - long.: 8 - decimales: 0
        control_final_registry += str(count + 2).rjust(8, "0")[:8]
        # 3 - Importe primer vencimiento - tipo: numérico - long.: 18 - decimales: 2
        control_final_registry += str(int(round(total, 3)
                                     * 100)).rjust(18, "0")[:18]
        # 4 - Importe segundo vencimiento - tipo: numérico - long.: 18 - decimales: 2
        control_final_registry += "0".rjust(18, "0")[:18]
        # 5 - Importe tercer vencimiento - tipo: numérico - long.: 18 - decimales: 2
        control_final_registry += "0".rjust(18, "0")[:18]
        # 6 - Fecha último vencimiento - tipo: alfanumérico - long.: 8 - decimales: 0
        control_final_registry += (self.file_date + BDay(self.imputation_business_days)).strftime("%Y%m%d")[:8]      
        control_final_registry += "\r\n"
        
        control_filename = "C" + self.payment_acquirer_id.red_link_company[:3] + str(
            self.file_number) + month.upper() + self.file_date.strftime("%d") + '.txt'
        
        values = {
            'name': filename,
            'control_file_name': control_filename,
            'date': self.file_date,
            'next_business_days': self.imputation_business_days,
            'count': count,
            'total': total,
            'file': base64.b64encode("\n".join([refresh_initial_registry + refresh_data_registry + refresh_final_registry]).encode('ascii', errors='ignore')),
            'control_file': base64.b64encode("\n".join([control_initial_registry + control_data_registry + control_final_registry]).encode('ascii', errors='ignore')),
            'payment_acquirer_id': self.payment_acquirer_id.id,
            'description': self.payment_mode_id.name + ' ' + filename + ' ' + self.file_date.strftime('%d/%m/%Y'),
        }
        ddf = direct_debit_file.create(values)
