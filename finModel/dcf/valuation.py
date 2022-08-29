"""
PURPOSE: This module performs the direct cashflows valuation and holds associated analysis
"""
from finModel.statements.main import FinancialStatement
from dataclasses import dataclass, field
from typing import List
import pandas as pd
import numpy as np


def calc_cost_of_equity(rf:float,beta:float,market_risk:float) -> float:
    '''
    Calculates cost-of-equity using CAPM model
    :param rf: risk-free rate (generally 10Y govt. bond yields)
    :param beta: stock sensitivity (provided by Yahoo finance)
    :param market_risk: market index returns
    :return: cost of equity
    '''
    ke: float = rf + beta * (market_risk - rf)
    return ke


def calc_cost_of_debt(fs: FinancialStatement) -> pd.Series:
    '''
    Calculates cost of debt as the ratio of interest expenses (from income statement)
    to financial liabilities (from balance sheet).
    :param fs: Financial statements
    :return: cost of debt for each period
    '''
    int_exp: pd.Series = FinancialStatement.income.int_expense
    fin_liab: pd.Series = FinancialStatement.balance.financial_liability.total
    kd: pd.Series = int_exp/fin_liab
    return kd


def calc_wacc(D:float,E:float,t:float,kd:float,ke:float) -> float:
    '''
    Calculates weighted average cost of capital
    :param D: total debt
    :param E: total equity
    :param t: tax-rate
    :param kd: cost of debt
    :param ke: cost of equity
    '''
    wacc: float = (D/(D+E))*(1-t)*kd + (E/(D+E))*ke
    return wacc

@dataclass
class DCFValuation:
    wacc: float
    g: float
    pv_ufcf: float = field(init=False)
    pv_ufcf_shr: float = field(init=False)
    cont_val: float = field(init=False)
    pv_cont_val: float = field(init=False)
    pv_cont_val_shr: float = field(init=False)
    ent_val: float = field(init=False)
    tot_fin_liab: float = field(init=False)
    cash: float = field(init=False)
    equity: float = field(init=False)

    def __init__(self,wacc:float,lt_growth:float,a_date:List[str],f_date:List[str],fin:FinancialStatement):
        self.wacc = wacc
        self.g = lt_growth
        ufcf: pd.Series = fin.cash.ufcf[f_date]
        discount: np.ndarray = np.ndarray([1/np.power(1+wacc,idx) for idx in np.arange(1,len(ufcf)+1)])
        self.pv_ufcf = np.multiply(ufcf,discount).sum()
        self.cont_val = self.pv_ufcf * (1+self.g) / (self.wacc-self.g)
        self.pv_cont_val = self.cont_val * discount[-1]
        self.ent_val = self.pv_ufcf + self.pv_cont_val
        self.tot_fin_liab = - fin.balance.financial_liability.total[a_date[-1]]
        self.cash = fin.balance.cash[a_date[-1]]
        self.equity = self.ent_val + self.tot_fin_liab + self.cash
        self.pv_ufcf_shr = self.pv_ufcf/self.ent_val
        self.pv_cont_val_shr = self.pv_cont_val/self.ent_val

    def __str__(self):
        out: List[pd.Series] = [
            pd.Series(f"{round(self.wacc*100,0)}%",index="WACC"),
            pd.Series(f"{round(self.g*100,0)}%",index="long-term growth"),
            pd.Series(self.pv_ufcf,index="PV of Cash flows"),
            pd.Series(self.pv_ufcf_shr,index="PV of Cash flows (%)"),
            pd.Series(self.cont_val,index="Continuing value"),
            pd.Series(self.pv_cont_val,index="PV of Continuing value"),
            pd.Series(self.pv_cont_val_shr,index="PV of Continuing value (%)"),
            pd.Series(self.ent_val,index="Enterprise value"),
            pd.Series(self.tot_fin_liab,index="(-) Financial liabilities"),
            pd.Series(self.cash,index="(+) Cash"),
            pd.Series(self.equity,index="Equity value")]

        return pd.concat(out,axis=0)






