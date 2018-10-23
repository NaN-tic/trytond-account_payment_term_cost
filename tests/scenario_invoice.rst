================
Invoice Scenario
================

Imports::
    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, create_tax_code
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Activate account_payment_term_cost::

    >>> config = activate_modules('account_payment_term_cost')

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
    >>> TaxCode = Model.get('account.tax.code')
    >>> tax = create_tax(Decimal('.10'))
    >>> tax.save()
    >>> invoice_base_code = create_tax_code(tax, 'base', 'invoice')
    >>> invoice_base_code.save()
    >>> invoice_tax_code = create_tax_code(tax, 'tax', 'invoice')
    >>> invoice_tax_code.save()
    >>> credit_note_base_code = create_tax_code(tax, 'base', 'credit')
    >>> credit_note_base_code.save()
    >>> credit_note_tax_code = create_tax_code(tax, 'tax', 'credit')
    >>> credit_note_tax_code.save()

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.save()

Create account category::

    >>> ProductCategory = Model.get('product.category')
    >>> account_category = ProductCategory(name="Account Category")
    >>> account_category.accounting = True
    >>> account_category.account_expense = expense
    >>> account_category.account_revenue = revenue
    >>> account_category.customer_taxes.append(tax)
    >>> account_category.save()

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
    >>> template.account_category = account_category
    >>> template.save()
    >>> product, = template.products
    >>> product.save()

    >>> cost_product = Product()
    >>> cost_template = ProductTemplate()
    >>> cost_template.name = 'cost product'
    >>> cost_template.default_uom = unit
    >>> cost_template.type = 'service'
    >>> cost_template.list_price = Decimal('40')
    >>> cost_template.account_category = account_category
    >>> cost_template.save()
    >>> cost_product, = cost_template.products
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
    >>> len(invoice.lines)
    2
    >>> line1, line2 = invoice.lines
    >>> line1.amount
    Decimal('200.00')
    >>> line2.amount
    Decimal('10.00')
    >>> invoice.untaxed_amount
    Decimal('210.00')
