# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

import datetime


class ResponseDirectDebitFile(models.Model):
    _name = "response.direct.debit.file"
    _description = 'response.direct.debit.file'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Name",
    )
    file_number = fields.Char(
        string="File Number",
        readonly=True
    )
    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('posted', 'Posted')
        ],
        string="State",
        default='draft',
    )
    direct_debit_file_id = fields.Many2one(
        comodel_name='direct.debit.file',
        String="Direct Debit File",
        readonly=True,
    )
    date = fields.Date(
        string="Date",
        readonly=True,
        default=datetime.date.today()
    )
    file = fields.Binary(
        string="File",
    )
    description = fields.Char(
        string="Description",
    )
    count = fields.Integer(
        string="Entry Count",
        readonly=True
    )
    total = fields.Float(
        string="Total",
        readonly=True
    )
    total_ok = fields.Float(
        string="Total Ok",
        readonly=True
    ) 
    payment_count_ok = fields.Integer(
        string="Payment Count Ok",
        readonly=True
    )
    payment_count_ko = fields.Integer(
        string="Payment Count Ko",
        readonly=True
    )
    # Related fields
    payment_acquirer_id = fields.Many2one(
        related='direct_debit_file_id.payment_acquirer_id',
        string="Payment Acquirer",
    )

    def action_post(self):
        pass
 