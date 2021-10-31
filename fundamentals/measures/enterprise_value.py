from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities.exchange_rates import Exchange
import fundamentals.miscellaneous as fund_utils

from fundamentals.measures.market_cap_preferred_shares import get_market_cap_preferred_shares
from fundamentals.measures.market_cap import get_market_cap
from utilities import log


def get_enterprise_value(equity, year=None, market_cap=None):
    """
    @function get_enterprise_value
    The function returns the enterprise value.
    The enterprise value is defined as the
    """
    try:
        # get last year in digits
        if year is None:
            market_cap = get_market_cap(equity)
            year = methods.get_last_year()
        elif market_cap is None:
            market_cap = get_market_cap(equity, year)

        # extract the balance sheet we are interested in
        balance_sheet = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.balance_sheet, year)

        if balance_sheet:
            exchange_rate = fund_utils.gm.get_exchange_rate(methods.validate(balance_sheet.currency), equity)
            multiplier = fund_utils.gm.get_measure_unit_multiplier(balance_sheet.measure_unit)
            if multiplier is None or exchange_rate is None:
                return None

            total_debt = methods.validate(balance_sheet.total_debt)
            minority_interest = methods.validate(balance_sheet.minority_interest)
            # divided by multiplier because it was previously multiplied by the multiplier
            market_cap_preferred_shares = get_market_cap_preferred_shares(equity, year) / multiplier

            # total_cash = methods.validate(balance_sheet.cash_and_short_term_investments)
            cash = methods.validate(balance_sheet.cash)
            cash_and_equivalents = methods.validate(balance_sheet.cash_and_equivalents)
            total_cash = cash + cash_and_equivalents
        else:
            return None

        enterprise_value_before_market_cap = total_debt + \
                                             market_cap_preferred_shares + \
                                             minority_interest - \
                                             total_cash

        enterprise_value = market_cap + (enterprise_value_before_market_cap * multiplier * exchange_rate)

        return enterprise_value

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
