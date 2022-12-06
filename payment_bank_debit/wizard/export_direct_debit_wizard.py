# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

import datetime
from pandas.tseries.offsets import BDay


class ExportDirectDebitWizard(models.TransientModel):
    _name = 'export.direct.debit.wizard'
    _description = "export.direct.debit.wizard"

    payment_acquirer_id = fields.Many2one(
        comodel_name="payment.acquirer",
        string="Payment Acquirer",
        domain=[('state', 'in', ['enabled', 'test'])],
    )
    payment_mode_id = fields.Many2one(
        comodel_name="account.payment.mode",
        string="Payment Mode",
    )
    file_date = fields.Date(
        string="Fecha",
        default=datetime.date.today()
    )
    imputation_business_days = fields.Integer(
        string="Next Business Days",
        default=((datetime.datetime.today() + BDay(2)) - datetime.datetime.today()).days
    )
    file_number = fields.Integer(
        sting="File Number",
        default=1
    )

    @api.onchange('payment_acquirer_id')
    def onchange_payment_acquirer_id(self):
        payment_method_id = self.env['account.payment.method'].search([('code','=',self.payment_acquirer_id.provider)])
        if payment_method_id:
            payment_mode_ids = self.env['account.payment.mode'].search([('payment_method_id','=',payment_method_id.id)])
            if payment_mode_ids:
                self.payment_mode_id = payment_mode_ids[0]
        domain = [('payment_method_id','=',payment_method_id.id)]
        res = {
            'domain': {
                'payment_mode_id': domain,
            }
        }
        return res
        
    def file_save(self):
        pass
  