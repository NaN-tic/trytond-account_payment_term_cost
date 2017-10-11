================
Invoice Scenario
================

Imports::
    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, set_tax_code
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install account_payment_term_cost::

    >>> Module = Model.get('ir.module')
    >>> account_invoice_module, = Module.find(
    ...     [('name', '=', 'account_payment_term_cost')])
    >>> Module.install([account_invoice_module.id], config.context)
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()
    >>> party = company.party

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> payable = accounts['payable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> account_tax = accounts['tax']
    >>> account_cash = accounts['cash']

Create tax::

    >>> Tax = Model.get('account.tax')
    >>> tax = set_tax_code(create_tax(Decimal('.10')))
    >>> tax.save()
    >>> invoice_base_code = tax.invoice_base_code
    >>> invoice_tax_code = tax.invoice_tax_code
    >>> credit_note_base_code = tax.credit_note_base_code
    >>> credit_note_tax_code = tax.credit_note_tax_code

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.list_price = Decimal('40')
    >>> template.cost_price = Decimal('25')
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.customer_taxes.append(tax)
    >>> template.save()
    >>> product.template = template
    >>> product.save()
    >>> cost_product = Product()
    >>> cost_template = ProductTemplate()
    >>> cost_template.name = 'cost product'
    >>> cost_template.default_uom = unit
    >>> cost_template.type = 'service'
    >>> cost_template.list_price = Decimal('40')
    >>> cost_template.cost_price = Decimal('25')
    >>> cost_template.account_expense = expense
    >>> cost_template.account_revenue = revenue
    >>> tax,  = Tax.find([], limit=1)
    >>> cost_template.customer_taxes.append(tax)
    >>> cost_template.save()
    >>> cost_product.template = cost_template
    >>> cost_product.save()

Create payment term::

    >>> PaymentTerm = Model.get('account.invoice.payment_term')

    >>> payment_term = PaymentTerm(name='Term Without Cost')
    >>> payment_term_line = payment_term.lines.new()
    >>> payment_term_line.type = 'remainder'
    >>> delta_days = payment_term_line.relativedeltas.new()
    >>> delta_days.days = 30
    >>> payment_term.save()

    >>> payment_term_cost = PaymentTerm(name='Term With Cost')
    >>> payment_term_cost.has_cost = True
    >>> payment_term_cost.cost_product = cost_product
    >>> payment_term_cost.cost_percent = Decimal('0.05')
    >>> payment_term_cost_line = payment_term_cost.lines.new()
    >>> payment_term_cost_line.type = 'remainder'
    >>> delta_days = payment_term_cost_line.relativedeltas.new()
    >>> delta_days.days = 30
    >>> payment_term_cost.save()

Create invoice without cost::

    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> line = InvoiceLine()
    >>> invoice.lines.append(line)
    >>> line.product = product
    >>> line.quantity = 5
    >>> line.unit_price = Decimal('40')
    >>> invoice.click('post')
    >>> len(invoice.lines)
    1
    >>> invoice.untaxed_amount
    Decimal('200.00')

Create invoice with cost::

    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term_cost
    >>> line = InvoiceLine()
    >>> invoice.lines.append(line)
    >>> line.product = product
    >>> line.quantity = 5
    >>> line.unit_price = Decimal('40')
    >>> invoice.click('post')
    >>> invoice.state
    u'posted'
    >>> len(invoice.lines) == 2
    True
    >>> line1, line2 = invoice.lines
    >>> line1.amount
    Decimal('200.00')
    >>> line2.amount
    Decimal('10.00')
    >>> invoice.untaxed_amount
    Decimal('210.00')
