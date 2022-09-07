# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        for rec in self:
            PurchaseRequest = self.env['purchase.request']
            request_group = PurchaseRequest.read_group([('order_line_id.order_id', '=', rec.id)],
                                                                  ['supplier_id'], ['supplier_id'])
            for pr in request_group:
                request_ids = PurchaseRequest.search(pr['__domain'])
                request_ids.create_purchase_order(pr['supplier_id'][0])
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    request_ids = fields.One2many('purchase.request', 'order_line_id')
    request_total = fields.Monetary(compute='_compute_request_amount', string='Purchase total')
    request_margin = fields.Float(compute='_compute_request_amount', string='Margin request (%)')

    @api.depends('request_ids', 'request_ids.price_subtotal', 'price_subtotal')
    def _compute_request_amount(self):
        for rec in self:
            rec.request_total = sum(rec.request_ids.mapped('price_subtotal'))
            rec.request_margin = (rec.price_subtotal-rec.request_total)/rec.price_subtotal * 100 if rec.price_subtotal \
                else 0

    def open_purchase_request(self):
        self.ensure_one()
        view_id = self.env.ref('aptys_sale_purchase.sale_purchase_request_form').id
        return {
            'res_model': 'sale.order.line',
            'target': 'new',
            'name': _('Add purchase request'),
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'views': [[view_id, 'form']],
        }

    def validate_close(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}