# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.translate import _


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"
    _description = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('bnadd', "Banco de la Nación Argentina Débitos")],
        ondelete={'bnadd': 'set default'},
    )
   
    bna_bank = fields.Char(
        string="Bank"
    )
    bna_acc_type = fields.Char(
        string="Account Type",
    )
    bna_acc_number = fields.Char(
        string="Account",
    )
    

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'bnadd':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_bna.bna_account_payment_method').id
