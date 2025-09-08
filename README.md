<div style="display: flex; justify-content: center; align-items: center;"><h1>DataNautics KNIME Extension</h1></div>
<p align="center">
  <img src="src\icons\DatanNauticsLogoWhiteBG.png" alt="Logo" style="width: 300px; " />
</p>

<div style="display: flex; justify-content: center; align-items: center;">This is an Extension that provides nodes that are useful in the context of Financial Operations</div><br><br>

# Financial Functions Extension for KNIME

A comprehensive KNIME extension providing Excel-compatible financial functions and matrix operations for loan analysis, amortization scheduling, and mathematical computations.

## Overview

This extension brings powerful financial calculation capabilities to KNIME Analytics Platform, enabling users to perform complex loan calculations, generate detailed amortization schedules, and execute matrix operations directly within their KNIME workflows. All financial functions are fully compatible with Excel's implementations, ensuring consistent results across platforms.

## Features

### Excel-Compatible Loan Functions
- **PMT**: Calculate periodic loan payments
- **IPMT**: Determine interest payment portions
- **PPMT**: Calculate principal payment portions
- **CUMIPMT**: Compute cumulative interest payments over date ranges
- **CUMPRINC**: Calculate cumulative principal payments over date ranges
- **PV**: Determine present value of payment streams

### Comprehensive Amortization Schedules
- **Full Loan Schedule**: Complete amortization table with all payment components
- **CUMIPMT Schedule**: Cumulative interest payment tracking
- **CUMPMT Schedule**: Cumulative total payment tracking
- **CUMPRINCE Schedule**: Cumulative principal payment tracking
- **IPMT Schedule**: Period-by-period interest payments
- **PPMT Schedule**: Period-by-period principal payments
- **Open PMT Balance Schedule**: Forward-looking payment obligations
- **Open PPMT Balance Schedule**: Forward-looking outstanding Principal
- **Open IPMT Balance Schedule**: Forward-looking outstanding Interest

### Matrix Operations
- **Matrix x Matrix**: Element-wise operations between two matrices
- **Matrix x Column Vector**: Broadcast column vector across matrix rows
- **Matrix x Row Vector**: Broadcast row vector across matrix columns
- **Matrix x Scalar**: Apply scalar operations to entire matrices

## Installation

1. Download the extension from the KNIME Community Hub or build from source
2. Install through KNIME Analytics Platform: File → Install KNIME Extensions
3. Restart KNIME Analytics Platform
4. Find the nodes under "Community Extensions → DataNautics Finance Extension"

## Quick Start

### Basic Loan Payment Calculation

1. Create a table with loan parameters:
   - **rate**: 0.05 (5% annual interest rate)
   - **nper**: 360 (30 years × 12 months)
   - **pv**: 100000 (loan amount)

2. Use the **PMT** node to calculate monthly payments
3. The result will show approximately -$536.82 per month

### Generate Complete Amortization Schedule

1. Prepare input data with annual rate, number of periods, and present value
2. Use the **Full Loan Schedule** node
3. Configure payment frequency (Monthly, Quarterly, or Annual)
4. Select interest calculation method (Simple or Compound)
5. The output provides a complete period-by-period breakdown

### Matrix Operations Example

1. Create two tables representing matrices with numeric columns
2. Use **Matrix x Matrix** node for element-wise operations
3. Choose operation type (Addition, Subtraction, Multiplication, Division)
4. Configure missing value handling as needed

## Node Categories

### Loan Functions
Located under `/community/financial_functions/loan_functions`

**PMT** - Calculate fixed periodic payments for loan amortization
**IPMT** - Determine interest portion of payments for specific periods  
**PPMT** - Calculate principal portion of payments for specific periods
**CUMIPMT** - Sum interest payments over specified period ranges
**CUMPRINC** - Sum principal payments over specified period ranges
**PV** - Calculate present value of future payment streams

### Amortization Schedules
Located under `/community/financial_functions/schedule_functions`

**Full Loan Schedule** - Comprehensive amortization table with all components
**CUMIPMT Schedule** - Progressive cumulative interest tracking
**CUMPMT Schedule** - Progressive cumulative payment tracking  
**CUMPRINCE Schedule** - Progressive cumulative principal tracking
**IPMT Schedule** - Period-by-period interest payment breakdown
**PPMT Schedule** - Period-by-period principal payment breakdown
**Open PMT Balance Schedule**: Forward-looking payment obligations
**Open PPMT Balance Schedule**: Forward-looking outstanding Principal
**Open IPMT Balance Schedule**: Forward-looking outstanding Interest

### Matrix Operations
Located under `/community/financial_functions/matrix_operations`

**Matrix x Matrix** - Element-wise operations between conformable matrices
**Matrix x Column Vector** - Row-wise vector broadcasting operations
**Matrix x Row Vector** - Column-wise vector broadcasting operations  
**Matrix x Scalar** - Uniform scalar operations across matrix elements

## Configuration Options

### Payment Frequency
All schedule nodes support configurable payment frequencies:
- **Monthly**: 12 payments per year (most common)
- **Quarterly**: 4 payments per year  
- **Annual**: 1 payment per year

### Interest Rate Calculation
Choose between two interest calculation methods:
- **Simple**: Periodic rate = Annual rate ÷ Frequency
- **Compound**: Periodic rate = (1 + Annual rate)^(1/Frequency) - 1

### Payment Timing
Configure when payments occur within each period:
- **0**: End-of-period payments (ordinary annuity) - default
- **1**: Beginning-of-period payments (annuity due)

### Missing Value Handling
Matrix operations include optional missing value replacement:
- **Enabled**: Replace NaN values with zero before calculation
- **Disabled**: Propagate missing values according to mathematical rules

## Input Requirements

### Loan Functions
**Rate columns**: Annual interest rates in decimal format (e.g., 0.05 for 5%)
**Period columns**: Payment period numbers or total periods (integer or decimal)
**Present value columns**: Loan amounts or present values (monetary amounts)
**Payment columns**: Payment amounts for PV calculations

### Matrix Operations
**Numeric columns**: Integer or double precision columns for calculations
**Dimensional compatibility**: Matching dimensions for matrix operations
**Broadcasting requirements**: Appropriate vector/scalar dimensions

## Output Structure

### Individual Loan Functions
Original input table with appended calculation column:
- **PMT**: Periodic payment amounts
- **IPMT**: Interest payment portions  
- **PPMT**: Principal payment portions
- **CUMIPMT**: Cumulative interest totals
- **CUMPRINC**: Cumulative principal totals
- **PV**: Present value calculations

### Schedule Functions
Expanded table with one row per payment period containing:
- **Period**: Sequential period numbers (1 to total periods)
- **Payment components**: PMT, IPMT, PPMT as applicable
- **Cumulative tracking**: Running totals for payments, interest, principal
- **Balance information**: Remaining balances and outstanding amounts
- **Original columns**: All input table columns preserved

### Matrix Operations
Result table maintaining original structure:
- **Non-numeric columns**: Preserved unchanged from primary input
- **Result columns**: Calculated values with original column names
- **Dimensional consistency**: Same number of rows as input matrices

## Use Cases

### Financial Analysis
- Mortgage payment calculations and comparisons
- Loan amortization schedule generation
- Interest vs. principal allocation tracking
- Refinancing analysis and decision support
- Investment present value calculations

### Risk Management
- Cash flow projection and planning
- Payment obligation tracking over time
- Outstanding balance monitoring
- Interest cost analysis for budgeting

### Reporting and Compliance
- Detailed amortization reports for accounting
- Tax-related interest payment summaries
- Loan progress tracking and documentation
- Financial statement preparation support

### Mathematical Computing
- Element-wise matrix computations
- Vector broadcasting operations
- Batch mathematical transformations
- Data scaling and normalization

## Technical Notes

### Precision and Accuracy
All calculations use double-precision floating-point arithmetic to ensure accuracy consistent with Excel implementations. Financial functions follow standard mathematical conventions for loan calculations.

### Performance Considerations
Schedule nodes generate one row per payment period, so a 30-year monthly loan produces 360 output rows per input loan. Consider memory requirements when processing large loan portfolios.

### Data Type Handling
The extension automatically handles mixed numeric types (integer and double) in input columns. Non-numeric columns are preserved without modification in all operations.



## Support and Contributing

For issues, feature requests, or contributions, please visit the project repository. The extension is built using the KNIME Python Extension framework and follows standard KNIME development practices.

## License

This extension is released under Apache 2.0. See LICENSE file for full terms and conditions.

## Version History

**v1.0.0**: Initial release with core loan functions and basic schedules
