# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class PosPaymentInh(models.Model):
    _inherit = 'pos.payment'

    analytical_account_id = fields.Many2one('account.analytic.account')


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    analytical_account_id = fields.Many2one('account.analytic.account')


class PosSessionInh(models.Model):
    _inherit = 'pos.session'

    def action_assign_account(self):
        for res in self:
            if res.config_id.analytical_account_id:
                all_related_moves = res._get_related_account_moves()
                for rec in all_related_moves.line_ids:
                    rec.analytic_account_id = res.config_id.analytical_account_id.id

                for order in res.order_ids:
                    order.analytical_account_id = res.config_id.analytical_account_id.id
                pos_payment = self.env['pos.payment'].search([('session_id', '=', res.id)])
                for i in pos_payment:
                    i.analytical_account_id = res.config_id.analytical_account_id.id
                for payment in res.bank_payment_ids:
                    payment.analytical_account_id = res.config_id.analytical_account_id.id
                moves = self.env['account.move.line'].search([('move_id.order_id', 'in', res.order_ids.ids)])
                for move in moves:
                    move.analytic_account_id = res.config_id.analytical_account_id.id

    def action_update_account(self):
        all_related_moves = self._get_related_account_moves()
        for rec in all_related_moves.line_ids:
            rec.analytic_account_id = self.config_id.analytical_account_id.id

        for order in self.order_ids:
            order.analytical_account_id = self.config_id.analytical_account_id.id
        pos_payment = self.env['pos.payment'].search([('session_id', '=', self.id)])
        for i in pos_payment:
            i.analytical_account_id = self.config_id.analytical_account_id.id
        for payment in self.bank_payment_ids:
            payment.analytical_account_id = self.config_id.analytical_account_id.id
            # for i in payment.pos_payment_ids:
            #     i.analytical_account_id = self.config_id.analytical_account_id.id
        moves = self.env['account.move.line'].search([('move_id.order_id', 'in', self.order_ids.ids)])
        for move in moves:
            move.analytic_account_id = self.config_id.analytical_account_id.id

    def _validate_session(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        bank_payment_method_diffs = bank_payment_method_diffs or {}
        self.ensure_one()
        sudo = self.user_has_groups('point_of_sale.group_pos_user')
        if self.order_ids or self.statement_ids.line_ids:
            self.cash_real_transaction = self.cash_register_total_entry_encoding
            self.cash_real_expected = self.cash_register_balance_end
            self.cash_real_difference = self.cash_register_difference
            if self.state == 'closed':
                raise UserError(_('This session is already closed.'))
            self._check_if_no_draft_orders()
            self._check_invoices_are_posted()
            if self.update_stock_at_closing:
                self._create_picking_at_end_of_session()
                self.order_ids.filtered(lambda o: not o.is_total_cost_computed)._compute_total_cost_at_session_closing(
                    self.picking_ids.move_lines)
            try:
                data = self.with_company(self.company_id)._create_account_move(balancing_account, amount_to_balance,
                                                                               bank_payment_method_diffs)
            except AccessError as e:
                if sudo:
                    data = self.sudo().with_company(self.company_id)._create_account_move(balancing_account,
                                                                                          amount_to_balance,
                                                                                          bank_payment_method_diffs)
                else:
                    raise e

            try:
                balance = sum(self.move_id.line_ids.mapped('balance'))
                self.move_id._check_balanced()
            except UserError:
                # Creating the account move is just part of a big database transaction
                # when closing a session. There are other database changes that will happen
                # before attempting to create the account move, such as, creating the picking
                # records.
                # We don't, however, want them to be committed when the account move creation
                # failed; therefore, we need to roll back this transaction before showing the
                # close session wizard.
                self.env.cr.rollback()
                return self._close_session_action(balance)

            if self.move_id.line_ids:
                self.move_id.sudo().with_company(self.company_id)._post()
                # Set the uninvoiced orders' state to 'done'
                orders = self.env['pos.order'].search([('session_id', '=', self.id), ('state', '=', 'paid'), ('state', '=', 'paid')])
                print(orders)
                for order in orders:
                    if order.incentive_lines:
                        order.general_entry()
                self.env['pos.order'].search([('session_id', '=', self.id), ('state', '=', 'paid')]).write(
                    {'state': 'done'})
            else:
                self.move_id.sudo().unlink()
            self.sudo().with_company(self.company_id)._reconcile_account_move_lines(data)
        else:
            statement = self.cash_register_id
            if not self.config_id.cash_control:
                statement.write({'balance_end_real': statement.balance_end})
            statement.button_post()
            statement.button_validate()
        self.write({'state': 'closed'})
        self.action_update_account()
        return True


class PosOrderInh(models.Model):
    _inherit = 'pos.order'

    analytical_account_id = fields.Many2one('account.analytic.account')

    # def action_pos_order_invoice(self):
    #     rec = super(PosOrderInh, self).action_pos_order_invoice()
    #     print('hello')
    #     for line in self.seesion_move_id:
    #         line.analytical_account_id = self.analytical_account_id.id
    #     return rec


class PosConfigInh(models.Model):
    _inherit = 'pos.config'

    analytical_account_id = fields.Many2one('account.analytic.account')
