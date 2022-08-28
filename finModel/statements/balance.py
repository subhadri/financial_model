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

    def attach(self,other:"OtherLiab") -> "OtherLiab":
        return OtherLiab(
            other_liability=pd.concat([self.other_liability,other.other_liability]).sort_index(),
            deferred_taxes=pd.concat([self.deferred_taxes,other.deferred_taxes]).sort_index(),
            provision_for_retirement_benefit=pd.concat([self.provision_for_retirement_benefit,
                                                        other.provision_for_retirement_benefit]).sort_index()
        )


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

    def attach(self,other:"FinLiab") -> "FinLiab":
        return FinLiab(
            bank_borrowing=pd.concat([self.bank_borrowing,other.bank_borrowing]).sort_index(),
            other_financial_liability=pd.concat([self.other_financial_liability,
                                                 other.other_financial_liability]).sort_index())

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

    def attach(self,other:"Equity") -> "Equity":
        return Equity(share_capital=pd.concat([self.share_capital,other.share_capital]).sort_index(),
                      reserve=pd.concat([self.reserve,other.reserve]).sort_index(),
                      retained_earning=pd.concat([self.retained_earning,other.retained_earning]).sort_index(),
                      net_annual_profit=pd.concat([self.net_annual_profit,other.net_annual_profit]).sort_index())


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
    trade_payable: pd.Series
    shareholder_equity: Equity
    cash: pd.Series = field(init=False)
    total_asset: pd.Series = field(init=False)
    total_liability_and_equity: pd.Series = field(init=False)

    def __post_init__(self):
        asset_minus_cash = self.intangible_asset + self.ppe + self.financial_asset + self.inventory + \
                           self.trade_receivable + self.other_asset
        self.total_liability_and_equity = self.trade_payable + self.other_liability.total + self.financial_liability.total + \
                                          self.shareholder_equity.total_equity
        self.cash = self.total_liability_and_equity - asset_minus_cash
        self.total_asset = asset_minus_cash + self.cash

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

    def attach(self,other:"BalanceSheet") -> "BalanceSheet":
        return BalanceSheet(
            intangible_asset=pd.concat([self.intangible_asset,other.intangible_asset]).sort_index(),
            ppe=pd.concat([self.ppe,other.ppe]).sort_index(),
            financial_asset=pd.concat([self.financial_asset,other.financial_asset]).sort_index(),
            financial_liability=self.financial_liability.attach(other.financial_liability),
            inventory=pd.concat([self.inventory,other.inventory]).sort_index(),
            trade_receivable=pd.concat([self.trade_receivable,other.trade_receivable]).sort_index(),
            other_asset=pd.concat([self.other_asset,other.other_asset]).sort_index(),
            other_liability=self.other_liability.attach(other.other_liability),
            trade_payable=pd.concat([self.trade_payable,other.trade_payable]).sort_index(),
            shareholder_equity=self.shareholder_equity.attach(other.shareholder_equity)
        )