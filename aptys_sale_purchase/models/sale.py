# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    budget_count = fields.Integer(compute='_compute_budget_count')
    total_cost = fields.Monetary(compute='_compute_cost')
    margin_cost = fields.Float(compute='_compute_cost')

    @api.depends('order_line')
    def _compute_budget_count(self):
        for rec in self:
            rec.budget_count = self.env['margin.analysis'].search_count([('order_line_id', 'in', rec.order_line.ids)])

    def generate_purchase_budget(self):
        for rec in self:
            MarginAnalysis = self.env['margin.analysis']
            margin_group = MarginAnalysis.read_group([('order_line_id.order_id', '=', rec.id), ('to_purchase', '=',
                                                                                                True),
                                                      ('purchase_line_id', '=', False)],
                                                                  ['supplier_id'], ['supplier_id'])
            for pr in margin_group:
                request_ids = MarginAnalysis.search(pr['__domain'])
                request_ids.create_purchase_order(pr['supplier_id'][0])

    @api.depends('order_line', 'order_line.request_total', 'amount_total')
    def _compute_cost(self):
        for rec in self:
            rec.total_cost = sum(rec.order_line.mapped('request_total'))
            rec.margin_cost = ((rec.amount_total - rec.total_cost) / rec.amount_total)*100 if rec.amount_total else 0.0


    def action_view_budget(self):
        self.ensure_one()
        return {
            'res_model': 'margin.analysis',
            'type': 'ir.actions.act_window',
            'name': _("Budget"),
            'domain': [('id', 'in', self.order_line.request_ids.ids)],
            'view_mode': 'tree,form',
            'context': {
                'search_default_groupby_order_line_id': True,
            },
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    request_ids = fields.One2many('margin.analysis', 'order_line_id')
    request_total = fields.Monetary(compute='_compute_request_amount', string='Purchase total')
    request_margin = fields.Float(compute='_compute_request_amount', string='Margin request (%)')

    @api.depends('request_ids', 'request_ids.price_subtotal', 'price_subtotal')
    def _compute_request_amount(self):
        for rec in self:
            rec.request_total = sum(rec.request_ids.mapped('price_subtotal'))
            rec.request_margin = (rec.price_subtotal-rec.request_total)/rec.price_subtotal * 100 if rec.price_subtotal \
                else 0

    def open_margin_analysis(self):
        self.ensure_one()
        view_id = self.env.ref('aptys_sale_purchase.sale_margin_analysis_form').id
        return {
            'res_model': 'sale.order.line',
            'target': 'new',
            'name': _('Add purchase request'),
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'views': [[view_id, 'form']],
            'context': {'default_to_purchase': self.product_id.type != 'service'}
        }

    def validate_close(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}