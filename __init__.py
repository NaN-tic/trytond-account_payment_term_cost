# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import invoice
from . import payment_term

def register():
    Pool.register(
        invoice.Invoice,
        payment_term.PaymentTerm,
        module='account_payment_term_cost', type_='model')
