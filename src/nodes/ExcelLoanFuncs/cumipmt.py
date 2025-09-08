import knime.extension as knext
import numpy as np
import numpy_financial as npf
from nodes.utils.category import loan_functions_category


@knext.node(name="CUMIPMT",
            node_type=knext.NodeType.MANIPULATOR,
            icon_path="src\icons\CUMIPMT.png",
            category=loan_functions_category)
@knext.input_table(name="Input Data", description="Table containing rate, nper, pv, start period, and end period values")
@knext.output_table(name="CUMIPMT Results", description="Table with calculated cumulative interest payments")
class CUMIPMTNode:
    """Calculates the cumulative interest paid between two specified periods of a loan.
    
    # CUMIPMT Node
    
    This node implements Excel's **CUMIPMT** function to calculate the total interest payments made over a range of payment periods. This is particularly useful for tax calculations, financial planning, and understanding the total interest cost over specific portions of a loan's lifetime.
    
    ## Input Requirements
    
    The input table must contain the following columns:
    
    1. **Rate column**: Interest rate per period (decimal format)
    2. **Number of periods column**: Total number of payment periods in the loan (integer or decimal)
    3. **Present value column**: Principal loan amount or present value (monetary amount)
    4. **Start period column**: First period to include in the cumulative calculation (integer or decimal)
    5. **End period column**: Last period to include in the cumulative calculation (integer or decimal)
    
    ## Configuration Parameters
    
    **Rate Column**: Select the column containing the interest rate per period in decimal format.
    
    **Number of Periods Column**: Select the column containing the total number of payment periods for the complete loan term.
    
    **Present Value Column**: Select the column containing the loan principal amount or present value.
    
    **Start Period Column**: Select the column containing the first period number to include in the cumulative interest calculation. Must be between 1 and the total number of periods.
    
    **End Period Column**: Select the column containing the last period number to include in the cumulative interest calculation. Must be greater than or equal to the start period and not exceed the total number of periods.
    
    **Payment Timing**: Configure when payments are due within each period. Set to `0` for end-of-period payments (default) or `1` for beginning-of-period payments.
    
    ## Output
    
    The node appends a new **CUMIPMT** column containing the sum of all interest payments from the start period through the end period (inclusive). Values are typically negative, representing the total interest cost over the specified range.
    

    """
    
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
    
    start_period_column = knext.ColumnParameter(
        "Start Period Column",
        "Column containing the first period to include",
        column_filter=lambda col: col.ktype == knext.double() or col.ktype == knext.int64() or col.ktype == knext.int32()
    )
    
    end_period_column = knext.ColumnParameter(
        "End Period Column",
        "Column containing the last period to include",
        column_filter=lambda col: col.ktype == knext.double() or col.ktype == knext.int64() or col.ktype == knext.int32()
    )
    
    pmt_type = knext.BoolParameter(
        "Payment Timing",
        "When payments are due (0: end of period, 1: beginning of period)",
        False
    )

    def configure(self, configure_context, input_schema):
        # Check if CUMIPMT column already exists and remove it if it does
        output_schema = input_schema
        if "CUMIPMT" in input_schema.column_names:
            output_schema = input_schema.remove("CUMIPMT")
        return output_schema.append(knext.Column(knext.double(), "CUMIPMT"))

    def execute(self, exec_context, input_table):
        df = input_table.to_pandas()
        
        # Remove CUMIPMT column if it already exists
        if "CUMIPMT" in df.columns:
            df = df.drop(columns=["CUMIPMT"])
        
        def calculate_cumipmt(row):
            return np.sum([
                npf.ipmt(row[self.rate_column], per, row[self.nper_column], 
                        row[self.pv_column], when=self.pmt_type)
                for per in range(int(row[self.start_period_column]), 
                               int(row[self.end_period_column]) + 1)
            ])
        
        df["CUMIPMT"] = df.apply(calculate_cumipmt, axis=1)
        
        return knext.Table.from_pandas(df)