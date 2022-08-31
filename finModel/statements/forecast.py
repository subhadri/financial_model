"""
PURPOSE: Houses all the methodologies that are used to perform forecasts of the various financial statements.
"""

from finModel.utils.transform import const_growth, days_outstanding, const_pandas_series
from finModel.utils.transform import add_movement, mean_g, const_share
from finModel.statements.income import IncomeStatement, Revenue, OperatingExpense, COGS
from finModel.statements.balance import BalanceSheet, FinLiab, OtherLiab, Equity
from typing import List
import pandas as pd
import numpy as np


def is_forecast_avg_growth(inc:IncomeStatement, f_date:np.ndarray) -> IncomeStatement:
    '''
    Performs the forecast for each date using historical period-on-period historical growth and % shares of revenue.

    The rules are defined as follows:

        1. Revenue (sales and services) = avg. historical growth to continue
        2. Revenue (other) = set to previous value
        3. COGS = avg % of revenues
        4. Opex = avg % of revenues
        5. D&A = avg % of revenues
        6. Interest expense = set to previous value
        7. Extraordinary item = assume 0
        8. tax-rate = avg % of EBT

    :param inc: income statement (actuals)
    :param f_date: dates to be forecasted
    :return: income statement (forecasted)
    '''
    # Forecast the revenues first; as they will be used to compute % shares when initialising the forecast instance
    f_revenue: pd.Series = const_growth(inc.revenue.sales, mean_g(inc.revenue.sales), f_date)
    # Initialise the forecasted instance
    forecasted = IncomeStatement(
        revenue=Revenue(sales=f_revenue, other_revenue=const_growth(inc.revenue.other_revenue, 0.0, f_date)),
        cogs=COGS(
            raw_material=const_pandas_series(inc.cogs.cogs.name,f_date),
            direct_cost=const_share(f_revenue, np.nanmean(inc.cogs.cogs / inc.revenue.sales), f_date)),
        opex=OperatingExpense(
            cost_for_services=const_share(f_revenue, np.nanmean(inc.opex.opex / inc.revenue.sales), f_date),
            lease_cost=const_pandas_series(inc.opex.lease_cost.name,f_date),
            other=const_pandas_series(inc.opex.other,f_date)),
        d_and_a=const_share(f_revenue, np.nanmean(inc.d_and_a / inc.revenue.sales), f_date),
        int_expense=const_growth(inc.int_expense,0.0,f_date),
        extraordinary_income=const_share(f_revenue,np.array(0.0),f_date),
        tax=const_pandas_series(inc.tax.name,f_date))
    # By default, IncomeStatement computes tax-rate from tax and EBT; for now there is no provision for inputting
    # tax-rates in this class. Temporary hack is to manually override tax-rate, tax and net-income (being a function of
    # tax). Need to think of a better approach in future.
    forecasted.tax_rate = const_pandas_series(inc.tax_rate.name,f_date,np.nanmean(inc.tax/inc.ebt))
    forecasted.tax = forecasted.tax_rate * forecasted.ebt
    forecasted.net_income = forecasted.ebt + forecasted.tax

    return forecasted


def bs_forecast_avg_growth(bs: BalanceSheet, a_inc: IncomeStatement, f_inc: IncomeStatement,
                           f_date: np.ndarray) -> "BalanceSheet":
    '''
    Forecast for the dates provided using historical growths as % of revenues.

    The following assumptions apply here:

        1. Intangible asset -> set to previous value
        2. PP&E -> avg. % of revenues
        3. Financial assets/liabilities -> set to previous value
        4. Inventory -> days outstanding as % of revenues
        5. Trade receivables/payables -> days outstanding as % of revenues
        6. Other assets/liabilities -> avg. % of revenues
        7. Shareholder's equity -> Beginning equity + net income

    :param bs: balance sheet (actuals)
    :param a_inc: income statement (actuals)
    :param f_inc: income statement with forecasts
    :param f_date: dates to forecast on
    :return: balance sheet with forecasts
    '''
    f_bs = BalanceSheet(
        intangible_asset=const_growth(bs.intangible_asset,0.0,f_date),
        ppe=const_share(f_inc.revenue.sales, np.nanmean(bs.ppe / a_inc.revenue.sales), f_date),
        financial_asset=const_growth(bs.financial_asset,0.0,f_date),
        financial_liability=FinLiab(
            bank_borrowing=const_growth(bs.financial_liability.bank_borrowing,0.0,f_date),
            other_financial_liability=const_growth(bs.financial_liability.other_financial_liability,0.0,f_date)),
        inventory=(const_share(
            f_inc.cogs.cogs,np.mean(days_outstanding(bs.inventory,a_inc.cogs.cogs,360)),f_date))/360,
        trade_receivable=(const_share(
            f_inc.revenue.sales,np.mean(days_outstanding(bs.trade_receivable, a_inc.revenue.sales, 360)),f_date)) / 360,
        other_asset=const_share(f_inc.revenue.sales, np.nanmean(bs.other_asset / a_inc.revenue.sales), f_date),
        other_liability=OtherLiab(
            other_liability=const_share(
                f_inc.revenue.sales,np.nanmean(bs.other_liability.other_liability / a_inc.revenue.sales),f_date),
            provision_for_retirement_benefit=const_share(
                f_inc.revenue.sales,np.nanmean(bs.other_liability.provision_for_retirement_benefit / a_inc.revenue.sales),
                f_date),
            deferred_taxes=const_share(
                f_inc.revenue.sales,np.nanmean(bs.other_liability.deferred_taxes / a_inc.revenue.sales),f_date)),
        trade_payable=(const_share(
            f_inc.cogs.cogs,np.mean(days_outstanding(bs.trade_payable,a_inc.cogs.cogs,360)),f_date))/360,
        shareholder_equity=Equity(
            share_capital=const_pandas_series(bs.shareholder_equity.share_capital.name,f_date),
            reserve=const_pandas_series(bs.shareholder_equity.reserve.name,f_date),
            retained_earning=const_pandas_series(bs.shareholder_equity.retained_earning.name,f_date),
            net_annual_profit=add_movement(bs.shareholder_equity.total_equity,f_inc.net_income))
    )
    # Storing the difference in total assets and liabilities

    return f_bs