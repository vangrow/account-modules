# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class DirectDebitFile(models.Model):
    _name = "direct.debit.file"
    _description = 'direct.debit.file'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Name",
        readonly=True
    )
    payment_acquirer_id = fields.Many2one(
        comodel_name="payment.acquirer",
        string="Payment Acquirer",
        readonly=True,
    )
    date = fields.Date(
        string="Date",
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('posted', 'Posted')
        ],
        string="State",
        default='draft',
    )
    next_business_days = fields.Integer(
        string="Next Business Days",
        readonly=True,
    )
    file = fields.Binary(
        string="File",
        readonly=True,
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
    response_direct_debit_file_ids = fields.One2many(
        comodel_name="response.direct.debit.file",
        inverse_name='direct_debit_file_id',
        string="Response Direct Debit File",
        ondelete='cascade',
    )
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.company.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda
                                  self: self.env.company.currency_id.id)

    def action_post(self):
        pass
 