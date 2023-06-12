# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import tools, models, fields, api, _


class AccountArWithholdingLine(models.Model):
    """  """
    _name = "account.ar.withholding.line"
    _description = "account.ar.withholding.line"
    _auto = False
    _order = 'date asc, id asc'

    move_id = fields.Many2one(
        comodel_name='account.move', 
        string='', 
        auto_join=True
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Unposted'), 
            ('posted', 'Posted'),
            ('cancel', 'Cancel'),
        ],
        string="Status",
        readonly=True
    )
    account_payment_id = fields.Many2one(
        comodel_name='account.payment', 
        string='', 
        readonly=True,
        auto_join=True
    )
    account_payment_group_id = fields.Many2one(
        comodel_name='account.payment.group', 
        string='', 
        readonly=True,
        auto_join=True
    )
    account_payment_name = fields.Char(
        readonly=True
    )
    date = fields.Date(
        string="Date",
        readonly=True
    )
    withholding_number = fields.Char(
        readonly=True
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal', 
        string='Journal', 
        readonly=True, 
        auto_join=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner', 
        string='Partner', 
        readonly=True, 
        auto_join=True
    )
    partner_name = fields.Char(
        readonly=True
    )
    retencion_ganancia = fields.Char(
        readonly=True
    )
    codigo = fields.Char(
        readonly=True
    )
    concepto = fields.Char(
        readonly=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company', 
        string='Company', 
        readonly=True, 
        auto_join=True
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id', 
        readonly=True
    )
    tax_withholding_id = fields.Many2one(
        comodel_name='account.tax', 
        string='', 
        readonly=True, 
        auto_join=True
    )
    withholding_base_amount = fields.Monetary(
        readonly=True, 
        string='Importe Base de Retención', 
        currency_field='company_currency_id'
    )
    withholdable_invoiced_amount = fields.Monetary(
        readonly=True, 
        string='Importe imputado sujeto a Retención', 
        currency_field='company_currency_id'
    )
    withholdable_advanced_amount = fields.Monetary(
        readonly=True, 
        string='Importe a cuenta sujeto a Retención', 
        currency_field='company_currency_id'
    )
    accumulated_amount = fields.Monetary(
        readonly=True, 
        string='Monto Acumulado', 
        currency_field='company_currency_id'
    )
    total_amount = fields.Monetary(
        readonly=True, 
        string='Importe Total', 
        currency_field='company_currency_id'
    )
    withholding_non_taxable_minimum = fields.Monetary(
        readonly=True, 
        string='Mínimo No Imponible', 
        currency_field='company_currency_id'
    )
    withholding_non_taxable_amount = fields.Monetary(
        readonly=True, 
        string='Base No Imponible', 
        currency_field='company_currency_id'
    )
    withholdable_base_amount = fields.Monetary(
        readonly=True, 
        string='Importe Base de Retención', 
        currency_field='company_currency_id'
    )
    period_withholding_amount = fields.Monetary(
        readonly=True, 
        string='Retención del período', 
        currency_field='company_currency_id'
    )
    previous_withholding_amount = fields.Monetary(
        readonly=True, 
        string='Importe de Retenciones anteriores', 
        currency_field='company_currency_id'
    )
    computed_withholding_amount = fields.Monetary(
        readonly=True, 
        string='Importe de Retención Calculado', 
        currency_field='company_currency_id'
    )
   
    def open_payment_entry(self):
        self.ensure_one()
        return self.account_payment_id.get_formview_action()

    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, self._table)
        sql = """CREATE or REPLACE VIEW account_ar_withholding_line as (
        SELECT
            ap.id,
            ap.id as account_payment_id,
			apg.id as account_payment_group_id,
			apg.name as account_payment_name,
            apg.payment_date as date,
			am.id as move_id,
            am.state as state,
			am.journal_id as account_move_journal_id,
			aj.id as journal_id,
			aj.name as journal_name,
            ap.withholding_number as withholding_number,
            rp.name as partner_name,
			ap.withholding_base_amount as withholding_base_amount,
            ap.withholdable_invoiced_amount as withholdable_invoiced_amount,
			ap.withholdable_advanced_amount as withholdable_advanced_amount,
			ap.accumulated_amount as accumulated_amount,
			ap.total_amount as total_amount,
			ap.withholding_non_taxable_minimum as withholding_non_taxable_minimum,
			ap.withholding_non_taxable_amount as withholding_non_taxable_amount,
			ap.withholdable_base_amount as withholdable_base_amount,
			ap.period_withholding_amount as period_withholding_amount,
			ap.previous_withholding_amount as previous_withholding_amount,
			ap.computed_withholding_amount as computed_withholding_amount,
			apg.retencion_ganancias as retencion_ganancia,
			atga.codigo_de_regimen as codigo,
			atga.concepto_referencia as concepto,
			atga.porcentaje_inscripto,
			atga.porcentaje_no_inscripto,
			apg.regimen_ganancias_id,
            ap.tax_withholding_id as tax_withholding_id,
            ap.partner_id,
            apg.company_id as company_id
        FROM
            account_payment ap
        LEFT JOIN
            account_payment_group AS apg
            ON apg.id = ap.payment_group_id
		LEFT JOIN
			account_move AS am
			ON am.id = ap.move_id
		LEFT JOIN
			account_journal AS aj
			ON aj.id = am.journal_id
        LEFT JOIN
            res_partner AS rp
            ON rp.id = ap.partner_id
		LEFT JOIN
			afip_tabla_ganancias_alicuotasymontos AS atga
			ON apg.regimen_ganancias_id = atga.id
        WHERE
            ap.payment_type in ('outbound')
            and am.state in ('posted')
            and ap.withholding_number is not null
			and ap.tax_withholding_id is not null
        GROUP BY
            ap.id, rp.id, apg.id, am.id, aj.id, atga.id
        ORDER BY
            apg.payment_date
        )"""
        cr.execute(sql)