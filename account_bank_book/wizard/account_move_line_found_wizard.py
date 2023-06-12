# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _


class AccountMoveLineFound(models.TransientModel):
    _name = 'account.move.line.found'
    _description = "account.move.line.found"

    real_date = fields.Date(
        string="Real Date",
    )
    bank_book_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string="Journal",
        readonly=True,
    )
    account_move_line_id = fields.Many2one(
        comodel_name='account.move.line',
        readonly=True,
    )
    account_move_line_search = fields.Many2one(
        comodel_name="account.move.line.search",
        readonly=True,
    )

    def unlink_found(self):
        record_ids = self._context.get('account_move_line_found_ids')
        record_ids.remove(self.id)
        self.unlink()
        res = {
            'name': _("Found Account Move Line"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': False,
            'res_model': 'account.move.line.search',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {
                'account_move_line_found_ids': record_ids,
            },
        }
        return res
