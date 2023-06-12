# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from importlib.metadata import requires
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

import datetime
import ast

import logging
_logger = logging.getLogger(__name__)


class AccountMoveLineSearch(models.TransientModel):
    _name = 'account.move.line.search'
    _description = "account.move.line.search"

    date_from = fields.Date(
        string="Date From",
        required=True,
        default=lambda self: self.env.context.get(
            'date_from', datetime.datetime.today().replace(day=1))
    )
    date_to = fields.Date(
        string="Date To",
        required=True,
        default=lambda self: self.env.context.get(
            'date_to', datetime.datetime.today())
    )
    account_bank_book_id = fields.Many2one(
        string="Bank Book",
        required=True,
        comodel_name='bank.book.config',
        default=lambda self: self.env.context.get(
            'account_bank_book_id', False)
    )
    account_move_line_found_ids = fields.One2many(
        comodel_name='account.move.line.found',
        inverse_name='account_move_line_search',
        default=lambda self: self.env.context.get(
            'account_move_line_found_ids', False),
        readonly=True,
    )
    # Related Fields
    domain = fields.Char(
        string="Domain",
        related='account_bank_book_id.bank_book_domain',
    )

    @api.constrains('date_to')
    def _check_date_to(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError(
                    "The Date to cannot be set in the past of Date from")

    def account_move_line_search(self):
        self.env['account.move.line.found'].search([]).unlink()
        domain = ast.literal_eval(self.domain)
        domain.insert(0, ['date', '<=', self.date_to])
        domain.insert(0, ['date', '>=', self.date_from])

        account_move_line_ids = self.env['account.move.line'].search(domain)

        for account_move_line_id in account_move_line_ids:
            vals = {
                'real_date': account_move_line_id.date if not account_move_line_id.date_maturity else account_move_line_id.date_maturity,
                'bank_book_journal_id': self.account_bank_book_id.journal_id.id,
                'account_move_line_id': account_move_line_id.id,
            }
            record_id = self.env['account.move.line.found'].create(vals)

        record_ids = self.env['account.move.line.found'].search([])
        
        res = {
            'name': _("Found Account Move Line"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': False,
            'res_model': 'account.move.line.search',
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'new',
            'context': {
                'date_to': self.date_to,
                'date_from': self.date_from,
                'account_bank_book_id': self.account_bank_book_id.id,
                'account_move_line_found_ids': record_ids.ids,
            },
        }
        return res

    def account_move_line_save(self):
        record_ids = self.env['account.move.line.found'].search([])
        for record_id in record_ids:
            vals = {
                'date_real_move': record_id.real_date,
                'bank_book_journal_id': record_id.bank_book_journal_id.id,
                'account_move_line_id': record_id.account_move_line_id.id,
            }
            if self.env['account.bankbook'].search([('account_move_line_id', '=', record_id.account_move_line_id.id)]):
                record_id = self.env['account.bankbook'].write(vals)
            else:
                record_id = self.env['account.bankbook'].create(vals)
