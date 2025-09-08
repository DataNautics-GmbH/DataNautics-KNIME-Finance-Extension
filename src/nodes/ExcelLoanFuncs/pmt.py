import knime.extension as knext
import numpy as np
import numpy_financial as npf
from nodes.utils.category import loan_functions_category


@knext.node(name="PMT", 
            node_type=knext.NodeType.MANIPULATOR,
            icon_path="src\icons\PMT.png",
            category=loan_functions_category)
@knext.input_table(name="Input Data", description="Table containing rate, nper, and pv values")
@knext.output_table(name="PMT Results", description="Table with calculated PMT values")
class PMTNode:
    """Calculates the periodic payment required to amortize a loan with constant payments and a constant interest rate.
    
    # PMT Node
    
    This node implements Excel's **PMT** function to calculate the fixed payment amount required to fully amortize a loan over a specified number of periods at a constant interest rate.
    
    ## Input Requirements
    
    The input table must contain three essential columns for the calculation:
    
    1. **Rate column**: Interest rate per period (decimal format, e.g., 0.05 for 5%)
    2. **Number of periods column**: Total number of payment periods (integer or decimal)
    3. **Present value column**: Principal loan amount or present value (monetary amount)
    
    ## Configuration Parameters
    
    **Rate Column**: Select the column containing the interest rate per period. This should be in decimal format (e.g., 0.05 for 5% annual rate).
    
    **Number of Periods Column**: Select the column containing the total number of payment periods. This can be integer or decimal values.
    
    **Present Value Column**: Select the column containing the present value or principal loan amount. This can be integer or decimal monetary values.
    
    **Payment Timing**: Configure when payments are due within each period. Set to `0` for payments at the end of each period (default), or `1` for payments at the beginning of each period.
    
    ## Output
    
    The node appends a new **PMT** column to the input table containing the calculated periodic payment amount for each row. Negative values indicate outgoing payments (typical for loan payments from the borrower's perspective).
    
   
    """

    
    # Parameters
    rate_column = knext.ColumnParameter(
        "Rate Column",
        "Column containing the interest rate per period",
        column_filter=lambda col: col.ktype == knext.double() or col.ktype == knext.int64() or col.ktype == knext.int32()
    )
    
    nper_column = knext.ColumnParameter(
        "Number of Periods Column",
        "Column containing the total number of payment periods",
        column_filter=lambda col: col.ktype == knext.double() or col.ktype == knext.int64() or col.ktype == knext.int32()
    )
    
    pv_column = knext.ColumnParameter(
        "Present Value Column",
        "Column containing the present value (loan amount)",
        column_filter=lambda col: col.ktype == knext.double() or col.ktype == knext.int64() or col.ktype == knext.int32()
    )
    
    pmt_type = knext.BoolParameter(
        "Payment Timing",
        "When payments are due (0: end of period, 1: beginning of period)",
        False
    )

    def configure(self, configure_context, input_schema):
        # Check if PMT column already exists and remove it if it does
        output_schema = input_schema
        if "PMT" in input_schema.column_names:
            output_schema = input_schema.remove("PMT")
        return output_schema.append(knext.Column(knext.double(), "PMT"))

    def execute(self, exec_context, input_table):
        df = input_table.to_pandas()
        
        # Remove PMT column if it already exists
        if "PMT" in df.columns:
            df = df.drop(columns=["PMT"])
        
        df["PMT"] = npf.pmt(
            rate=df[self.rate_column],
            nper=df[self.nper_column],
            pv=df[self.pv_column],
            when=self.pmt_type
        )
        
        return knext.Table.from_pandas(df)