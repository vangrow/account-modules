# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.translate import _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _description = 'account.move.line'

    commission = fields.Float(
        string="Comisión",
        default=0.0,
        readonly=True,
        compute='_compute_commission'
    )

    @api.depends('discount','price_unit')
    def _compute_commission(self):
        for rec in self:
            rec.commission = abs(rec.quantity*(rec.price_unit * rec.discount)/100)