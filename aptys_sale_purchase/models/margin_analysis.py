# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class MarginAnalysis(models.Model):
    _name = "margin.analysis"
    _description = "Margin analysis"

    order_line_id = fields.Many2one('sale.order.line', ondelete="cascade", required=True)
    order_id = fields.Many2one('sale.order', related='order_line_id.order_id')
    purchase_line_id = fields.Many2one('purchase.order.line')
    supplier_id = fields.Many2one('res.partner', string='Supplier', required=False)
    product_id = fields.Many2one('product.product', 'Product', required=False)
    quantity = fields.Float('Quantity', default=1.0)
    price_unit = fields.Float('Price unit')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    currency_id = fields.Many2one('res.currency', related='order_line_id.currency_id')
    to_purchase = fields.Boolean('Purchase')
    description = fields.Text('Description')

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for rec in self:
            rec.price_subtotal = rec.quantity * rec.price_unit

    def create_purchase_order(self, supplier_id):
        purchase_id = self.env['purchase.order'].search([('partner_id', '=', supplier_id), ('state', '=', 'draft')],
                                                        limit=1)
        if not purchase_id:
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

    def action_generate_purchase_order(self):
        margin_group = self.read_group([('id', 'in', self.ids)], ['supplier_id'], ['supplier_id'])
        for pr in margin_group:
            request_ids = self.search(pr['__domain'])
            request_ids.create_purchase_order(pr['supplier_id'][0])
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _("Purchase orders have been generated"),
                'sticky': False,
            },
            'next': {'type': 'ir.actions.act_window_close'}
        }

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.ensure_one()
        self.description = self.product_id.display_name
