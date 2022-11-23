# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.translate import _


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"
    _description = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('nbsfdd', "Banco Santa Fe Débitos")],
        ondelete={'nbsfdd': 'set default'},
    )
   
    nbsf_header = fields.Char(
        string="Header"
    )
    nbsf_company = fields.Char(
        string="Company",
    )
    nbsf_agreedment = fields.Char(
        string="Agreedment",
    )

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'nbsfdd':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_nbsf.nbsf_account_payment_method').id
