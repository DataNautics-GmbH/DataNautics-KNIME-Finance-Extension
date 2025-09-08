import knime.extension as knext
import pandas as pd
import logging
from nodes.utils.category import matrix_category
from nodes.matrixOps.utils import Operation, MatrixOperationOptions

LOGGER = logging.getLogger(__name__)

@knext.node(
    name="Matrix x Matrix",
    node_type=knext.NodeType.MANIPULATOR,
    icon_path="src\icons\MatrixXMatrix.png",
    category=matrix_category,
)
@knext.input_table(name="Matrix A", description="First matrix (nxm) - all numeric columns will be used")
@knext.input_table(name="Matrix B", description="Second matrix (nxm) - all numeric columns will be used")
@knext.output_table(name="Result", description="Element-wise result containing all numeric columns from both matrices")
class MatrixMatrixNode:
    """Performs element-wise operations between two matrices of identical dimensions.

# Matrix x Matrix Node

This node executes element-wise mathematical operations between two matrices represented as tables with multiple numeric columns. The operation automatically processes all numeric columns from both matrices, performing calculations between corresponding columns based on their positional order rather than column names.

## Input Requirements

The node requires two input tables representing matrices:

1. **Matrix A**: First matrix table where all numeric columns will be automatically included in the operation
2. **Matrix B**: Second matrix table where all numeric columns will be automatically included in the operation

**Dimensional Requirements**: Both matrices must have exactly the same number of rows and the same number of numeric columns. The matrices must be conformable for element-wise operations.

**Column Requirements**: Each matrix must contain at least one numeric column (integer or double type). Non-numeric columns from Matrix A are preserved in the output.

**Column Matching**: Columns are matched by position, not by name. The first numeric column from Matrix A operates with the first numeric column from Matrix B, the second with the second, and so forth.

## Configuration Parameters

**Operation Type**: Choose the mathematical operation to perform between the matrices. Addition performs A + B with element-wise addition of corresponding matrix elements. Subtraction performs A - B with element-wise subtraction where B is subtracted from A. Multiplication performs A * B with element-wise multiplication, also known as Hadamard product. Division performs A / B with element-wise division where A is divided by B.

**Handle Missing Values**: Enable this option to automatically replace any missing values (NaN) with zero before performing the operation. When disabled, missing values will propagate through the calculation according to standard mathematical rules.

## Output Structure

The output table contains the following columns:

**Non-Numeric Columns**: All non-numeric columns from Matrix A are preserved unchanged and appear first in the output table.

**Result Columns**: All numeric columns containing the results of the element-wise operation between corresponding columns from Matrix A and Matrix B. These columns retain the original column names from Matrix A.

The output table has the same number of rows as both input matrices and maintains the row order from Matrix A.
"""
    opts = MatrixOperationOptions()

    def configure(self, ctx, schema_a, schema_b):
        # Get all numeric columns from both schemas
        numeric_cols_a = [c for c in schema_a if c.ktype in (knext.double(), knext.int32(), knext.int64())]
        numeric_cols_b = [c for c in schema_b if c.ktype in (knext.double(), knext.int32(), knext.int64())]
        
        if len(numeric_cols_a) == 0:
            raise ValueError("Matrix A must contain at least one numeric column")
        if len(numeric_cols_b) == 0:
            raise ValueError("Matrix B must contain at least one numeric column")
        
        # Check that both matrices have the same number of numeric columns
        if len(numeric_cols_a) != len(numeric_cols_b):
            raise ValueError(f"Matrices must have the same number of numeric columns. Matrix A has {len(numeric_cols_a)}, Matrix B has {len(numeric_cols_b)}")
        
        # Create output schema with all numeric columns as double (float) and preserve column order
        output_columns = []
        numeric_col_names = [c.name for c in numeric_cols_a]
        
        for col in schema_a:
            if col.name in numeric_col_names:
                # All numeric operations output double (float) regardless of input types
                output_columns.append(knext.Column(knext.double(), col.name))
            else:
                # Non-numeric columns remain unchanged
                output_columns.append(col)
        
        return knext.Schema.from_columns(output_columns)

    def execute(self, ctx, table_a, table_b):
        df_a = table_a.to_pandas()
        df_b = table_b.to_pandas()
        
        # Get all numeric columns
        numeric_cols_a = [c for c in df_a.columns if df_a[c].dtype in ['int32', 'int64', 'float64']]
        numeric_cols_b = [c for c in df_b.columns if df_b[c].dtype in ['int32', 'int64', 'float64']]
        
        # Validate dimensions match
        if len(numeric_cols_a) != len(numeric_cols_b):
            raise ValueError(f"Matrices must have the same number of numeric columns. Matrix A has {len(numeric_cols_a)}, Matrix B has {len(numeric_cols_b)}")
        
        if len(df_a) != len(df_b):
            raise ValueError(f"Matrices must have the same number of rows. Matrix A has {len(df_a)}, Matrix B has {len(df_b)}")

        if self.opts.handle_missing:
            df_a = df_a.fillna(0)
            df_b = df_b.fillna(0)

        func_map = {
            Operation.ADDITION.name: lambda x, y: x + y,
            Operation.SUBTRACTION.name: lambda x, y: x - y,
            Operation.MULTIPLICATION.name: lambda x, y: x * y,
            Operation.DIVISION.name: lambda x, y: x / y,
        }
        func = func_map[self.opts.operation]
        
        # Create a copy of Matrix A to preserve column order
        result = df_a.copy()
        
        # Perform element-wise operation only on numeric columns (ordered by position)
        for i, col_a in enumerate(numeric_cols_a):
            col_b = numeric_cols_b[i]
            result[col_a] = func(df_a[col_a], df_b[col_b])
        
        return knext.Table.from_pandas(result)