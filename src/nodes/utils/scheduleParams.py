import knime.extension as knext

class FrequencyOptions(knext.EnumParameterOptions):
    ANNUAL = ("Annual", "Payments made once per year")
    QUARTERLY = ("Quarterly", "Payments made four times per year")
    MONTHLY = ("Monthly", "Payments made monthly")

class InterestTypeOptions(knext.EnumParameterOptions):
    SIMPLE = ("Simple Interest", "Interest rate divided by frequency")
    COMPOUND = ("Compound Interest", "Interest rate compounded by frequency")

rate_column = knext.ColumnParameter(
    "Annual Interest Rate Column",
    "Column containing the annual interest rate (as decimal, e.g. 0.05 for 5%)",
    column_filter=lambda col: col.ktype == knext.double()
)

nper_column = knext.ColumnParameter(
    "Number of Periods Column",
    "Column containing the total number of payment periods",
    column_filter=lambda col: col.ktype == knext.double()
)

pv_column = knext.ColumnParameter(
    "Present Value Column",
    "Column containing the present value (loan amount)",
    column_filter=lambda col: col.ktype == knext.double()
)

frequency = knext.EnumParameter(
    "Payment Frequency",
    "How often payments are made",
    FrequencyOptions.MONTHLY.name,
    FrequencyOptions
)

interest_type = knext.EnumParameter(
    "Interest Calculation Method",
    "Method used to calculate periodic interest rate",
    InterestTypeOptions.COMPOUND.name,
    InterestTypeOptions
)

pmt_type = knext.BoolParameter(
    "Payment Timing",
    "When payments are due (0: end of period, 1: beginning of period)",
    False
)