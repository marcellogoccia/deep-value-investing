from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from utilities import log


def get_return_on_invested_capital(equity, year):
    """
    @function get_return_on_invested_capital
    The function return the return on invested capital of the share passed as
    input for the year specified in the input.
    The formula used was retrieved from the website The Balance.
    """
    try:
        income_statements = equity.fundamentals.income_statement
        balance_sheets = equity.fundamentals.balance_sheet

        nopat = None
        operating_capital = None
        roic = None

        taxes = 1 - 0.35

        for income_statement in income_statements:
            if income_statement.period_ending.year == year and \
                    income_statement.period_length == Timespan.annual:

                operating_income = income_statement.operating_income
                nopat = operating_income * taxes

                # depreciation_amortization = income_statement.depreciation_amortization
                # nopat = (operating_income + depreciation_amortization) * taxes

                break

        for balance_sheet in balance_sheets:
            if balance_sheet.period_ending.year == year and \
                    balance_sheet.period_length == Timespan.annual:

                if not balance_sheet.total_long_term_debt:
                    total_long_term_debt = 0
                else:
                    total_long_term_debt = balance_sheet.total_long_term_debt

                total_equity = balance_sheet.total_equity
                operating_capital = total_long_term_debt + total_equity
                # operating_capital = balance_sheet.total_liabilities_shareholders_equity
                break

        if nopat is not None and operating_capital is not None:
            roic = nopat / operating_capital

        return roic

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")



def get_return_on_invested_capital_v2(equity, year):
    """
    @function get_return_on_invested_capital_v2
    The function return the return on invested capital of the share passed as
    input for the year specified in the input.
    The formula used was retrieved from the book invested of Danielle Town.
    """
    try:
        income_statements = equity.fundamentals.income_statement
        balance_sheets = equity.fundamentals.balance_sheet

        net_income = None
        operating_capital = None
        roic = None

        for income_statement in income_statements:
            if income_statement.period_ending.year == year and \
                    income_statement.period_length == Timespan.annual:

                net_income = income_statement.net_income
                break

        for balance_sheet in balance_sheets:
            if balance_sheet.period_ending.year == year and \
                    balance_sheet.period_length == Timespan.annual:

                if not balance_sheet.total_long_term_debt:
                    total_long_term_debt = 0
                else:
                    total_long_term_debt = balance_sheet.total_long_term_debt

                shareholders_equity = balance_sheet.total_equity

                operating_capital = shareholders_equity + total_long_term_debt
                break

        if net_income is not None and operating_capital is not None:
            roic = net_income / operating_capital

        return roic

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
