# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductPricelistInh(models.Model):
    _inherit = "product.pricelist.item"

    @api.constrains('product_id')
    def remove_duplication_variant(self):
        if self.product_id and self.pricelist_id:
            record = self.env['product.pricelist.item'].search([('product_id', '=', self.product_id.id), ('pricelist_id', '=', self.pricelist_id.id)])
            if len(record) > 1:
                raise UserError('This Product Already Exists in this Pricelist.')


class ProductTemplateInh(models.Model):
    _inherit = "product.template"

    @api.model
    def default_get(self, fields_list):
        res = super(ProductTemplateInh, self).default_get(fields_list)
        res.update({'list_price': 1000})
        return res


class ProductProductInh(models.Model):
    _inherit = "product.product"

    def create(self, vals_list):
        record = super(ProductProductInh, self).create(vals_list)
        pricelist = self.env['product.pricelist'].search([('id', '=', 1)])
        if pricelist:
            for rec in record:
                self.env['product.pricelist.item'].create({
                    'product_tmpl_id': rec.product_tmpl_id.id,
                    'product_id': rec.id,
                    'compute_price': 'fixed',
                    'applied_on': '0_product_variant',
                    'fixed_price': 1000,
                    'pricelist_id': pricelist.id
                })
        return record