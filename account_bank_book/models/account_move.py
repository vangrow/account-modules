# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

import ast


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = "account.move"

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for rec in self:
            if 'state' in vals and self.env['ir.config_parameter'].sudo().get_param('create_bank_book_entries.create_entries'):
                if vals['state'] == 'posted':
                    domain = ast.literal_eval(
                        self.env['ir.config_parameter'].sudo().get_param('bank_book_domain.domain'))
                    domain.insert(0, ['move_id', '=', rec.id])
                    account_move_line_ids = self.env['account.move.line'].search(
                        [('move_id', '=', rec.id)])
                    for account_move_line_id in account_move_line_ids:
                        vals_bank_book = {
                            'date_real_move': account_move_line_id.date if not account_move_line_id.date_maturity else account_move_line_id.date_maturity,
                            'account_move_line_id': account_move_line_id.id,
                        }
                        if self.env['account.bankbook'].search([('account_move_line_id', '=', account_move_line_id.id)]):
                            record_id = self.env['account.bankbook'].write(vals_bank_book)
                        else:
                            record_id = self.env['account.bankbook'].create(vals_bank_book)
        return res
