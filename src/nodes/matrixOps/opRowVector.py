import knime.extension as knext
import pandas as pd
import logging
from nodes.utils.category import matrix_category
from nodes.matrixOps.utils import Operation, MatrixRowVectorOperationOptions

LOGGER = logging.getLogger(__name__)

@knext.node(
    name="Matrix x Row Vector",
    node_type=knext.NodeType.MANIPULATOR,
    icon_path="src\icons\RowVector.png",
    category=matrix_category,
)
@knext.input_table(name="Matrix", description="Matrix (nxm) - all numeric columns will be used")
@knext.input_table(name="Row Vector", description="Row vector (1xm) - must have 1 row and same number of numeric columns as matrix")
@knext.output_table(name="Result", description="Element-wise result containing all numeric columns from matrix")
class MatrixRowVectorNode:
    """Performs element-wise operations between a matrix and a row vector with automatic broadcasting.

# Matrix x Row Vector Node

This node executes element-wise mathematical operations between a matrix (represented as multiple numeric columns) and a row vector (a single row with multiple numeric columns). The operation automatically broadcasts the single row of values from the row vector across all rows of the matrix, performing column-wise calculations where corresponding columns are matched by position.

## Input Requirements

The node requires two input tables:

1. **Matrix Input**: Table containing the matrix data where all numeric columns will be automatically included in the operation
2. **Row Vector Input**: Table containing exactly one row with numeric values that will be broadcast across the matrix

**Matrix Requirements**: Must contain at least one numeric column (integer or double type). Non-numeric columns are preserved in the output without modification.

**Row Vector Requirements**: Must contain exactly one row and must have the same number of numeric columns as the matrix input. The row vector provides the values that will be applied to every row of the matrix.

**Column Matching**: Columns are matched by position, not by name. The first numeric column from the matrix operates with the first numeric column from the row vector, the second with the second, and so forth.

## Configuration Parameters

**Operation Type**: Choose the mathematical operation to perform between the matrix and row vector. Addition performs Matrix + RowVector, adding row vector values to each matrix row. Subtraction performs Matrix - RowVector, subtracting row vector values from each matrix row. Multiplication performs Matrix * RowVector, multiplying each matrix row by row vector values. Division performs Matrix / RowVector, dividing each matrix row by row vector values.

**Handle Missing Values**: Enable this option to automatically replace any missing values (NaN) with zero before performing the operation. When disabled, missing values will propagate through the calculation according to standard mathematical rules.

## Output Structure

The output table contains the following columns:

**Non-Numeric Columns**: All non-numeric columns from the matrix input are preserved unchanged and appear first in the output table.

**Result Columns**: All numeric columns from the matrix input, now containing the results of the element-wise operation with the corresponding row vector values. These columns retain their original names from the matrix input.

The output table has the same number of rows as the matrix input and maintains the original row order.
"""
    opts = MatrixRowVectorOperationOptions()

    def configure(self, ctx, schema_m, schema_r):
        # Get all numeric columns from matrix
        numeric_cols_m = [c for c in schema_m if c.ktype in (knext.double(), knext.int32(), knext.int64())]
        numeric_cols_r = [c for c in schema_r if c.ktype in (knext.double(), knext.int32(), knext.int64())]
        
        if len(numeric_cols_m) == 0:
            raise ValueError("Matrix must contain at least one numeric column")
        if len(numeric_cols_r) == 0:
            raise ValueError("Row vector must contain at least one numeric column")
        
        # Check that row vector has same number of numeric columns as matrix
        if len(numeric_cols_m) != len(numeric_cols_r):
            raise ValueError(f"Row vector must have the same number of numeric columns as matrix. Matrix has {len(numeric_cols_m)}, row vector has {len(numeric_cols_r)}")
        
        # Create output schema with all numeric columns as double (float)
        output_columns = []
        numeric_col_names = [c.name for c in numeric_cols_m]
        
        for col in schema_m:
            if col.name in numeric_col_names:
                # All numeric operations output double (float) regardless of input types
                output_columns.append(knext.Column(knext.double(), col.name))
            else:
                # Non-numeric columns remain unchanged
                output_columns.append(col)
        
        return knext.Schema.from_columns(output_columns)

    def execute(self, ctx, table_m, table_r):
        df_m = table_m.to_pandas()
        df_r = table_r.to_pandas()
        
        # Get all numeric columns
        numeric_cols_m = [c for c in df_m.columns if df_m[c].dtype in ['int32', 'int64', 'float64']]
        numeric_cols_r = [c for c in df_r.columns if df_r[c].dtype in ['int32', 'int64', 'float64']]
        
        # Validate row vector has exactly 1 row
        if len(df_r) != 1:
            raise ValueError(f"Row vector must have exactly 1 row, but has {len(df_r)}")
        
        # Validate same number of numeric columns
        if len(numeric_cols_m) != len(numeric_cols_r):
            raise ValueError(f"Row vector must have the same number of numeric columns as matrix. Matrix has {len(numeric_cols_m)}, row vector has {len(numeric_cols_r)}")

        if self.opts.handle_missing:
            df_m = df_m.fillna(0)
            df_r = df_r.fillna(0)

        func_map = {
            Operation.ADDITION.name: lambda x, y: x + y,
            Operation.SUBTRACTION.name: lambda x, y: x - y,
            Operation.MULTIPLICATION.name: lambda x, y: x * y,
            Operation.DIVISION.name: lambda x, y: x / y,
        }
        func = func_map[self.opts.operation]
        
        # Create a copy of the original matrix to preserve column order
        result = df_m.copy()
        
        # Perform element-wise operation only on numeric columns (ordered by position)
        for i, col_m in enumerate(numeric_cols_m):
            col_r = numeric_cols_r[i]
            row_value = df_r.iloc[0][col_r]
            result[col_m] = func(df_m[col_m], row_value)
        
        return knext.Table.from_pandas(result)