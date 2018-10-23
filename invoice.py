# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta

__all__ = ['Invoice']


class Invoice(metaclass=PoolMeta):
    'Invoice'
    __name__ = 'account.invoice'

    def get_move(self):
        pool = Pool()
        Line = pool.get('account.invoice.line')
        if self.payment_term and self.payment_term.has_cost:
            lines = Line.search([
                    ('invoice', '=', self),
                    ('product', '=', self.payment_term.cost_product),
                    ])

            if not lines:
                line = self._get_payment_term_cost_line()
                line.save()
                # Taxes must be recomputed before creating the move
                self.update_taxes([self])
        return super(Invoice, self).get_move()

    def _get_payment_term_cost_line(self):
        "Returns invoice line with the cost of the payment term"
        Line = Pool().get('account.invoice.line')

        if not self.payment_term or not self.payment_term.has_cost:
            return

        line = Line()
        line.invoice = self
        for key, value in Line.default_get(Line._fields.keys(),
                with_rec_name=False).items():
            setattr(line, key, value)
        line.quantity = 1
        line.unit = None
        line.description = None
        line.product = self.payment_term.cost_product
        line.on_change_product()
        if self.payment_term.compute_over_total_amount:
            line.unit_price = (self.total_amount *
                self.payment_term.cost_percent)
        else:
            line.unit_price = (self.untaxed_amount *
                self.payment_term.cost_percent)
        return line
