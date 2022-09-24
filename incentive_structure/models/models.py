# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

from odoo.exceptions import UserError, AccessError


class AccountMoveIn(models.Model):
    _inherit = 'account.move'

    order_id = fields.Many2one('pos.order')

class HrEmployeeIn(models.Model):
    _inherit = 'hr.employee'

    def action_view_incentive(self):
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('partner_id', '=', self.user_id.partner_id.id)],
            'target': 'current',
            'name': 'Journal Items',
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
        }


class StockLotIn(models.Model):
    _inherit = 'stock.production.lot'

    incentive = fields.Float()


class PosOrderLineIn(models.Model):
    _inherit = 'pos.order.line'

    incentive = fields.Float()


class PosOrderIn(models.Model):
    _inherit = 'pos.order'

    incentive = fields.Float()
    incentive_lines = fields.One2many('incentive.lines', 'order_id')

    def action_pos_order_paid(self):
        self.action_add()
        return super(PosOrderIn, self).action_pos_order_paid()

    def action_view_entry(self):
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('order_id', '=', self.id)],
            'target': 'current',
            'name': 'Journal Entry',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
        }

    def general_entry(self):
        print(self.incentive_lines)
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        journal = self.env['account.journal'].search([('name', '=', 'Miscellaneous Operations')])
        move_dict = {
            'ref': self.session_id.name,
            'order_id': self.id,
            'journal_id': journal.id,
            # 'partner_id': self.partner_id.id,
            'date': datetime.today(),
            'move_type': 'entry',
            # 'state': 'draft',
        }

        credit_account = self.env['account.account'].search([('name', '=', 'Payables')])
        if not credit_account:
            raise UserError('Credit Account Not Found')
        debit_account = self.env['account.account'].search([('name', '=', 'Incentives')])
        if not debit_account:
            raise UserError('Debit Account Not Found')
        debit_line = (0, 0, {
            'date': datetime.today(),
            'name': self.name,
            'debit': abs(self.incentive_lines[0].total_incentive),
            'credit': 0.0,
            'account_id': debit_account.id,
            'analytic_account_id': self.analytical_account_id.id,
        })
        line_ids.append(debit_line)
        debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
    # if oline.product_id.categ_id.property_account_expense_categ_id.id == oline.account_id.id:
        credit_line = (0, 0, {
            'date': datetime.today(),
            'name': self.name,
            'debit': 0.0,
            'partner_id': self.employee_id.user_id.partner_id.id,
            'credit': abs(self.incentive_lines[0].total_incentive),
            'account_id': credit_account.id,
            'analytic_account_id': self.analytical_account_id.id,
        })
        line_ids.append(credit_line)
        credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        move.action_post()
        print("General entry created")

    def action_add(self):
        total = 0
        for line in self.lines:
            for tax in line.pack_lot_ids:
                lot = self.env['stock.production.lot'].search([('name', '=', tax.lot_name), ('product_id', '=', line.product_id.id)])
                if lot.incentive > 0:
                    total = total + (line.qty * lot.incentive)
                    line.incentive = line.qty * lot.incentive
        if total > 0:
            val = []
            credit_line = (0, 0, {'total_incentive': total, 'employee_id': self.employee_id.id,})
            val.append(credit_line)
            self.incentive_lines = val


class IncentiveLinesInh(models.Model):
    _name = 'incentive.lines'

    total_incentive = fields.Float()
    order_id = fields.Many2one('pos.order')
    employee_id = fields.Many2one('hr.employee')
