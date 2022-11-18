# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

import datetime
import base64


class ResponseDirectDebitFile(models.Model):
    _name = "response.direct.debit.file"
    _description = 'response.direct.debit.file'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Name",
    )
    file_number = fields.Char(
        string="File Number",
        readonly=True
    )
    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('posted', 'Posted')
        ],
        string="State",
        default='draft',
    )
    direct_debit_file_id = fields.Many2one(
        comodel_name='direct.debit.file',
        String="Direct Debit File",
        readonly=True,
    )
    date = fields.Date(
        string="Date",
        readonly=True,
        default=datetime.date.today()
    )
    file = fields.Binary(
        string="File",
    )
    description = fields.Char(
        string="Description",
    )
    count = fields.Integer(
        string="Entry Count",
        readonly=True
    )
    total = fields.Float(
        string="Total",
        readonly=True
    )
    total_ok = fields.Float(
        string="Total Ok",
        readonly=True
    ) 
    payment_count_ok = fields.Integer(
        string="Payment Count Ok",
        readonly=True
    )
    payment_count_ko = fields.Integer(
        string="Payment Count Ko",
        readonly=True
    )
    # Related fields
    payment_acquirer_id = fields.Many2one(
        related='direct_debit_file_id.payment_acquirer_id',
        string="Payment Acquirer",
    )

    def action_post(self):
        if self.payment_acquirer_id.provider == 'nbsfdd':  # Debitos Directo Nuevo Banco de Santa Fe
            self.nbsf_file_process()

    def nbsf_file_process(self):
        file_string = base64.b64decode(self.file).decode('utf-8').split('\n')

        # Registro Cabecera
        # 1 - Cabecera - tipo: numérico - long.: 4 - decimales: 0
        header = file_string[0][:4]
        if header != "9997":
            raise ValidationError("Test: Error in response file header!!!")
        # 2 - Empresa - tipo: numérico - long.: 4 - decimales: 0
        company = file_string[0][4:8]
        if company != self.payment_acquirer_id.nbsf_company:
            raise ValidationError("Test: Error in response file company!!!")
        # 3 - Convenio - tipo: numérico - long.: 4 - decimales: 0
        agreedment = file_string[0][8:12]
        if agreedment != self.payment_acquirer_id.nbsf_agreedment:
            raise ValidationError("Test: Error in response file agreedment!!!")
        # 4 - Fecha de Archivo - tipo: numérico - long.: 8 - decimales: 0
        self.date = datetime.datetime.strptime(file_string[0][12:20], "%Y%m%d")
        # 5 - Número de archivo - tipo: numérico - long.: 6 - decimales: 0
        self.file_number = file_string[0][20:26]
        # 6 - Monto - sumatoria - tipo: numérico - long.: 14 - decimales: 3
        self.total = float(file_string[0][26:40])/1000
        # 7 - Cantidad de regiatros - tipo: numérico - long.: 6 - decimales: 0
        self.count = int(file_string[0][40:46])

        # Registro Datos
        payment_ok = 0
        total_ok = 0.0
        payment_ko = 0
        for data_registry in file_string[1:]:
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
            
        self.payment_count_ok = payment_ok
        self.payment_count_ko = payment_ko
        self.total_ok = total_ok
        self.state = 'posted'
