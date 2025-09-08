
import knime_extension as knext



category = knext.category(
    path="/community",
    level_id="DataNautics_Fin",
    name="DataNautics Finance Extension",
    description="Nodes for working in Finance Operations and FP&A",

    icon="src\icons\DN.png",
)

loan_category = knext.category(
    path=category,
    level_id="DataNautics_Fin_LoanSchedules",
    name="Loan Calculations",
    description="Excel-Like Loan Calculation Nodes",

    icon="src\icons\LOANSCHEDULE.png",
)


loan_schedule_category = knext.category(
    path=loan_category,
    level_id="DataNautics_Fin_LoanSchedules",
    name="Loan Schedules Nodes",
    description="Loan Amortisation Schedule Nodes",

    icon="src\icons\PPMTSCHEDULEFUTURE.png",
)

loan_functions_category = knext.category(
    path=loan_category,
    level_id="DataNautics_Fin_LoanFunctions",
    name="Loan Functions Nodes",
    description="Excel-Like Loan Calculation Nodes",

    icon="src\icons\PMT.png",
)





matrix_category = knext.category(
    path=category,
    level_id="DataNautics_Fin_MatrixOps",
    name="DataNautics Matrix Operations",
    description="Matrix Operations Nodes (Element-wise)",

    icon="src\icons\MatrixXMatrix.png",
)