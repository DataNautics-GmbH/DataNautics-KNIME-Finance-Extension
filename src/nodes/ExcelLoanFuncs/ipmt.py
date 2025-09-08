import knime.extension as knext
import numpy as np
import numpy_financial as npf
from nodes.utils.category import loan_functions_category


@knext.node(name="IPMT",
            node_type=knext.NodeType.MANIPULATOR,
            icon_path="src\icons\IPMT.png",
            category=loan_functions_category)
@knext.input_table(name="Input Data", description="Table containing payment period, rate, nper, and pv values")
@knext.output_table(name="IPMT Results", description="Table with calculated IPMT values")
class IPMTNode:
    """Calculates the interest payment portion for a specific period of a loan.
    
    # IPMT Node
    
    This node implements Excel's **IPMT** function to determine how much of a specific loan payment goes toward interest charges. This complements the PPMT function and is essential for creating detailed amortization schedules and understanding the interest cost allocation over the life of a loan.
    
    ## Input Requirements
    
    The input table must contain the following columns:
    
    1. **Rate column**: Interest rate per period (decimal format)
    2. **Period column**: Specific period number for which to calculate the interest payment (integer or decimal)
    3. **Number of periods column**: Total number of payment periods in the loan (integer or decimal)
    4. **Present value column**: Principal loan amount or present value (monetary amount)
    
    ## Configuration Parameters
    
    **Rate Column**: Select the column containing the interest rate per period in decimal format (e.g., 0.004167 for a monthly rate derived from 5% annual rate).
    
    **Period Column**: Select the column containing the specific period number for which you want to calculate the interest payment portion. Must be between 1 and the total number of periods.
    
    **Number of Periods Column**: Select the column containing the total number of payment periods for the complete loan term.
    
    **Present Value Column**: Select the column containing the loan principal amount or present value.
    
    **Payment Timing**: Configure when payments are due within each period. Set to `0` for end-of-period payments (default) or `1` for beginning-of-period payments.
    
    ## Output
    
    The node appends a new **IPMT** column containing the interest payment portion for the specified period. Values are typically negative, representing the interest cost for that specific payment period.
    
  
    """
    
    rate_column = knext.ColumnParameter(
        "Rate Column",
        "Column containing the interest rate per period",
        column_filter=lambda col: col.ktype == knext.double()
    )
    
    per_column = knext.ColumnParameter(
        "Period Column",
        "Column containing the period for which to calculate the interest",
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
        # Check if IPMT column already exists and remove it if it does
        output_schema = input_schema
        if "IPMT" in input_schema.column_names:
            output_schema = input_schema.remove("IPMT")
        return output_schema.append(knext.Column(knext.double(), "IPMT"))

    def execute(self, exec_context, input_table):
        df = input_table.to_pandas()
        
        # Remove IPMT column if it already exists
        if "IPMT" in df.columns:
            df = df.drop(columns=["IPMT"])
        
        df["IPMT"] = npf.ipmt(
            rate=df[self.rate_column],
            per=df[self.per_column],
            nper=df[self.nper_column],
            pv=df[self.pv_column],
            when=self.pmt_type
        )
        
        return knext.Table.from_pandas(df)