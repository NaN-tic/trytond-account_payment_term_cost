# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .invoice import *
from .payment_term import *

def register():
    Pool.register(
        Invoice,
        PaymentTerm,
        module='account_payment_term_cost', type_='model')
