odoo.define('pos_lot_selection_knk.models', function(require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;

    models.load_fields("product.product", ["qty_available", "packaging_ids"]);
    models.load_models({
        model: 'stock.production.lot',
        fields: ['id', 'name', 'display_name', 'company_id', 'product_id', 'product_qty'],
        domain: function(self) {
            return [
                ['company_id', '=', self.company && self.company.id]
            ];
        },
        loaded: function(self, production_lots) {
            self.production_lots = production_lots;
        },
    });
    var order_super = models.Order.prototype;
    models.Order = models.Order.extend({
        // A series of overwrites for pushing the order to the backend whenever
        // a change is made.
        // An order is only pushed once there's been at least one change to
        // prevent empty orders, e.g. when an order is finished,
        // to clog up transactions.

        // The function is specifically only called for these changes, instead
        // of a general trigger-Overwrite to prevent saves for paymentlines:
        // Example: price is 50€, only typing in 60€ will save and prevent
        // further changes since the order is already set to 'paid' even if
        // this input was in error or not final.
        add_product: function(product, options) {
            var res = order_super.add_product.apply(this, arguments);
            var self = this;
            if (options.draftPackLotLines) {
                self.selected_orderline.setPackLotLines(options.draftPackLotLines);
                var qties = 1;
                if(product.tracking != 'serial'){
                    if (options.draftPackLotLines.newPackLotLines){
                        var qties = options.draftPackLotLines.newPackLotLines.map(function(line){
                            return line.qty
                        });
                        if(qties.length > 0){
                            qties.reduce(function(a, b){return a + b});
                        }
                    }
                    self.selected_orderline.set_quantity(qties)
                }
            }
            return res
        },
    });
});