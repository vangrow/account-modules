# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.translate import _


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"
    _description = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('rlpagar', "Red Link Pagar")],
        ondelete={'rlpagar': 'set default'},
    )
    red_link_company = fields.Char(
        string="Company"
    )
   
    
    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'rlpagar':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_pagar_link.pagar_link_account_payment_method').id
