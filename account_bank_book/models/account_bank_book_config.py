# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import string
from typing_extensions import Required
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _


class AccountBankBookConfig(models.Model):
    _name = "bank.book.config"
    _description = 'bank.book.config'

    name = fields.Char(
        string="Name",
        required=True
    )
    description = fields.Char(
        string="Description"
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Journal",
        Required=True,
        domain=[('type','=','bank')]
    )
    bank_book_domain = fields.Char(
        string="Default Domain",
    )
    create_bank_book_entries = fields.Boolean(
        string="Create Bank Book Entries",
    )
