# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PuchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase request"

    order_line_id = fields.Many2one('sale.order.line', ondelete="cascade", required=True)
    purchase_line_id = fields.Many2one('purchase.order.line')
    supplier_id = fields.Many2one('res.partner', string='Supplier', required=True)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Float('Quantity', default=1.0)
    price_unit = fields.Float('Price unit')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    currency_id = fields.Many2one('res.currency', related='order_line_id.currency_id')

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for rec in self:
            rec.price_subtotal = rec.quantity * rec.price_unit

    def create_purchase_order(self, supplier_id):
        purchase_id = self.env['purchase.order'].create({'partner_id': supplier_id})
        purchase_id.onchange_partner_id()
        for rec in self:
            pol = self.env['purchase.order.line'].new({
                'product_id': rec.product_id.id,
                'sale_line_id': rec.order_line_id.id,
                'order_id': purchase_id.id
            })
            pol.onchange_product_id()
            pol_vals = pol._convert_to_write(pol._cache)
            pol_vals.update({
                'product_qty': rec.quantity,
                'price_unit': rec.price_unit,
            })
            pol_id = self.env['purchase.order.line'].create(pol_vals)
            rec.purchase_line_id = pol_id
        return purchase_id
