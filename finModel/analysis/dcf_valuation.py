"""
PURPOSE: This module performs the direct cashflows valuation and holds associated analysis
"""
from finModel.statements.main import FinancialStatement
from dataclasses import dataclass, field
from typing import List, Dict
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
    statement: FinancialStatement
    pv_ufcf: float = field(init=False)
    pv_ufcf_shr: float = field(init=False)
    cont_val: float = field(init=False)
    pv_cont_val: float = field(init=False)
    pv_cont_val_shr: float = field(init=False)
    ent_val: float = field(init=False)
    tot_fin_liab: float = field(init=False)
    cash: float = field(init=False)
    equity: float = field(init=False)

    def __init__(self,wacc:float,lt_growth:float,fin:FinancialStatement):
        self.wacc = wacc
        self.g = lt_growth
        self.statement = fin
        ufcf: pd.Series = fin.cash.ufcf[fin.forecast_dates]
        discount: np.ndarray = np.array([1/np.power(1+wacc,idx) for idx in np.arange(1,len(fin.forecast_dates)+1)])
        self.pv_ufcf = np.multiply(ufcf,discount).sum()
        self.cont_val = ufcf[-1] * (1+self.g) / (self.wacc-self.g)
        self.pv_cont_val = self.cont_val * discount[-1]
        self.ent_val = self.pv_ufcf + self.pv_cont_val
        self.tot_fin_liab = - fin.balance.financial_liability.total[fin.actual_dates[-1]]
        self.cash = fin.balance.cash[fin.actual_dates[-1]]
        self.equity = self.ent_val + self.tot_fin_liab + self.cash
        self.pv_ufcf_shr = self.pv_ufcf/self.ent_val
        self.pv_cont_val_shr = self.pv_cont_val/self.ent_val

    def to_pandas_df(self) -> pd.DataFrame:
        res_dict: Dict[str,float] = {
            "WACC": self.wacc,
            "long-term growth": self.g,
            "PV of Cash flows": self.pv_ufcf,
            "PV of Cash flows (%)": self.pv_ufcf_shr,
            "Continuing value": self.cont_val,
            "PV of Continuing value": self.pv_cont_val,
            "PV of Continuing value (%)": self.pv_cont_val_shr,
            "Enterprise value": self.ent_val,
            "(-) Financial liabilities": self.tot_fin_liab,
            "(+) Cash": self.cash,
            "Equity value": self.equity,
        }
        out: pd.DataFrame = pd.DataFrame({
            "metric": [k for k,v in res_dict.items()],
            "": [v for k,v in res_dict.items()]
        })

        return out

    def simulate_enterprise_val(self, wacc: List[float] = None, lt_growth: List[float] = None) -> pd.DataFrame:
        '''
        Generate enterprise values for each various WACC and long-term growth rates
        '''
        if wacc is None:
            wacc: List[float] = [self.wacc + v for v in [-0.01,0,0.01,0.02]]
        if lt_growth is None:
            lt_growth: List[float] = [self.g + v for v in [-0.01,0,0.01,0.02]]

        result_set = []
        for w in wacc:
            for g in lt_growth:
                d: DCFValuation = DCFValuation(wacc=w,lt_growth=g,fin=self.statement)
                result_set.append(d)

        simulated: pd.DataFrame = pd.DataFrame({
            "wacc": [dcf.wacc for dcf in result_set],
            "long-term growth": [dcf.g for dcf in result_set],
            "enterpise value": [dcf.ent_val for dcf in result_set],
        })

        return simulated