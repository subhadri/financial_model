'''
PURPOSE: Houses the ratios and datasets we would be using for plotting purposes
'''

from finModel.statements.main import FinancialStatement
from finModel.analysis.dcf_valuation import DCFValuation
from finModel.utils.transform import days_outstanding
from dataclasses import dataclass, field
import pandas as pd
import numpy as np


@dataclass
class VizData:
    '''
    Prepare and store the datasets to be used for visualisation.
    '''
    dcf: DCFValuation
    ebitda_rev_ratio: pd.DataFrame = field(init=False)
    ufcf_trend: pd.DataFrame = field(init=False)
    ebitda_components: pd.DataFrame = field(init=False)
    working_capital: pd.DataFrame = field(init=False)
    dcf_simulations: pd.DataFrame = field(init=False)

    def __init__(self,dcf:DCFValuation):
        self.dcf = dcf
        self.ebitda_rev_ratio = VizData.get_ebitda_revenue_ratio(self.dcf.statement)
        self.ufcf_trend = VizData.get_ufcf_trend(self.dcf)
        self.ebitda_components = VizData.decompose_ebitda(self.dcf)
        self.working_capital = VizData.get_working_capital(self.dcf)

    @staticmethod
    def get_ebitda_revenue_ratio(fin:FinancialStatement) -> pd.DataFrame:
        '''
        Compute EBITDA as % of sales revenue
        '''
        ebitda: pd.Series = fin.income.ebitda
        revenue: pd.Series = fin.income.revenue.sales
        ratio: pd.Series = (ebitda/revenue)
        combined: pd.DataFrame = pd.concat([revenue,ebitda,ratio],axis=1)
        combined.columns = ["Revenues","EBITDA","EBITDA%"]
        combined["period"] = combined.index
        combined["year"] = [date.year for date in combined.period]
        combined["year-q"] = [f"{date.year}Q{date.quarter}" for date in combined.period]
        combined["type"] = ["Actual" if date in fin.actual_dates else "Forecast" for date in combined["period"].values]

        return combined.reset_index().sort_values("period")

    @staticmethod
    def get_ufcf_trend(dcf: DCFValuation) -> pd.DataFrame:
        '''
        Extract unlevered cashflow forecasts and discount using WACC
        '''
        ufcf: pd.Series = dcf.statement.cash.ufcf[dcf.statement.forecast_dates]
        discount: np.ndarray = np.array([1/np.power(1+dcf.wacc,idx) for idx in np.arange(1,len(dcf.statement.forecast_dates)+1)])
        pv_ufcf: pd.Series = pd.Series(np.multiply(ufcf,discount),index=dcf.statement.forecast_dates)
        combined: pd.DataFrame = pd.concat([ufcf,pv_ufcf],axis=1)
        combined.columns = ["UFCF","PV of UFCF"]
        combined["period"] = combined.index
        combined["year"] = [str(date.year) for date in combined.period]
        combined["year-q"] = [f"{date.year}Q{date.quarter}" for date in combined.period]

        return combined.reset_index().sort_values("period")

    @staticmethod
    def decompose_ebitda(dcf: DCFValuation) -> pd.DataFrame:
        '''
        Show the decomposition of EBITDA into change in total revenues, COGS and OPEX
        '''
        delta_ebitda: pd.Series = dcf.statement.income.ebitda.diff()
        delta_rev: pd.Series = dcf.statement.income.revenue.tot_revenue.diff()
        delta_cogs: pd.Series = dcf.statement.income.cogs.cogs.diff()
        delta_opex: pd.Series = dcf.statement.income.opex.opex.diff()
        combined: pd.DataFrame = pd.concat([delta_ebitda,delta_rev,delta_cogs,delta_opex],axis=1).dropna()
        combined.columns = ["Delta EBITDA","Delta revenues","Delta COGS","Delta OPEX"]
        combined["period"] = combined.index
        combined["year"] = [str(date.year) for date in combined.period]
        combined["year-q"] = [f"{date.year}Q{date.quarter}" for date in combined.period]

        return combined

    @staticmethod
    def get_working_capital(dcf: DCFValuation) -> pd.DataFrame:
        '''
        Get DSO, DIO and DPO and the working capital
        '''
        dso: np.ndarray = days_outstanding(dcf.statement.balance.trade_receivable,dcf.statement.income.revenue.sales)
        dio: np.ndarray = -days_outstanding(dcf.statement.balance.inventory,dcf.statement.income.cogs.cogs)
        dpo: np.ndarray = -days_outstanding(dcf.statement.balance.trade_payable,dcf.statement.income.cogs.cogs)
        combined: pd.DataFrame = pd.DataFrame({"DSO":dso,"DIO":dio,"DPO":dpo},index=dcf.statement.income.revenue.sales.index)
        combined: pd.DataFrame = pd.concat([combined,pd.Series(dcf.statement.balance.trade_receivable,name="Trade receivables"),
                                            pd.Series(dcf.statement.balance.inventory,name="Inventory"),
                                            -pd.Series(dcf.statement.balance.trade_payable,name="Trade payables")], axis=1)
        combined["Working capital"] = combined["Trade receivables"] + combined["Inventory"] + combined["Trade payables"]
        combined["period"] = combined.index
        combined["year"] = [str(date.year) for date in combined.period]
        combined["year-q"] = [f"{date.year}Q{date.quarter}" for date in combined.period]
#        combined = combined.melt(id_vars="year",value_vars=["DSO","DIO","DPO"],var_name="metric",value_name="days")
        return combined