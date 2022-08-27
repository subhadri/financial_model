from finModel.utils.transform import const_growth, linear_trend, const_pandas_series, mean_g, const_share
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
import numpy as np

@dataclass
class Revenue:
    '''
    Stores the revenue from sales and other sources and calculates the total revenue
    '''
    revenue: pd.Series
    other_revenue: pd.Series
    tot_revenue: pd.Series = field(init=False)

    def __post_init__(self):
        self.tot_revenue = self.revenue + self.other_revenue


@dataclass
class COGS:
    '''
    Cost of goods sold includes raw materials cost and direct costs
    '''
    raw_material: pd.Series
    direct_cost: pd.Series
    cogs: pd.Series = field(init=False)

    def __post_init__(self):
        self.cogs = self.raw_material + self.direct_cost


@dataclass
class OperatingExpense:
    '''
    Operating expenses include cost for services, lease costs and other operating expenses
    '''
    cost_for_services: pd.Series
    lease_cost: pd.Series
    other: pd.Series
    opex: pd.Series = field(init=False)

    def __post_init__(self):
        self.opex = self.cost_for_services + self.lease_cost + self.other


@dataclass
class IncomeStatement:
    '''
    Inputs/calculates all the reported components of an Income statement and stores as a pandas DataFrame
    '''
    revenue: Revenue
    cogs: COGS
    opex: OperatingExpense
    d_and_a: pd.Series
    int_expense: pd.Series
    extraordinary_income: pd.Series
    tax: pd.Series
    gross_margin: pd.Series = field(init=False)
    ebitda: pd.Series = field(init=False)
    ebit: pd.Series = field(init=False)
    ebt: pd.Series = field(init=False)
    tax_rate: Optional[pd.Series] = field(init=False)
    net_income: pd.Series = field(init=False)

    def __post_init__(self):
        self.gross_margin = self.revenue.tot_revenue + self.cogs.cogs
        self.ebitda = self.gross_margin + self.opex.opex
        self.ebit = self.ebitda + self.d_and_a
        self.ebt = self.ebit + self.int_expense + self.extraordinary_income
        self.tax_rate = self.tax/self.ebt
        self.net_income = self.ebt + self.tax

    def to_pandas_df(self) -> pd.DataFrame:
        series_list: List[pd.Series] = [pd.Series(self.revenue.revenue,name="Revenues"),
                                        pd.Series(self.revenue.other_revenue,name="Other revenues"),
                                        pd.Series(self.revenue.tot_revenue,name="Total revenues"),
                                        pd.Series(self.cogs.cogs,name="Cost of goods sold"),
                                        pd.Series(self.gross_margin,name="Gross margin"),
                                        pd.Series(self.opex.opex,name="Operating expenses"),
                                        pd.Series(self.ebitda,name="EBITDA"),
                                        pd.Series(self.d_and_a,name="D&A"),
                                        pd.Series(self.ebit,name="EBIT"),
                                        pd.Series(self.int_expense,name="Interest expense"),
                                        pd.Series(self.extraordinary_income,name="Extraordinary income"),
                                        pd.Series(self.ebt,name="EBT"),
                                        pd.Series(self.tax_rate,name="Tax rate"),
                                        pd.Series(self.tax,name="Taxes"),
                                        pd.Series(self.net_income,name="Net income")]
        return pd.concat(series_list,axis=1)


def ForecastedIncomeStatement(inc:IncomeStatement,f_date:List[str]) -> IncomeStatement:
    '''
    Performs the forecast for each date using assumptions for each component as defined here.
    :param inc: actuals instance
    :param f_date: dates to be forecasted
    :return: forecasted instance
    '''
    f_revenue: pd.Series = const_growth(inc.revenue.revenue,mean_g(inc.revenue.revenue),f_date)
    forecasted = IncomeStatement(
        revenue=Revenue(revenue=f_revenue, other_revenue=const_growth(inc.revenue.other_revenue,0.0,f_date)),
        cogs=COGS(raw_material=const_pandas_series(inc.cogs.raw_material.name,f_date),
                  direct_cost=const_share(f_revenue,np.nanmean(inc.cogs.cogs/inc.revenue.revenue),f_date)),
        opex=OperatingExpense(
            cost_for_services=const_share(f_revenue,np.nanmean(inc.opex.opex/inc.revenue.revenue),f_date),
            lease_cost=const_pandas_series(inc.opex.lease_cost.name, f_date),
            other=const_pandas_series(inc.opex.other.name, f_date)),
        d_and_a=const_share(f_revenue,np.nanmean(inc.d_and_a/inc.revenue.revenue),f_date),
        int_expense=const_growth(inc.int_expense,0.0,f_date),
        extraordinary_income=const_share(f_revenue,np.array(0.0),f_date),
        tax=const_pandas_series(inc.tax.name,f_date))
    forecasted.tax_rate = const_pandas_series(inc.tax_rate.name,f_date,np.nanmean(inc.tax/inc.ebt))
    forecasted.tax = forecasted.tax_rate * forecasted.ebt
    forecasted.net_income = forecasted.ebt + forecasted.tax
    return forecasted

