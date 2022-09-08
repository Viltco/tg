# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    default_location_src_id = fields.Many2one(
        "stock.location", related="picking_type_id.default_location_src_id"
    )
    use_expiration = fields.Boolean(string="Expiration", compute="_compute_expiration_date")

    def _compute_expiration_date(self):
        for record in self:
            module_product_expiry = self.env.ref('base.module_product_expiry')
            if module_product_expiry and module_product_expiry.state == 'installed':
                self.use_expiration = True
            else:
                self.use_expiration = False
