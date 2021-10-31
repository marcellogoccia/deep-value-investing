from data_storing.assets.common import Timespan
import fundamentals.miscellaneous as fund_utils

from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities import log


def get_net_income(equity, year):
    """
    The net income can be found in the income statement (towards the end) and in the statement of cash flow.
    """
    try:
        # cash_flow = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.cash_flow, year)
        income_statement = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.income_statement, year)

        if not income_statement:
            return None

        # get the net income, two ways to get it.
        # net_income_cf = methods.validate(cash_flow.net_income_starting_line)
        net_income_is = methods.validate(income_statement.net_income)

        # if net_income_cf != net_income_is:
        #     log.info(f"Something wrong, the net income different from casf-flow and income statement "
        #              f"for {equity.exchange}:{equity.symbol_1}")

        return net_income_is

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
