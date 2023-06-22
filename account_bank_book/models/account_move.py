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
            bank_book_config_ids = self.env['bank.book.config'].sudo().search([('create_bank_book_entries','=',True)])
            for bank_book_config_id in bank_book_config_ids:
                if rec.state == 'draft' or rec.state == 'cancel':
                    for line_id in rec.line_ids:
                        self.env['account.bankbook'].sudo().search([('account_move_line_id', '=', line_id.id)]).unlink()
                    #if self.env['account.bankbook'].sudo().search([('account_move_line_id', '=', account_move_line_id.id)]):
                    #    raise ValidationError("Test: %s"%(rec.state))
                elif rec.state == 'posted':
                    domain = domain = ast.literal_eval(bank_book_config_id.bank_book_domain)
                    domain.insert(0, ['move_id', '=', rec.id])
                    account_move_line_ids = self.env['account.move.line'].search(domain)
                    
                    for account_move_line_id in account_move_line_ids:
                        vals = {
                            'date_real_move': account_move_line_id.date if not account_move_line_id.date_maturity else account_move_line_id.date_maturity,
                            'account_bank_book_id': bank_book_config_id.id,
                            'account_move_line_id': account_move_line_id.id,
                        }
                        if self.env['account.bankbook'].sudo().search([('account_move_line_id', '=', account_move_line_id.id)]):
                            record_id = self.env['account.bankbook'].sudo().write(vals)
                        else:
                            record_id = self.env['account.bankbook'].sudo().create(vals)               
        return res
    