import sys
from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities.exchange_rates import Exchange
import fundamentals.miscellaneous as fund_utils
from utilities import log


def get_market_cap_preferred_shares(equity, year=None):
    """
    @function get_market_cap_preferred_shares
    The function returns the market capitalisation of the preferred stocks, if any.
    The market capitalisation of the preferred stocks is defined as ...
    """
    try:
        balance_sheets = equity.fundamentals.balance_sheet

        if year is None:
            year = methods.get_last_year()

        balance_sheet = None
        for balance_sheet in balance_sheets:
            if balance_sheet.period_ending.year == year and balance_sheet.period_length == Timespan.annual:
                break

        if balance_sheet is None:
            return None

        multiplier = fund_utils.gm.get_measure_unit_multiplier(balance_sheet.measure_unit)
        if multiplier is None:
            multiplier = 1000000

        if balance_sheet:

            # approximating the market cap for the preferred stock
            # need to check if reliable
            preferred_shares_outstanding = methods.validate(balance_sheet.total_preferred_shares_outstanding)
            prevailing_market_yield = 0.04

            # Convert to USD !!!!
            exchange_rate = fund_utils.gm.get_exchange_rate(methods.validate(balance_sheet.currency), equity)

            annual_dividend_income = methods.validate(equity.overview.dividend)

            price_preferred_share = annual_dividend_income / (prevailing_market_yield + sys.float_info.epsilon)
            market_cap_preferred_shares = preferred_shares_outstanding * price_preferred_share * exchange_rate * multiplier

            return market_cap_preferred_shares

        else:
            return None

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
