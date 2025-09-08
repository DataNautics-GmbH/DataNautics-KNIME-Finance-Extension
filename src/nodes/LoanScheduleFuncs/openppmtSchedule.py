
import knime.extension as knext
import pandas as pd
import numpy as np
import numpy_financial as npf
import logging
from nodes.utils.category import loan_schedule_category
from nodes.utils.scheduleParams import rate_column, nper_column, pv_column, frequency, interest_type, pmt_type, FrequencyOptions, InterestTypeOptions

LOGGER = logging.getLogger(__name__)

schedule_category = knext.category(
    path="/community/financial_functions",
    level_id="schedule_functions",
    name="Amortization Schedule Functions", 
    description="Financial functions that output full amortization schedules",
    icon="icons/icon.png"
)


@knext.node(name="Open PPMT Balance Schedule",
            node_type=knext.NodeType.MANIPULATOR,
            icon_path="src\icons\PPMTSCHEDULEFUTURE.png",
            category=loan_schedule_category)
@knext.input_table(name="Input Data", description="Table containing annual rate, nper, and pv values")
@knext.output_table(name="Full Schedule", description="Complete amortization schedule with all payment components")
class AmortizationOutstandingPrincipalScheduleNode:
    """Generates a comprehensive amortization schedule with detailed payment breakdowns and outstanding balance tracking.

# Open PPMT Balance Schedule Node

This node creates a complete amortization schedule that provides detailed breakdowns of each payment component along with comprehensive tracking of cumulative amounts and outstanding balances. This schedule combines payment details with forward-looking balance information, making it ideal for comprehensive loan analysis and planning.

## Input Requirements

The input table must contain the following loan parameters:

1. **Annual rate column**: Annual interest rate in decimal format (e.g., 0.05 for 5%)
2. **Number of periods column**: Total number of payment periods (integer or decimal)
3. **Present value column**: Principal loan amount or present value (monetary amount)

## Configuration Parameters

**Annual Rate Column**: Select the column containing the annual interest rate in decimal format. This rate will be automatically converted to the appropriate periodic rate based on the selected payment frequency.

**Number of Periods Column**: Select the column containing the total number of payment periods for the complete loan term.

**Present Value Column**: Select the column containing the loan principal amount or present value.

**Payment Frequency**: Choose the frequency of loan payments. Monthly payments occur 12 times per year and are most common for mortgages and personal loans. Quarterly payments occur 4 times per year and are common for business loans. Annual payments occur once per year and are typical for some commercial loans.

**Interest Type**: Select the method for calculating periodic interest rates. Simple interest uses the formula: Periodic rate = Annual rate ÷ Payment frequency. Compound interest uses the formula: Periodic rate = (1 + Annual rate)^(1/Payment frequency) - 1.

**Payment Timing**: Configure when payments are due within each period. Set to `0` for payments due at end of each period (ordinary annuity), which is the default. Set to `1` for payments due at beginning of each period (annuity due).

## Output Structure

The node generates a comprehensive amortization schedule with these columns:

**Original Input Columns**: All columns from the input table are preserved for reference

**Period**: Sequential period numbers from 1 to the total number of payment periods

**PMT**: Fixed payment amount for each period (principal + interest)

**IPMT**: Interest payment portion for each period

**PPMT**: Principal payment portion for each period

**Remaining_Balance**: Outstanding loan balance after each payment

**Cumulative_Interest_Paid**: Running total of interest payments made from period 1 through current period

**Cumulative_Principal_Paid**: Running total of principal payments made from period 1 through current period

**Outstanding_Interest**: Total interest remaining to be paid after current period

**Outstanding_Principal**: Remaining principal balance still owed after current period
"""
    
            # node config params
    FrequencyOptions = FrequencyOptions

    InterestTypeOptions = InterestTypeOptions
    
    rate_column = rate_column
    
    nper_column = nper_column
    
    pv_column = pv_column
    
    frequency = frequency
    
    interest_type = interest_type
    
    pmt_type = pmt_type

    def configure(self, configure_context, input_schema):
        return input_schema.append([
            knext.Column(knext.int32(), "Period"),
            knext.Column(knext.double(), "PMT"),
            knext.Column(knext.double(), "IPMT"),
            knext.Column(knext.double(), "PPMT"),
            knext.Column(knext.double(), "Remaining_Balance"),
            knext.Column(knext.double(), "Cumulative_Interest_Paid"),
            knext.Column(knext.double(), "Cumulative_Principal_Paid"),
            knext.Column(knext.double(), "Outstanding_Interest"),
            knext.Column(knext.double(), "Outstanding_Principal")
        ])

    def execute(self, exec_context, input_table):
        df = input_table.to_pandas()
        
        input_columns = df.columns.tolist()
        output_columns = input_columns + [
            'Period', 'PMT', 'IPMT', 'PPMT', 'Remaining_Balance',
            'Cumulative_Interest_Paid', 'Cumulative_Principal_Paid',
            'Outstanding_Interest', 'Outstanding_Principal'
        ]
        
        # Pre-allocate a list to store all our data
        all_data = []
        
        # Frequency multiplier for interest rate adjustment
        frequency_multiplier = {
            self.FrequencyOptions.ANNUAL.name: 1,
            self.FrequencyOptions.QUARTERLY.name: 4,
            self.FrequencyOptions.MONTHLY.name: 12
        }[self.frequency]
        
        for _, row in df.iterrows():
            # Extract and convert core calculation values
            nper = int(row[self.nper_column])
            pv = float(row[self.pv_column])
            annual_rate = float(row[self.rate_column])
            
            # Calculate periodic rate based on frequency and interest type
            if self.interest_type == self.InterestTypeOptions.SIMPLE.name:
                # Simple division for periodic rate
                periodic_rate = annual_rate / frequency_multiplier
            else:
                # Compound interest formula for effective periodic rate
                periodic_rate = (1 + annual_rate) ** (1/frequency_multiplier) - 1
            
            # Calculate constant PMT value for this loan
            pmt = float(npf.pmt(rate=periodic_rate, nper=nper, pv=pv, when=self.pmt_type))
            
            # Initialize tracking variables
            remaining_balance = pv
            cumulative_interest = 0
            cumulative_principal = 0
            
            # Calculate total interest over loan life for outstanding interest tracking
            total_interest = abs(pmt) * nper - pv
            
            # Generate rows for each period
            for period in range(1, nper + 1):
                # Start with original row values
                new_row = []
                for col in input_columns:
                    val = row[col]
                    if isinstance(val, (np.integer, np.floating)):
                        val = val.item()
                    new_row.append(val)
                
                # Calculate period-specific values
                ipmt = float(npf.ipmt(rate=periodic_rate, per=period, nper=nper, pv=pv, when=self.pmt_type))
                ppmt = float(npf.ppmt(rate=periodic_rate, per=period, nper=nper, pv=pv, when=self.pmt_type))
                
                # Update cumulative values
                cumulative_interest += abs(ipmt)
                cumulative_principal += abs(ppmt)
                
                # Calculate outstanding values
                outstanding_interest = total_interest - cumulative_interest
                outstanding_principal = remaining_balance - ppmt
                
                # Update remaining balance
                remaining_balance = float(remaining_balance + ppmt)
                
                # Add new columns
                new_row.extend([
                    period,                  # Period
                    pmt,                     # PMT
                    ipmt,                    # IPMT
                    ppmt,                    # PPMT
                    remaining_balance,       # Remaining_Balance
                    cumulative_interest,     # Cumulative_Interest_Paid
                    cumulative_principal,    # Cumulative_Principal_Paid
                    outstanding_interest,    # Outstanding_Interest
                    outstanding_principal    # Outstanding_Principal
                ])
                
                all_data.append(new_row)
        
        # Create DataFrame with explicit column names
        result_df = pd.DataFrame(all_data, columns=output_columns)
        
        # Ensure proper data types
        for col in result_df.columns:
            if col == 'Period':
                result_df[col] = result_df[col].astype(np.int32)
            elif col in ['PMT', 'IPMT', 'PPMT', 'Remaining_Balance',
                        'Cumulative_Interest_Paid', 'Cumulative_Principal_Paid',
                        'Outstanding_Interest', 'Outstanding_Principal']:
                result_df[col] = result_df[col].astype(np.float64)
                
        return knext.Table.from_pandas(result_df)