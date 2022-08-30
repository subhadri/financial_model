from finModel.statements.income import Revenue, COGS, OperatingExpense, IncomeStatement
from finModel.statements.balance import OtherLiab, FinLiab, Equity, BalanceSheet
from typing import List
import pandas as pd
import numpy as np

# To be inputted by user

file_loc = 'C:/Users/ssmal/learning/Projects/financial modeling/data/cheesco-model.xlsm'
actual_dates = ['2016-12-31','2017-12-31','2018-12-31']
forecast_dates = ['2019-12-31','2020-12-31','2021-12-31','2022-12-31','2023-12-31']

def source_income(file_loc:str,actual_dates:List[str]) -> IncomeStatement:

    data = pd.read_excel(file_loc,sheet_name='P&L source',skiprows=2,usecols='B,D:F')
    data.columns = ['component'] + actual_dates
    data = data.dropna()

    data = data.melt(id_vars='component',var_name='date')
    data['date'] = [np.datetime64(date) for date in data['date']]
    data = data.pivot(index='date',columns='component')['value'].reset_index()
    data = data.set_index('date')

    income: IncomeStatement = IncomeStatement(
        revenue = Revenue(revenue = data["Revenue from sales and services"],
                          other_revenue = data["Other revenue"]),
        cogs = COGS(raw_material = data["Raw materials"],
                    direct_cost=data["Direct costs"]),
        opex = OperatingExpense(cost_for_services = data["Cost for services"],
                                lease_cost = data["Lease costs"],
                                other = data["Other operating expenses"]),
        d_and_a = data["D&A"],
        int_expense = data["Financial income/expenses"],
        extraordinary_income = data["Extraordinary income"],
        tax = data["Taxes"]
    )
    return income

def source_balance(file_loc:str,actual_dates:List[str]) -> BalanceSheet:

    data_a = pd.read_excel(file_loc,sheet_name='BS source',skiprows=2,usecols='B,D:F')
    data_a.columns = ['component'] + actual_dates

    data_b = pd.read_excel(file_loc,sheet_name='BS source',skiprows=2,usecols='H,J:L')
    data_b.columns = ['component'] + actual_dates

    data = pd.concat([data_a,data_b],axis=0).dropna()
    data = data.melt(id_vars='component',var_name='date')
    data['date'] = [np.datetime64(date) for date in data['date']]
    data = data.pivot(index='date',columns='component')['value'].reset_index()
    data = data.set_index('date')

    balance: BalanceSheet = BalanceSheet(
        intangible_asset = data["Intangible assets"],
        ppe = data["PP&E"],
        financial_asset = data["Financial assets"],
        financial_liability = FinLiab(bank_borrowing = data["Bank borrowings"],
                                      other_financial_liability = data["Other Financial liabilities"]),
        inventory = data["Inventory"],
        trade_receivable = data["Trade receivables"],
        other_asset = data["Other assets"],
        other_liability = OtherLiab(other_liability = data["Other liabilities"],
                                    deferred_taxes = data["Deferred taxes"],
                                    provision_for_retirement_benefit = data["Provisions for retirement benefits"]),
        trade_payable = data["Trade payable"],
        shareholder_equity = Equity(share_capital = data["Share Capital"],
                                    reserve = data["Reserves"],
                                    retained_earning = data["Retained earnings"],
                                    net_annual_profit = data["Profit/(loss) for the year"])
    )    
    return balance
