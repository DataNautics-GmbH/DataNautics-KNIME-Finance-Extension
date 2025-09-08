import knime.extension as knext
import pandas as pd
import logging
from nodes.utils.category import matrix_category
from nodes.matrixOps.utils import Operation, MatrixScalarOperationOptions

LOGGER = logging.getLogger(__name__)

@knext.node(
    name="Matrix x Scalar",
    node_type=knext.NodeType.MANIPULATOR,
    icon_path="src\icons\Scalar.png",
    category=matrix_category,
)
@knext.input_table(name="Matrix", description="Matrix (nxm) - all numeric columns will be used")
@knext.input_table(name="Scalar", description="Single-value table")
@knext.output_table(name="Result", description="Element-wise result containing all numeric columns from matrix")
class MatrixScalarNode:
    """Performs element-wise operations between a matrix and a scalar value with complete broadcasting.

# Matrix x Scalar Node

This node executes element-wise mathematical operations between a matrix (represented as multiple numeric columns) and a single scalar value. The operation automatically applies the scalar value to every element in every numeric column of the matrix, providing uniform scaling or adjustment across the entire matrix.

## Input Requirements

The node requires two input tables:

1. **Matrix Input**: Table containing the matrix data where all numeric columns will be automatically included in the operation
2. **Scalar Input**: Table containing exactly one column and one row (single cell) with the scalar value to be applied

**Matrix Requirements**: Must contain at least one numeric column (integer or double type). Non-numeric columns are preserved in the output without modification.

**Scalar Requirements**: Must be a table with exactly one column and one row, containing a single numeric value that will be broadcast across all elements of the matrix.

## Configuration Parameters

**Operation Type**: Choose the mathematical operation to perform between the matrix and scalar:
- **Addition**: Matrix + Scalar (adds the scalar value to every matrix element)
- **Subtraction**: Matrix - Scalar (subtracts the scalar value from every matrix element)
- **Multiplication**: Matrix * Scalar (multiplies every matrix element by the scalar value)
- **Division**: Matrix / Scalar (divides every matrix element by the scalar value)

**Handle Missing Values**: Enable this option to automatically replace any missing values (NaN) with zero before performing the operation. This applies to both the matrix elements and the scalar value if it is missing.

## Output Structure

The output table contains the following columns:

**Non-Numeric Columns**: All non-numeric columns from the matrix input are preserved unchanged and appear first in the output table.

**Result Columns**: All numeric columns from the matrix input, now containing the results of the element-wise operation with the scalar value. These columns retain their original names from the matrix input.

The output table has the same number of rows as the matrix input and maintains the original row order. Every numeric element in the matrix will have been operated with the same scalar value.
"""
    opts = MatrixScalarOperationOptions()

    def configure(self, ctx, schema_m, schema_s):
        # Get all numeric columns from matrix
        numeric_cols_m = [c for c in schema_m if c.ktype in (knext.double(), knext.int32(), knext.int64())]
        
        if len(numeric_cols_m) == 0:
            raise ValueError("Matrix must contain at least one numeric column")
        
        if schema_s.num_columns != 1:
            raise ValueError("Scalar input must have exactly one column")
        
        # Create output schema with all numeric columns as double (float) and preserve column order
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

    def execute(self, ctx, table_m, table_s):
        df_m = table_m.to_pandas()
        df_s = table_s.to_pandas()
        
        # Get all numeric columns from matrix
        numeric_cols_m = [c for c in df_m.columns if df_m[c].dtype in ['int32', 'int64', 'float64']]
        scalar = df_s.iloc[0, 0]

        if self.opts.handle_missing:
            df_m = df_m.fillna(0)
            if pd.isna(scalar):
                scalar = 0

        func_map = {
            Operation.ADDITION.name: lambda x, y: x + y,
            Operation.SUBTRACTION.name: lambda x, y: x - y,
            Operation.MULTIPLICATION.name: lambda x, y: x * y,
            Operation.DIVISION.name: lambda x, y: x / y,
        }
        func = func_map[self.opts.operation]
        
        # Create a copy of the original matrix to preserve column order
        result = df_m.copy()
        
        # Perform element-wise operation only on numeric columns
        for col in numeric_cols_m:
            result[col] = func(df_m[col], scalar)
        
        return knext.Table.from_pandas(result)