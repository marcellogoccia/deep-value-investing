import sys
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
import fundamentals.miscellaneous as fund_utils
from utilities import log


def get_shareholder_yield(equity, year=None, market_cap=None):
    """
    This measure unites the stock's dividend yield with its buyback yield.

    It just sums up the two values.
    """
    try:
        if year is None:
            year = methods.get_last_year()

        # The cash flow of interest, which means the one we are interested in.
        cash_flow = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.cash_flow, year)

        if cash_flow is not None:
            multiplier = fund_utils.gm.get_measure_unit_multiplier(cash_flow.measure_unit)
            exchange = fund_utils.gm.get_exchange_rate(methods.validate(cash_flow.currency), equity)

            total_cash_dividends_paid = methods.validate(cash_flow.total_cash_dividends_paid)
            issuance_retirement_of_stock_net = methods.validate(cash_flow.issuance_retirement_of_stock_net)
            issuance_retirement_of_debt_net = methods.validate(cash_flow.issuance_retirement_of_debt_net)

        else:
            return 0  # set the value to 0, which is the worst value for this factor.

        if multiplier is not None and exchange is not None:
            # remove the multiplier from the market cap, to make it divisible
            shareholder_yield_dividend = (total_cash_dividends_paid +
                                          issuance_retirement_of_stock_net +
                                          issuance_retirement_of_debt_net) * multiplier * exchange

            shareholder_yield = shareholder_yield_dividend / (market_cap + sys.float_info.epsilon)
        else:
            shareholder_yield = 0  # set the value to 0, which is the worst value for this factor.

        return shareholder_yield

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
