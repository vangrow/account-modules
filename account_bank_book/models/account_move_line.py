# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

import ast

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = "account.move.line"


    @api.model
    def create(self,vals):
        res = super(AccountMoveLine, self).create(vals)

        """
        bank_book_config_ids = self.env['bank.book.config'].search([('create_bank_book_entries','=',True)])

        for bank_book_configd_id in bank_book_config_ids:
            domain = domain = ast.literal_eval(bank_book_configd_id.bank_book_domain.replace('posted','draft'))
            for res_id in res:
                domain.insert(0, ['id', '=', res_id.id])
                account_move_line_id = res_id.search(domain)
                if account_move_line_id:
                    raise ValidationError("Test1: %s"%(res_id.search(domain)))
            #raise ValidationError("Test: %s"%(res.search(domain)))
        """
        return res

    def write(self,vals):
        res = super(AccountMoveLine, self).write(vals)
        """
        for rec in self:
            if self.env['ir.config_parameter'].sudo().get_param('create_bank_book_entries.create_entries'):
                account_bankbook_id = self.env['account.bankbook'].search([('account_move_line_id','=',rec.id)])
                if account_bankbook_id:
                    if any([item in vals for item in ['date','date_maturity']]):
                        account_bankbook_id.date_real_move = rec.date if not rec.date_maturity else rec.date_maturity
        """
        return res
    
    def unlink(self):
        """
        for rec in self:
            if self.env['ir.config_parameter'].sudo().get_param('create_bank_book_entries.create_entries'):
                account_bankbook_id = self.env['account.bankbook'].search([('account_move_line_id','=',rec.id)])
                if account_bankbook_id:
                    account_bankbook_id.unlink()
        """
        res = super(AccountMoveLine, self).unlink()
        return res