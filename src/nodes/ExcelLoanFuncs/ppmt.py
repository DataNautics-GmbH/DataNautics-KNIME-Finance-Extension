import knime.extension as knext
import numpy as np
import numpy_financial as npf
from nodes.utils.category import loan_functions_category


@knext.node(name="PPMT",
            node_type=knext.NodeType.MANIPULATOR,
            icon_path="src\icons\PPMT.png",
            category=loan_functions_category)
@knext.input_table(name="Input Data", description="Table containing payment period, rate, nper, and pv values")
@knext.output_table(name="PPMT Results", description="Table with calculated PPMT values")
class PPMTNode:
    """Calculates the principal payment portion for a specific period of a loan.
    
    # PPMT Node
    
    This node implements Excel's **PPMT** function to determine how much of a specific loan payment goes toward reducing the principal balance. This is useful for creating amortization schedules and understanding how loan payments are allocated between principal and interest over time.
    
    ## Input Requirements
    
    The input table must contain the following columns:
    
    1. **Rate column**: Interest rate per period (decimal format)
    2. **Period column**: Specific period number for which to calculate the principal payment (integer or decimal)
    3. **Number of periods column**: Total number of payment periods in the loan (integer or decimal)
    4. **Present value column**: Principal loan amount or present value (monetary amount)
    
    ## Configuration Parameters
    
    **Rate Column**: Select the column containing the interest rate per period in decimal format (e.g., 0.004167 for monthly rate).
    
    **Period Column**: Select the column containing the specific period number for which you want to calculate the principal payment portion. Must be between 1 and the total number of periods.
    
    **Number of Periods Column**: Select the column containing the total number of payment periods for the entire loan term.
    
    **Present Value Column**: Select the column containing the loan principal amount or present value.
    
    **Payment Timing**: Configure when payments are due. Set to `0` for end-of-period payments (default) or `1` for beginning-of-period payments.
    
    ## Output
    
    The node appends a new **PPMT** column containing the principal payment portion for the specified period. Values are typically negative, representing the amount of principal reduction for that payment period.
    
  
    """
    
    rate_column = knext.ColumnParameter(
        "Rate Column",
        "Column containing the interest rate per period",
        column_filter=lambda col: col.ktype == knext.double() or col.ktype == knext.int64() or col.ktype == knext.int32()
    )
    
    per_column = knext.ColumnParameter(
        "Period Column",
        "Column containing the period for which to calculate the payment",
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
        # Check if PPMT column already exists and remove it if it does
        output_schema = input_schema
        if "PPMT" in input_schema.column_names:
            output_schema = input_schema.remove("PPMT")
        return output_schema.append(knext.Column(knext.double(), "PPMT"))

    def execute(self, exec_context, input_table):
        df = input_table.to_pandas()
        
        # Remove PPMT column if it already exists
        if "PPMT" in df.columns:
            df = df.drop(columns=["PPMT"])
        
        df["PPMT"] = npf.ppmt(
            rate=df[self.rate_column],
            per=df[self.per_column],
            nper=df[self.nper_column],
            pv=df[self.pv_column],
            when=self.pmt_type
        )
        
        return knext.Table.from_pandas(df)