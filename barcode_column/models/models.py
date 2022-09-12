# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMoveInh(models.Model):
    _inherit = 'stock.move'

    barcode = fields.Char('Barcode', related='product_id.barcode')


class PricelistInh(models.Model):
    _inherit = 'product.pricelist.item'

    barcode = fields.Char('Barcode', related='product_id.barcode')
