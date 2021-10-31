import fundamentals.miscellaneous as fund_utils

from utilities.common_methods import Methods as methods
from utilities import log
from utilities.common_methods import getDebugInfo


def get_market_cap(equity, year=None, balance_sheet=None):
    """
    It returns the market capitalisation of the equity passed a s input variable

    The method returns the most updated market cap is no year is passed, otherwise the corresponding market cap
    according to the year passed as input variable.
    The market cap is returns in USD, no matter the stock exchange of the equity
    @param equity the equity of which we want to return the market capitalisation 
    @param date the date when the market cap is wanted to be returned (at the moment it does not have any effect)
    @return the market capitalisation calculated
    """
    try:
        market_cap = None

        try:
            equity.overview.currency
        except ValueError:
            log.info(f"Currency problems with the equity {equity.exchange}:{equity.symbol_1}")
            return None

        exchange_rate = fund_utils.gm.get_exchange_rate(methods.validate(equity.overview.currency))

        if year is None:

            # The currency of the following is the same as the stock exchange,
            market_cap = methods.validate(equity.overview.market_cap)

            # That is why it will be multiplied to exchange rate
            market_cap = market_cap * exchange_rate

        else:
            if balance_sheet is None:
                balance_sheet = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.balance_sheet, year)
                if balance_sheet is None:
                    return None

            date = balance_sheet.period_ending.replace(day=1)
            if date is None:
                raise Exception("date not available in the balance sheet")

            multiplier = fund_utils.gm.get_measure_unit_multiplier(balance_sheet.measure_unit)

            for price in equity.prices:
                if price.day == date:
                    number_outstanding_shares = methods.validate(balance_sheet.total_common_shares_outstanding)

                    # If the market cap is computed in this way, I probably do not need to consider the currency.
                    if number_outstanding_shares is not None and price.close is not None and multiplier is not None:
                        market_cap = number_outstanding_shares * price.close * multiplier * exchange_rate
                    break

        return market_cap

    except Exception as e:
        log.error(f"There is a problem with equity {equity.exchange}:{equity.symbol_1} {e}\n{getDebugInfo()}")
        return None
