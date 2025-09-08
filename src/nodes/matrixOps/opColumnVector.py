import knime.extension as knext
import pandas as pd
import logging
from nodes.utils.category import matrix_category
from nodes.matrixOps.utils import Operation, MatrixVectorOperationOptions

LOGGER = logging.getLogger(__name__)

@knext.node(
    name="Matrix x Column Vector",
    node_type=knext.NodeType.MANIPULATOR,
    icon_path="src\icons\ColVector.png",
    category=matrix_category,
)
@knext.input_table(name="Matrix", description="Matrix (nxm) - all numeric columns will be used")
@knext.input_table(name="Column Vector", description="Column vector (nx1)")
@knext.output_table(name="Result", description="Element-wise result containing all numeric columns from matrix")
class MatrixColumnVectorNode:
    """Performs element-wise operations between a matrix and a column vector with automatic broadcasting.

# Matrix x Column Vector Node

This node executes element-wise mathematical operations between a matrix (represented as multiple numeric columns) and a column vector (a single selected column). The operation automatically broadcasts the vector values across all numeric columns of the matrix, performing row-wise calculations where each matrix row is operated with the corresponding vector row value.

## Input Requirements

The node requires two input tables:

1. **Matrix Input**: Table containing the matrix data where all numeric columns will be automatically included in the operation
2. **Column Vector Input**: Table containing the vector data where one numeric column must be selected for the operation

**Matrix Requirements**: Must contain at least one numeric column (integer or double type). Non-numeric columns are preserved in the output without modification.

**Vector Requirements**: Must have exactly the same number of rows as the matrix input table. Must contain at least one numeric column for selection.

## Configuration Parameters

**Vector Column**: Select the specific numeric column from the vector input table that will be used in the operation. This column will be broadcast across all numeric columns in the matrix.

**Operation Type**: Choose the mathematical operation to perform between the matrix and vector. Addition performs Matrix + Vector with element-wise addition. Subtraction performs Matrix - Vector with element-wise subtraction. Multiplication performs Matrix * Vector with element-wise multiplication. Division performs Matrix / Vector with element-wise division.

**Handle Missing Values**: Enable this option to automatically replace any missing values (NaN) with zero before performing the operation. When disabled, missing values will propagate through the calculation according to standard mathematical rules.

## Output Structure

The output table contains the following columns:

**Non-Numeric Columns**: All non-numeric columns from the matrix input are preserved unchanged and appear first in the output table.

**Result Columns**: All numeric columns from the matrix input, now containing the results of the element-wise operation with the selected vector column. These columns retain their original names from the matrix input.

The output table has the same number of rows as both input tables and maintains the row order from the matrix input.
"""
    opts = MatrixVectorOperationOptions()

    def configure(self, ctx, schema_m, schema_v):
        # Get all numeric columns from matrix
        numeric_cols_m = [c for c in schema_m if c.ktype in (knext.double(), knext.int32(), knext.int64())]
        
        if len(numeric_cols_m) == 0:
            raise ValueError("Matrix must contain at least one numeric column")
        
        if not self.opts.vector_column:
            raise ValueError("Please select a column for vector input")
        
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

    def execute(self, ctx, table_m, table_v):
        df_m = table_m.to_pandas()
        df_v = table_v.to_pandas()
        
        # Get all numeric columns from matrix
        numeric_cols_m = [c for c in df_m.columns if df_m[c].dtype in ['int32', 'int64', 'float64']]
        vec = df_v[self.opts.vector_column]

        if self.opts.handle_missing:
            df_m = df_m.fillna(0)
            vec = vec.fillna(0)

        if len(vec) != len(df_m):
            raise ValueError("Vector length must match number of rows in matrix")

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
            result[col] = func(df_m[col], vec.values)
        
        return knext.Table.from_pandas(result)