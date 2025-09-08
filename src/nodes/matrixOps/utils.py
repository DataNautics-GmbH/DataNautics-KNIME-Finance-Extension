import knime.extension as knext

# Shared enum for operations
class Operation(knext.EnumParameterOptions):
    ADDITION = ("Addition", "Add the two matrices element-wise")
    SUBTRACTION = ("Subtraction", "Subtract the second matrix from the first element-wise")
    MULTIPLICATION = ("Multiplication", "Multiply the two matrices element-wise")
    DIVISION = ("Division", "Divide the first matrix by the second element-wise")

# Parameter group for matrix operations
@knext.parameter_group(label="Processing Options")
class MatrixOperationOptions:
    operation = knext.EnumParameter(
        "Operation",
        "Select the operation to perform",
        Operation.ADDITION.name,
        Operation,
    )
    handle_missing = knext.BoolParameter(
        "Handle missing values",
        "Replace missing values with 0",
        default_value=False,
    )

# Parameter group for matrix-vector operations
@knext.parameter_group(label="Processing Options")
class MatrixVectorOperationOptions:
    operation = knext.EnumParameter(
        "Operation",
        "Select the operation to perform",
        Operation.ADDITION.name,
        Operation,
    )
    vector_column = knext.ColumnParameter(
        "Vector Column",
        "Select single column from vector input",
        port_index=1,
        column_filter=lambda c: c.ktype in (knext.double(), knext.int32(), knext.int64()),
    )
    handle_missing = knext.BoolParameter(
        "Handle missing values",
        "Replace missing values with 0",
        default_value=False,
    )

# Parameter group for matrix-row vector operations  
@knext.parameter_group(label="Processing Options")
class MatrixRowVectorOperationOptions:
    operation = knext.EnumParameter(
        "Operation",
        "Select the operation to perform",
        Operation.ADDITION.name,
        Operation,
    )
    handle_missing = knext.BoolParameter(
        "Handle missing values",
        "Replace missing values with 0",
        default_value=False,
    )

# Parameter group for matrix-scalar operations
@knext.parameter_group(label="Processing Options")
class MatrixScalarOperationOptions:
    operation = knext.EnumParameter(
        "Operation",
        "Select the operation to perform",
        Operation.ADDITION.name,
        Operation,
    )
    handle_missing = knext.BoolParameter(
        "Handle missing values",
        "Replace missing values with 0",
        default_value=False,
    )