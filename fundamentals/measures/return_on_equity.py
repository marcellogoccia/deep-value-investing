from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from utilities import log


def get_return_on_equity(equity, year):
    """
    @fn get_return_on_equity
    @brief The function return the return on equity of the share passed as input.
    """
    try:
        income_statements = equity.fundamentals.income_statement
        balance_sheets = equity.fundamentals.balance_sheet

        net_income = None
        shareholders_equity = None
        roe = None

        for income_statement in income_statements:
            if income_statement.period_ending.year == year and \
                    income_statement.period_length == Timespan.annual:

                net_income = income_statement.net_income
                break

        for balance_sheet in balance_sheets:
            if balance_sheet.period_ending.year == year and \
                    balance_sheet.period_length == Timespan.annual:

                shareholders_equity = balance_sheet.total_assets - balance_sheet.total_liabilities
                break

        if net_income is not None and shareholders_equity is not None:
            roe = net_income / shareholders_equity

        return roe

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
