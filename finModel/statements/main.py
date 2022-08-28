from finModel.statements.forecast import is_forecast_avg_growth, bs_forecast_avg_growth
from finModel.statements.income import IncomeStatement
from finModel.statements.balance import BalanceSheet
from finModel.statements.cashflow import CashFlowStatement
from dataclasses import dataclass, field
from typing import Union, List

@dataclass
class FinancialStatement:
    company: str
    income: IncomeStatement = field(init=False)
    balance: BalanceSheet = field(init=False)
    cash: CashFlowStatement = field(init=False)

    def __init__(self, comp:str, f_date:List[str], inc:IncomeStatement, bs:BalanceSheet):
        self.company = comp
        f_inc = is_forecast_avg_growth(inc,f_date)
        f_bs = bs_forecast_avg_growth(bs,inc,f_inc,f_date)
        self.income = inc.attach(f_inc)
        self.balance = bs.attach(f_bs)
        self.cash = CashFlowStatement(self.income,self.balance)