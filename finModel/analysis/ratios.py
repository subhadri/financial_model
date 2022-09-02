'''
PURPOSE: Houses the ratios and datasets we would be using for plotting purposes
'''

from finModel.statements.main import FinancialStatement
from finModel.analysis.dcf_valuation import DCFValuation
from dataclasses import dataclass, field
import pandas as pd
import numpy as np


@dataclass
class VizData:
    dcf: DCFValuation
    ebitda_rev_ratio: pd.DataFrame = field(init=False)
    ufcf_trend: pd.DataFrame = field(init=False)

    def __init__(self,dcf:DCFValuation):
        self.dcf = dcf
        self.ebitda_rev_ratio = VizData.get_ebitda_revenue_ratio(self.dcf.statement)
        self.ufcf_trend = VizData.get_ufcf_trend(self.dcf)

    @staticmethod
    def get_ebitda_revenue_ratio(fin:FinancialStatement) -> pd.DataFrame:
        ebitda: pd.Series = fin.income.ebitda
        revenue: pd.Series = fin.income.revenue.sales
        ratio: pd.Series = (ebitda/revenue) * 100
        combined: pd.DataFrame = pd.concat([revenue,ebitda,ratio],axis=1)
        combined.columns = ["Revenues","EBITDA","EBITDA%"]
        combined["period"] = combined.index
        combined["year"] = [date.year for date in combined.period]
        combined["year-q"] = [f"{date.year}Q{date.quarter}" for date in combined.period]
        combined["type"] = ["Actual" if date in fin.actual_dates else "Forecast" for date in combined["period"].values]
        return combined.reset_index().sort_values("period")

    @staticmethod
    def get_ufcf_trend(dcf: DCFValuation) -> pd.DataFrame:
        ufcf: pd.Series = dcf.statement.cash.ufcf[dcf.statement.forecast_dates]
        discount: np.ndarray = np.array([1/np.power(1+dcf.wacc,idx) for idx in np.arange(1,len(dcf.statement.forecast_dates)+1)])
        pv_ufcf: pd.Series = pd.Series(np.multiply(ufcf,discount),index=dcf.statement.forecast_dates)
        combined: pd.DataFrame = pd.concat([ufcf,pv_ufcf],axis=1)
        combined.columns = ["UFCF","PV of UFCF"]
        combined["period"] = combined.index
        combined["year"] = [str(date.year) for date in combined.period]
        combined["year-q"] = [f"{date.year}Q{date.quarter}" for date in combined.period]
        return combined.reset_index().sort_values("period")
