# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ResConfigSettingBankBook(models.TransientModel):
    _inherit = "res.config.settings"
    _description = 'res.config.settings'

    bank_book_domain = fields.Char(
        string="Default Domain",
        config_parameter='bank_book_domain.domain',
    )
    create_bank_book_entries = fields.Boolean(
        string="Create Bank Book Entries",
        config_parameter='create_bank_book_entries.create_entries',
    )
