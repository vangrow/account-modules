# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _


class AccountBankBook(models.Model):
    _name = 'account.bankbook'
    _description = "account.bankbook"

    date_real_move = fields.Date(
        string="Date Real Move",
        readonly=True,
    )
    account_move_line_id = fields.Many2one(
        comodel_name="account.move.line",
        string="Account Move Line",
        readonly=True
    ) 
    search_ids = fields.Char(
        compute='_compute_search_ids',
        search='search_ids_search',
    )
    # Related fields
    date = fields.Date(
        related='account_move_line_id.date',
    )
    date_maturity = fields.Date(
        related='account_move_line_id.date_maturity',
    )
    journal_id = fields.Many2one(
        related='account_move_line_id.journal_id',
    )
    move_id = fields.Many2one(
        related='account_move_line_id.move_id',
    )
    account_id = fields.Many2one(
        related='account_move_line_id.account_id',
    )
    partner_id = fields.Many2one(
        related='account_move_line_id.partner_id',
    )
    ref = fields.Char(
        related='account_move_line_id.ref',
    )
    name = fields.Char(
        related='account_move_line_id.name',
    )
    currency_id = fields.Many2one(
        related='account_move_line_id.currency_id',
    )
    debit = fields.Monetary(
           related='account_move_line_id.debit',
    )
    credit = fields.Monetary(
           related='account_move_line_id.credit',
    )
    balance = fields.Monetary(
           related='account_move_line_id.balance'
    )

    def _compute_search_ids(self):
        print('my compute')

    def search_ids_search(self, operator, operand):
        obj = self.env['account.bankbook'].search([(1,'=',1)]).ids
        return [('id', 'in', obj)]
    
    
