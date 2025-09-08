import knime.extension as knext
import numpy as np
import numpy_financial as npf
from nodes.utils.category import loan_functions_category


@knext.node(name="PV",
            node_type=knext.NodeType.MANIPULATOR,
            icon_path="src\icons\PV.png",
            category=loan_functions_category)
@knext.input_table(name="Input Data", description="Table containing rate, nper, and pmt values")
@knext.output_table(name="PV Results", description="Table with calculated present values")
class PVNode:
    """Calculates the present value of a series of future payments or an investment.
    
    # PV Node
    
    This node implements Excel's **PV** function to calculate the present value of a series of equal payments made at regular intervals, discounted at a constant interest rate. This is the inverse calculation of PMT and is fundamental for loan valuation, investment analysis, and determining how much a stream of future payments is worth in today's dollars.
    
    ## Input Requirements
    
    The input table must contain the following columns:
    
    1. **Rate column**: Interest rate per period (decimal format)
    2. **Number of periods column**: Total number of payment periods (integer or decimal)
    3. **Payment column**: Payment amount made each period (monetary amount)
    
    ## Configuration Parameters
    
    **Rate Column**: Select the column containing the discount rate or interest rate per period in decimal format (e.g., 0.004167 for monthly rate).
    
    **Number of Periods Column**: Select the column containing the total number of payment periods over which payments will be made or received.
    
    **Payment Column**: Select the column containing the payment amount made each period. Positive values represent money received, negative values represent money paid out.
    
    **Payment Timing**: Configure when payments occur within each period. Set to `0` for end-of-period payments (default) or `1` for beginning-of-period payments.
    
    ## Output
    
    The node appends a new **PV** column containing the calculated present value of the payment stream. The result represents the lump sum amount that, if invested today at the given interest rate, would provide the same financial benefit as the series of future payments.
    
  
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
    
    pmt_column = knext.ColumnParameter(
        "Payment Column",
        "Column containing the payment made each period",
        column_filter=lambda col: col.ktype == knext.double() or col.ktype == knext.int64() or col.ktype == knext.int32()
    )
    
    pmt_type = knext.BoolParameter(
        "Payment Timing",
        "When payments are due (0: end of period, 1: beginning of period)",
        False
    )

    def configure(self, configure_context, input_schema):
        # Check if PV column already exists and remove it if it does
        output_schema = input_schema
        if "PV" in input_schema.column_names:
            output_schema = input_schema.remove("PV")
        return output_schema.append(knext.Column(knext.double(), "PV"))

    def execute(self, exec_context, input_table):
        df = input_table.to_pandas()
        
        # Remove PV column if it already exists
        if "PV" in df.columns:
            df = df.drop(columns=["PV"])
        
        df["PV"] = npf.pv(
            rate=df[self.rate_column],
            nper=df[self.nper_column],
            pmt=df[self.pmt_column],
            when=self.pmt_type
        )
        
        return knext.Table.from_pandas(df)