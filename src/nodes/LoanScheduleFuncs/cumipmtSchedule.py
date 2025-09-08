
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


@knext.node(name="CUMIPMT Schedule",
            node_type=knext.NodeType.MANIPULATOR,
            icon_path="src\icons\CUMIPMTSCHEDULE.png",
            category=loan_schedule_category)
@knext.input_table(name="Input Data", description="Table containing annual rate, nper, and pv values")
@knext.output_table(name="Full Schedule", description="Complete amortization schedule with all payment components")
class AmortizationCUMIPMTScheduleNode:
    """Generates a complete cumulative interest payment schedule for loan amortization analysis.

# CUMIPMT Schedule Node

This node creates a comprehensive amortization schedule showing the cumulative interest paid up to each payment period. Unlike the standard CUMIPMT function that calculates cumulative interest between two specific periods, this schedule node generates a complete table with cumulative interest values for every period from 1 to the final payment.

## Input Requirements

The input table must contain the following loan parameters:

1. **Annual rate column**: Annual interest rate in decimal format (e.g., 0.05 for 5%)
2. **Number of periods column**: Total number of payment periods (integer or decimal)
3. **Present value column**: Principal loan amount or present value (monetary amount)

## Configuration Parameters

**Annual Rate Column**: Select the column containing the annual interest rate in decimal format. This rate will be automatically adjusted based on the selected payment frequency.

**Number of Periods Column**: Select the column containing the total number of payment periods for the complete loan term.

**Present Value Column**: Select the column containing the loan principal amount or present value.

**Payment Frequency**: Choose the frequency of loan payments:
1. **Monthly**: 12 payments per year (most common)
2. **Quarterly**: 4 payments per year  
3. **Annual**: 1 payment per year

**Interest Type**: Select how the periodic interest rate is calculated:
1. **Simple**: Periodic rate = Annual rate ÷ Frequency
2. **Compound**: Periodic rate = (1 + Annual rate)^(1/Frequency) - 1

**Payment Timing**: Configure when payments occur within each period:
- `0` (default): Payments due at end of each period
- `1`: Payments due at beginning of each period

## Output Structure

The node generates a comprehensive schedule with these columns:

**Original Input Columns**: All columns from the input table are preserved

**Period**: Sequential period numbers from 1 to the total number of periods

**Cumulative_Interest_Paid**: Running total of interest payments from period 1 through the current period

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
            knext.Column(knext.double(), "Cumulative_Interest_Paid")
        ])

    def execute(self, exec_context, input_table):
        df = input_table.to_pandas()
        
        input_columns = df.columns.tolist()
        output_columns = input_columns + [
            'Period', 'Cumulative_Interest_Paid'
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
                
                
                # Update cumulative values
                cumulative_interest += abs(ipmt)
                
                
                # Add new columns
                new_row.extend([
                    period,                  # Period      # Remaining_Balance
                    cumulative_interest
                ])
                
                all_data.append(new_row)
        
        # Create DataFrame with explicit column names
        result_df = pd.DataFrame(all_data, columns=output_columns)
        
        # Ensure proper data types
        for col in result_df.columns:
            if col == 'Period':
                result_df[col] = result_df[col].astype(np.int32)
            elif col in ['Cumulative_Interest_Paid']:
                result_df[col] = result_df[col].astype(np.float64) *-1
                
        return knext.Table.from_pandas(result_df)