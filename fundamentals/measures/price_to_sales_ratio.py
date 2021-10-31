import sys
from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from data_storing.assets.common import Benchmark
from utilities.common_methods import Methods as methods
import fundamentals.miscellaneous as fund_utils
from utilities.exchange_rates import Exchange
from utilities import log


def get_price_to_sales_ratio(equity, year=None, market_cap=None):
    """
    This ratio can be found by dividing the current price of the stock by its revenue per share,

    Easy way is to get it from the ratios object extracted from investing.
    """
    try:
        price_to_sales = None

        if year is None:
            # get it from the ratios
            ratios = equity.fundamentals.ratios
            sorted_ratios = sorted(ratios, key=lambda x: x.current_period, reverse=True)  # the newest in front

            # Starting from the first going down the list.
            for ratio in sorted_ratios:
                if ratio.benchmark == Benchmark.company:
                    price_to_sales = ratio.price_to_sales_ttm
                    break

            if price_to_sales is None:
                price_to_sales = 1000

        else:
            if market_cap is None:
                raise Exception(f"Market cap for {equity.exchange}:{equity.symbol_1}:{equity.id} not available!")

            revenue = None
            normalised_revenue = None
            multiplier = None
            exchange = None

            # The income statement of interest.
            income_statement = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.income_statement, year)

            if income_statement is not None:
                multiplier = fund_utils.gm.get_measure_unit_multiplier(income_statement.measure_unit)
                exchange = fund_utils.gm.get_exchange_rate(methods.validate(income_statement.currency), equity)

                revenue = methods.validate(income_statement.revenue)

            if revenue is not None and multiplier is not None and exchange is not None:
                normalised_revenue = revenue * multiplier * exchange

            if normalised_revenue is not None:
                price_to_sales = market_cap / (normalised_revenue + sys.float_info.epsilon)

        return price_to_sales

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

