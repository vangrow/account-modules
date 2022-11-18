# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.translate import _


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"
    _description = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('bccoopdd', "Banco Credicoop Débitos")],
        ondelete={'bccoopdd': 'set default'},
    )
    credicoop_company = fields.Char(
        string="Company"
    )
    credicoop_frequency = fields.Char(
        string="Frequency",
    )
    credicoop_bank = fields.Char(
        string="Bank",
    )


    @api.depends('provider')
    def _compute_view_configuration_fields(self):
        """ Override of payment to hide the credentials page.
        :return: None
        """
        super()._compute_view_configuration_fields()
        self.filtered(lambda acq: acq.provider == 'ccoopdd').show_credentials_page = False

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'ccoopdd':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_credicoop.credicoop_account_payment_method').id
