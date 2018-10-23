# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields
from trytond.pyson import Eval, Not
from trytond.pool import PoolMeta

__all__ = ['PaymentTerm']


class PaymentTerm(metaclass=PoolMeta):
    __name__ = 'account.invoice.payment_term'

    has_cost = fields.Boolean('Has Costs?', help="Check it if it has to "
        "create a line with the operation cost in the customer invoices.")
    cost_product = fields.Many2One('product.product', 'Cost product', states={
            'required': Eval('has_cost', False),
            'invisible': Not(Eval('has_cost', False)),
            }, depends=['has_cost'])
    cost_percent = fields.Numeric('Cost (%)', digits=(8, 4), states={
            'required': Eval('has_cost', False),
            'invisible': Not(Eval('has_cost', False)),
            }, depends=['has_cost'])
    compute_over_total_amount = fields.Boolean('Compute over total amount',
        help='Check it if you want to compute cost over total amount with tax,'
        ' otherwise will compute it over total amount without tax', states={
            'invisible': Not(Eval('has_cost', False)),
            }, depends=['has_cost'])
