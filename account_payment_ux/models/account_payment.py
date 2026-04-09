from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    # PARCHE ODOO 19: Campos faltantes requeridos por vistas de bundles de ADHOC
    counterpart_currency_id = fields.Many2one('res.currency', string='Counterpart Currency')
    bundle_counterpart_currency_amount = fields.Monetary(string='Bundle Counterpart Amount', currency_field='counterpart_currency_id')
    duplicate_payment_ids = fields.Many2many('account.payment', string='Duplicated Payments', compute='_compute_duplicate_payment_ids')
    l10n_latam_check_warning_msg = fields.Char(string='Check Warning Message')
    counterpart_exchange_rate = fields.Float(string='Counterpart Exchange Rate', digits=(12, 6))
    payment_difference = fields.Monetary(string='Payment Difference', compute='_compute_payment_difference')

    def _compute_payment_difference(self):
        for rec in self:
            rec.payment_difference = 0.0

    def _compute_duplicate_payment_ids(self):
        for rec in self:
            rec.duplicate_payment_ids = False


    def action_post(self):
        """Odoo a partir de 16, cuando se valida un pago con token, si la transaccion no queda en done cancela el pago
        por ahora nosotros revertimos este cambio"""
        return super(AccountPayment, self.with_context(from_action_post=True)).action_post()

    def action_cancel(self):
        if self.env.context.get("from_action_post"):
            self = self - self.filtered(lambda x: x.payment_transaction_id.state in ["draft", "pending", "authorized"])
        return super(AccountPayment, self).action_cancel()
