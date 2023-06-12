# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _
from collections import OrderedDict
from odoo.tools.misc import format_date
from odoo.tools.float_utils import float_split_str
import re
import json
import base64
import io


class L10nARWithholdingReport(models.AbstractModel):
    _inherit = "account.report"
    _description = 'account.report'

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_all_entries = False

    def _get_country_for_fiscal_position_filter(self, options):
        return self.env.ref('base.ar')

    def _get_report_name(self):
        name = super(L10nARWithholdingReport, self)._get_report_name()
        if self._context.get('journal_type') in ['cash'] and self._context.get('report') == 'withholding':
            name = _("Retenciones de Impuesto a las ganancias")
        return name

    def _set_context(self, options):
        ctx = super(L10nARWithholdingReport, self)._set_context(options)
        if options.get('journal_type'):
            ctx['journal_type'] = options.get('journal_type')
        return ctx

    def print_pdf(self, options):
        options.update({
            'journal_type': self.env.context.get('journal_type')
        })
        return super(L10nARWithholdingReport, self).print_pdf(options)

    def print_xlsx(self, options):
        options.update({
            'journal_type': self.env.context.get('journal_type')
        })
        return super(L10nARWithholdingReport, self).print_xlsx(options)

    @api.model
    def _get_dynamic_columns(self, options):
        """ Show or not the VAT 2.5% and VAT 5% columns if this ones are active/inactive """
        res = []
        """
        if self.env['account.tax'].search([('type_tax_use', '=', options.get('journal_type')), ('tax_group_id.l10n_ar_vat_afip_code', '=', '9')]):
            res.append({'sql_var': 'vat_25', 'name': _('VAT 2,5%')})
        if self.env['account.tax'].search([('type_tax_use', '=', options.get('journal_type')), ('tax_group_id.l10n_ar_vat_afip_code', '=', '8')]):
            res.append({'sql_var': 'vat_5', 'name': _('VAT 5%')})
        """
        return res

    def _get_columns_name(self, options):
        if not options.get('journal_type'):
            options.update(
                {'journal_type': self.env.context.get('journal_type', 'cash')})
        dynamic_columns = [item.get('name')
                           for item in self._get_dynamic_columns(options)]
        return [
            {'name': _("Date"), 'class': 'date'},
            {'name': _("Number"), 'class': 'text-left'},
            {'name': _("Reference"), 'class': 'text-left'},
            {'name': _("Proveedor"), 'class': 'text-left'},
            {'name': _("Importe Base"), 'class': 'text-left'},
            {'name': _("Importe Imputado"), 'class': 'text-left'},
            {'name': _("Importe a Cuenta"), 'class': 'text-left'},
            {'name': _("Monto Acumulado"), 'class': 'text-left'},
            {'name': _("Importe Total"), 'class': 'text-left'},
            {'name': _("Mínimo no Imponible"), 'class': 'text-left'},
            {'name': _("Base no Imponible"), 'class': 'text-left'},
            {'name': _("Base de Retención"), 'class': 'text-left'},
            {'name': _("Retención del Período"), 'class': 'text-left'},
            {'name': _("Retención Anterior"), 'class': 'text-left'},
            {'name': _("Total"), 'class': 'text-left'},
        ]

    @api.model
    def _get_lines(self, options, line_id=None):
        journal_type = options.get('journal_type')
        if not journal_type:
            journal_type = self.env.context.get('journal_type', 'cash')
            options.update({'journal_type': journal_type})
        lines = []
        line_id = 0
        domain = self._get_lines_domain(options)

        dynamic_columns = [item.get('sql_var')
                           for item in self._get_dynamic_columns(options)]
        totals = {}.fromkeys(dynamic_columns + ['total'], 0)
        for rec in self.env['account.ar.withholding.line'].search_read(domain):

            for item in dynamic_columns:
                totals[item] += rec[item]
            totals['total'] += rec['computed_withholding_amount']

            lines.append({
                'id': rec['id'],
                'name': format_date(self.env, rec['date']),
                'class': 'date' + (' text-muted' if rec['state'] != 'posted' else ''),
                'level': 2,
                'model': 'account.ar.withholding.line',
                'caret_options': 'account.payment',
                'columns': [
                    {'name': rec['withholding_number']},
                    {'name': rec['concepto']},
                    {'name': rec['partner_name']},
                    {'name': rec['withholding_base_amount']},
                    {'name': rec['withholdable_invoiced_amount']},
                    {'name': rec['withholdable_advanced_amount']},
                    {'name': rec['accumulated_amount']},
                    {'name': rec['total_amount']},
                    {'name': rec['withholding_non_taxable_minimum']},
                    {'name': rec['withholding_non_taxable_amount']},
                    {'name': rec['withholdable_base_amount']},
                    {'name': rec['period_withholding_amount']},
                    {'name': rec['previous_withholding_amount']},
                    {'name': rec['computed_withholding_amount']},
                ],
            })
            line_id += 1

        lines.append({
            'id': 'total',
            'name': _('Total'),
            'class': 'o_account_reports_domain_total',
            'level': 0,
            'columns': [
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': self.format_value(totals['total'])},
            ],
        })
        return lines

    def get_report_filename(self, options):
        """ Return the name that will be used for the file when downloading pdf, xlsx, txt_file, etc """
        journal_type = options.get('journal_type')
        filename = {'withholding': 'Retenciones de Impuestos a las Ganancias'}.get(
            journal_type, 'Retenciones')
        return "%s_%s" % (filename, options['date']['date_to'])

    def _get_reports_buttons(self, options):
        """ Add buttons to print the txt files used for Withholding to report books """
        buttons = super(L10nARWithholdingReport,
                        self)._get_reports_buttons(options)
        if self._context.get('report') == 'withholding':
            buttons += [{'name': _('Retenciones (TXT)'), 'sequence': 3,
                         'action': 'export_withholding_book_files', 'file_export_type': _('TXT')}]
        return buttons
    
    def _get_txt_withholding_datas(self, options):
        state = options.get('all_entries') and 'all' or 'posted'
        if state != 'posted':
            raise UserError(_('Can only generate TXT files using posted entries.'
                              ' Please remove Include unposted entries filter and try again'))
        data_registry = ''
        domain = self._get_lines_domain(options)
        for rec in self.env['account.ar.withholding.line'].search_read(domain):
            # 1 - Código de comprobante - tipo: numérico - long.: 2 - decimales: 0 -- Si (Conceptos de Descuento - Conceptos de Haberes < 0) => 08 sino 07
            data_registry += '06'
            # 2 - Fecha de emisión del comprobante (DD/MM/AAAA) - long.: 10 - decimales 0 -- Fecha emisión liquidación
            data_registry += rec.get('date').strftime("%d/%m/%Y")[:10]
            # 3 - Número del comprobante - long.: 16 - decimales 0 
            data_registry += re.sub('[^0-9]', '', rec.get('withholding_number')).ljust(16, " ")[:16]
            # 4 - Importe del comprobante - long.: 16 - decimales 2 -- 
            data_registry += _("%.2f"%rec.get('withholding_base_amount')).replace('.',',').rjust(16, " ")[:16]
            # 5 - Código de impuesto - long.: 4 - decimales 0
            data_registry += '0217'
            # 6 - Código de Régimen - long.: 3 - decimales 0
            data_registry += rec.get('codigo').rjust(3, "0")[:3]
            # 7 - Código de operación - long.: 1 - decimales 0
            data_registry += '1'
            # 8 - Base de cálculo - long.: 14 - decimales 2
            data_registry += _("%.2f"%rec.get('withholdable_base_amount')).replace('.',',').rjust(14, " ")[:14]
            # 9 - Fecha de emisión de la retención (DD/MM/AAAA) - long.: 10 - decimales 0 -- Fecha emisión liquidación
            data_registry += rec.get('date').strftime("%d/%m/%Y")[:10]
            # 10 - Código de condición - long.: 2 - decmales 0
            data_registry += '01'
            # 11 - Retención practicada a sujetos suspendidos según: - long.: 1 - decimales 0	
            data_registry += '0'
            # 12 - Importe de retención	- long.: 14 - decimales 2
            data_registry += _("%.2f"%rec.get('computed_withholding_amount')).replace('.',',').rjust(14, " ")[:14]
            # 13 - Porcentaje de exclusión - long.: 6 - decimales 2
            data_registry += "0,00".rjust(6, " ")[:6]
            # 14 - Fecha publicación o de finalización de la vigencia - long.: 10 - decimales 0
            data_registry += ' '.rjust(10, " ")[:10]
            # 15 - Tipo de documento del retenido - long.: 2 - decimales 0
            data_registry += '80'
            # 16 - Número de documento del retenido	- long 20 - decimales 0
            vat = re.sub('[^0-9]', '',self.env['res.partner'].search([('id','=',rec.get('partner_id')[0])]).vat)
            data_registry += vat.ljust(20, " ")[:20]
            # 17 - Número de certificado original - long.: 14 - decimales 0
            data_registry += '0'.rjust(14, "0")[:14]
            # 18 - Denominación del ordenante - long.: 30 - decimales 0
            data_registry += ' '.rjust(30, " ")[:30]
            # 19 - Acrecentamiento - long.: 1 - decimales 0
            data_registry += '0'
            # 20 - Cuit del país retenido - long.: 11 - decimales 0
            data_registry += ' '.rjust(11, " ")[:11]
            # 21 - Cuit del país retenido - long.: 11 - decimales 0
            data_registry += ' '.rjust(11, " ")[:11]
            data_registry += "\r\n"
        return data_registry 

    def export_withholding_book_files(self, options):
        """ Button that lets us export the Withholding book zip which contains the files that we upload to AFIP for Withholding Book """
        file_name = 'SICORE '+options['date']['date_from'] + ' ' + options['date']['date_to']+'.txt'
        data = self._get_txt_withholding_datas(options)
        values = {
            'name': file_name,
            'store_fname': 'print_file_name.txt',
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': base64.b64encode(data.encode()),
        }

        attachment_id = self.env['ir.attachment'].sudo().create(values)
        download_url = '/web/content/' + \
            str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }

    @api.model
    def _get_lines_domain(self, options):
        company_ids = self.env.company.ids
        domain = [('journal_id.type', '=', options.get('journal_type')),
                  ('account_payment_id.withholding_number', '!=', False),
                  ('account_payment_id.tax_withholding_id', '!=', False),
                  ('company_id', 'in', company_ids)]
        state = options.get('all_entries') and 'all' or 'posted'
        if state and state.lower() != 'all':
            domain += [('state', '=', state)]
        if options.get('date').get('date_to'):
            domain += [('date', '<=', options['date']['date_to'])]
        if options.get('date').get('date_from'):
            domain += [('date', '>=', options['date']['date_from'])]
        return domain
