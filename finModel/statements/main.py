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
    actual_dates: np.ndarray
    forecast_dates: np.ndarray
    income: IncomeStatement = field(init=False)
    balance: BalanceSheet = field(init=False)
    cash: CashFlowStatement = field(init=False)

    def __init__(self, comp:str, a_date:List[str], f_date:List[str], inc:IncomeStatement, bs:BalanceSheet):
        self.company = comp
        self.actual_dates = pd.to_datetime(a_date).values
        self.forecast_dates = pd.to_datetime(f_date).values
        f_inc = is_forecast_avg_growth(inc,f_date)
        f_bs = bs_forecast_avg_growth(bs,inc,f_inc,f_date)
        self.income = inc.attach(f_inc)
        self.balance = bs.attach(f_bs)
        self.cash = CashFlowStatement(self.income,self.balance)