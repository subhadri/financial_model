from finModel.statements.income import IncomeStatement
from finModel.statements.balance import BalanceSheet
from dataclasses import dataclass, field
from typing import List
import pandas as pd


@dataclass
class OtherInvestmentMovement:
    other_asset: pd.Series
    other_liability: pd.Series
    intangible_asset: pd.Series
    financial_asset: pd.Series

    def __init__(self, bs:BalanceSheet):
        self.other_asset = -bs.other_asset.diff()
        self.other_liability = bs.other_liability.total.diff()
        self.intangible_asset = -bs.intangible_asset.diff()
        self.financial_asset = -bs.financial_asset.diff()

    def attach(self,other:"OtherInvestmentMovement") -> "OtherInvestmentMovement":
        return OtherInvestmentMovement(other_asset=pd.concat([self.other_asset,other.other_asset]).sort_index(),
            other_liability=pd.concat([self.other_liability,other.other_liability]).sort_index(),
            intangible_asset=pd.concat([self.intangible_asset,other.intangible_asset]).sort_index()
        )


@dataclass
class CashFlowStatement:
    ebit: pd.Series
    op_tax_rate: pd.Series
    d_and_a: pd.Series
    inventory_movement: pd.Series
    trade_receivable_movement: pd.Series
    trade_payable_movement: pd.Series
    extraordinary_item: pd.Series
    interest_expense: pd.Series
    delta_fin_liability: pd.Series
    ppe_movement: pd.Series
    nopat: pd.Series
    operating_tax: pd.Series
    gross_cf: pd.Series
    investment_in_working_capital: pd.Series
    other_investment: pd.Series
    investment_in_other_asset_and_liability: pd.Series
    capex_movement: pd.Series
    ufcf: pd.Series
    delta_taxes_vs_optax: pd.Series
    delta_equity_inc_dividend: pd.Series
    net_cashflow: pd.Series

    def __init__(self, inc:IncomeStatement, bs:BalanceSheet):
        self.ebit = inc.ebit
        self.op_tax_rate = inc.tax_rate
        self.operating_tax = self.op_tax_rate * self.ebit
        self.nopat = self.ebit + self.operating_tax
        self.d_and_a = -inc.d_and_a
        self.gross_cf = self.nopat + self.d_and_a
        self.inventory_movement = -bs.inventory.diff()
        self.trade_receivable_movement = -bs.trade_receivable.diff()
        self.trade_payable_movement = bs.trade_payable.diff()
        self.investment_in_working_capital = self.inventory_movement + self.trade_payable_movement + \
                                             self.trade_receivable_movement
        self.investment_in_other_asset_and_liability = OtherInvestmentMovement(bs).other_asset + \
                                                       OtherInvestmentMovement(bs).other_liability
        self.other_investment = OtherInvestmentMovement(bs).intangible_asset + \
                                OtherInvestmentMovement(bs).financial_asset
        self.ppe_movement = -bs.ppe.diff()
        self.capex_movement = self.ppe_movement - self.d_and_a
        self.extraordinary_item = inc.extraordinary_income
        self.ufcf = self.gross_cf + self.investment_in_working_capital + self.investment_in_other_asset_and_liability + \
                    self.capex_movement + self.other_investment + self.extraordinary_item
        self.interest_expense = inc.int_expense
        self.delta_taxes_vs_optax = inc.tax - self.operating_tax
        self.delta_fin_liability = bs.financial_liability.total.diff()
        self.delta_equity_inc_dividend = bs.shareholder_equity.total_equity.diff() - inc.net_income
        self.net_cashflow = self.ufcf + self.interest_expense + self.delta_taxes_vs_optax + self.delta_fin_liability + \
                            self.delta_equity_inc_dividend

    def to_pandas_df(self) -> pd.DataFrame:
        series_list: List[pd.Series] = [pd.Series(self.ebit,name="EBIT"),
                                        pd.Series(self.operating_tax,name="Operating taxes"),
                                        pd.Series(self.op_tax_rate,name="Operating tax rate"),
                                        pd.Series(self.nopat,name="NOPAT"),
                                        pd.Series(self.d_and_a,name="Add-back D&A"),
                                        pd.Series(self.gross_cf,name="Gross Cash Flow"),
                                        pd.Series(self.inventory_movement,name="Inventory (movement)"),
                                        pd.Series(self.trade_receivable_movement,name="Trade receivables (movement)"),
                                        pd.Series(self.trade_payable_movement,name="Trade payable (movement)"),
                                        pd.Series(self.investment_in_working_capital,name="Net change in working capital"),
                                        pd.Series(self.investment_in_other_asset_and_liability,
                                                  name="Net change in other asset/liabilities"),
                                        pd.Series(self.capex_movement,name="Capex (movement)"),
                                        pd.Series(self.other_investment,name="Other investment (movement)"),
                                        pd.Series(self.extraordinary_item,name="Extra-ordinary items"),
                                        pd.Series(self.ufcf,name="Unlevered Free Cashflows"),
                                        pd.Series(self.interest_expense,name="Interest expenses"),
                                        pd.Series(self.delta_taxes_vs_optax,name="Delta Taxes vs. Operating taxes"),
                                        pd.Series(self.delta_fin_liability,name="Delta Financial liabilities"),
                                        pd.Series(self.delta_equity_inc_dividend,name="Delta Equity (inc. dividends)"),
                                        pd.Series(self.net_cashflow,name="Net Cashflow")]
        return pd.concat(series_list,axis=1)




