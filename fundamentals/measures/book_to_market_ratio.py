import sys
from data_storing.assets.common import Timespan
from fundamentals.measures.market_cap import get_market_cap
import fundamentals.miscellaneous as fund_utils
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities.exchange_rates import Exchange
from utilities import log


def get_book_to_market_ratio(equity, year=None, market_cap=None):
    """
    This ratio can be found by dividing the current book value per share by the price of the stock.

    The book value is defined as its total asses minus any liabilities
    Instead of using the current price per share we use the market capitalisation.
    """
    try:
        if year is None:
            # get it from the ratios
            ratios = equity.fundamentals.ratios
            if ratios:
                sorted_ratios = sorted(ratios, key=lambda x: x.current_period, reverse=True)  # the newest in front
                book_to_market_ratio = 1 / sorted_ratios[0].price_to_book_mrq
                return book_to_market_ratio

        # only get the current market cap if the year is not provided.
        if market_cap is None:
            market_cap = get_market_cap(equity)

        book_to_market_ratio = None

        # calculate it from the balance sheet
        balance_sheets = equity.fundamentals.balance_sheet
        normalised_total_equity = None

        if year is None:
            year = methods.get_last_year() # take last year

            # sort the balance sheets according to date, want to select the newest, not matter quarterly or annual
            sorted_balance_sheets = sorted(balance_sheets, key=lambda x: x.period_ending, reverse=True)
            balance_sheet = None
            for balance_sheet in sorted_balance_sheets:
                if balance_sheet.period_ending == year:
                    break
        else:
            balance_sheet = fund_utils.gm.get_annual_financial_statement(balance_sheets, year=year)

        if balance_sheet is not None:
            multiplier = fund_utils.gm.get_measure_unit_multiplier(methods.validate(balance_sheet.measure_unit))
            exchange = fund_utils.gm.get_exchange_rate(methods.validate(balance_sheet.currency), equity)

            total_equity = methods.validate(balance_sheet.total_equity)

            if total_equity is not None and multiplier is not None and exchange is not None:
                normalised_total_equity = total_equity * multiplier * exchange

        if normalised_total_equity is not None:
            book_to_market_ratio = market_cap / (normalised_total_equity + sys.float_info.epsilon)

        return book_to_market_ratio


    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

