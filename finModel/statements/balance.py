from dataclasses import dataclass, field
from typing import List
import pandas as pd


@dataclass
class OtherLiab:
    '''
    Liabilities coming from non-financial sources, deferred taxes and provisions for retirement benefits
    '''
    other_liability: pd.Series
    deferred_taxes: pd.Series
    provision_for_retirement_benefit: pd.Series
    total: pd.Series = field(init=False)

    def __post_init__(self):
        self.total = self.other_liability + self.deferred_taxes + self.provision_for_retirement_benefit


@dataclass
class FinLiab:
    '''
    Financial liabilities include bank borrowings and other liabilities (financial)
    '''
    bank_borrowing: pd.Series
    other_financial_liability: pd.Series
    total: pd.Series = field(init=False)

    def __post_init__(self):
        self.total = self.bank_borrowing + self.other_financial_liability


@dataclass
class Equity:
    '''
    Shareholder's equity include share capital, annual reserves, retained earnings and yearly profit/losses
    '''
    share_capital: pd.Series
    reserve: pd.Series
    retained_earning: pd.Series
    net_annual_profit: pd.Series
    total_equity: pd.Series = field(init=False)

    def __post_init__(self):
        self.total_equity = self.share_capital + self.reserve + self.retained_earning + self.net_annual_profit


@dataclass
class BalanceSheet:
    '''
    Inputs/calculates all the reported components of a Balance sheet and stores as a pandas DataFrame
    '''
    intangible_asset: pd.Series
    ppe: pd.Series
    financial_asset: pd.Series
    financial_liability: FinLiab
    inventory: pd.Series
    trade_receivable: pd.Series
    other_asset: pd.Series
    other_liability: OtherLiab
    cash: pd.Series
    trade_payable: pd.Series
    shareholder_equity: Equity
    total_asset: pd.Series = field(init=False)
    total_liability_and_equity: pd.Series = field(init=False)

    def __post_init__(self):
        self.total_asset = self.intangible_asset + self.ppe + self.financial_asset + self.inventory + \
                           self.trade_receivable + self.other_asset + self.cash
        self.total_liability_and_equity = self.trade_payable + self.other_liability.total + self.financial_liability.total + \
                                          self.shareholder_equity.total_equity

    def to_pandas_df(self) -> pd.DataFrame:
        series_list: List[pd.Series] = [pd.Series(self.intangible_asset,name="Intangible assets"),
                                        pd.Series(self.ppe,name="PP&E"),
                                        pd.Series(self.financial_asset,name="Financial assets"),
                                        pd.Series(self.inventory,name="Inventory"),
                                        pd.Series(self.trade_receivable,name="Trade receivable"),
                                        pd.Series(self.other_asset,name="Other assets"),
                                        pd.Series(self.cash,name="Cash and equivalents"),
                                        pd.Series(self.total_asset,name="Total Assets"),
                                        pd.Series(self.trade_payable,name="Trade payable"),
                                        pd.Series(self.trade_payable,name="Trade payable"),
                                        pd.Series(self.other_liability.total,name="Other liabilities"),
                                        pd.Series(self.financial_liability.total,name="Financial liabilities"),
                                        pd.Series(self.shareholder_equity.total_equity,name="Shareholder's equity"),
                                        pd.Series(self.total_liability_and_equity,name="Total Liabilities & Equities")]
        return pd.concat(series_list,axis=1)
