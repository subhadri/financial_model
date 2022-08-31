from finModel.statements.forecast import is_forecast_avg_growth, bs_forecast_avg_growth
from finModel.statements.income import IncomeStatement
from finModel.statements.balance import BalanceSheet
from finModel.statements.cashflow import CashFlowStatement
from dataclasses import dataclass, field
from typing import List, Union
import pandas as pd
import numpy as np

@dataclass
class FinancialStatement:
    company: str
    actual_dates: List[str]
    forecast_dates: List[str]
    income: IncomeStatement = field(init=False)
    balance: BalanceSheet = field(init=False)
    cash: CashFlowStatement = field(init=False)

    def __init__(self, comp:str, a_date:List[str], f_date:List[str], inc:IncomeStatement, bs:BalanceSheet):
        self.company = comp
        self.actual_dates = a_date
        self.forecast_dates = f_date
        f_inc = is_forecast_avg_growth(inc,f_date)
        f_bs = bs_forecast_avg_growth(bs,inc,f_inc,f_date)
        self.income = inc.attach(f_inc)
        self.balance = bs.attach(f_bs)
        self.cash = CashFlowStatement(self.income,self.balance)


def report_table(d:Union[IncomeStatement,BalanceSheet,CashFlowStatement],f_date:List[str]) -> pd.DataFrame:

    data: pd.DataFrame = d.to_pandas_df()
    order: pd.DataFrame = pd.DataFrame({'component': data.columns.values})
    data['year'] = pd.DatetimeIndex(data.index).year
    data['period_label'] = ['F' if date in pd.to_datetime(f_date) else 'A' for date in data.index]
    data['index'] = [f"{round(data.year[idx],0)}{data.period_label[idx]}" for idx in data.index]
    melted_data: pd.DataFrame = data.melt(id_vars=['year','period_label','index'],var_name='component')
    pivoted_data: pd.DataFrame = melted_data.pivot(index='component',columns='index',values='value')
    out: pd.DataFrame = pd.merge(left=order,right=pivoted_data,how="left",on="component")

    return out
