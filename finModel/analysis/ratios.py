'''
PURPOSE: Houses the ratios and datasets we would be using for plotting purposes
'''

from finModel.statements.main import FinancialStatement
from finModel.statements.income import IncomeStatement
import pandas as pd


def ebitda_revenue_ratio(fin:FinancialStatement) -> pd.DataFrame:

    ebitda: pd.Series = fin.income.ebitda
    revenue: pd.Series = fin.income.revenue.sales
    ratio: pd.Series = (ebitda/revenue) * 100
    combined: pd.DataFrame = pd.concat([revenue,ebitda,ratio],axis=1)
    combined.columns = ["Revenues","EBITDA","EBITDA%"]
    combined["period"] = combined.index

    return combined.reset_index()
