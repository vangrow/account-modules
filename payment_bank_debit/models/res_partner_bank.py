# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"
    _description = 'res.partner.bank'

    _sql_constraints = [
        ('unique_number', 'unique(sanitized_acc_number, company_id, partner_id)', 'Account Number must be unique'),
    ]

    branch_number = fields.Char(
        string="Branch Number"
    )
    account_type = fields.Selection(
        string="Account Type",
        selection=[
            ('ca', 'Caja de Ahorro'),
            ('cc', 'Cuenta Corriente')
        ],
        default='ca'
    )
