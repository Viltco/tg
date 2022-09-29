# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockValuationInh(models.Model):
    _inherit = 'stock.valuation.layer'

    barcode = fields.Char('Barcode', related='product_id.barcode')

class StockQuantInh(models.Model):
    _inherit = 'stock.quant'

    barcode = fields.Char('Barcode', related='product_id.barcode')


class StockMoveLineInh(models.Model):
    _inherit = 'stock.move.line'

    barcode = fields.Char('Barcode', related='product_id.barcode')


class StockMoveInh(models.Model):
    _inherit = 'stock.move'

    barcode = fields.Char('Barcode', related='product_id.barcode')


class PricelistInh(models.Model):
    _inherit = 'product.pricelist.item'

    barcode = fields.Char('Barcode', related='product_id.barcode')
