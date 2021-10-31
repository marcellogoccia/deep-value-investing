import sys
from data_storing.assets.common import Timespan
from utilities.common_methods import Methods as methods
from utilities.common_methods import getDebugInfo
from data_storing.assets.common import Benchmark
import fundamentals.miscellaneous as fund_utils
from utilities.exchange_rates import Exchange
from utilities import log


def get_price_to_cash_flow_ratio(equity, year=None, market_cap=None):
    """
    This ratio can be found by dividing the current price of the stock by its operating cash flow per share,

    Easy way is to get it from the ratios object extracted from investing.
    """
    try:
        price_to_cash_flow = None

        if year is None:
            # get it from the ratios
            ratios = equity.fundamentals.ratios
            sorted_ratios = sorted(ratios, key=lambda x: x.current_period, reverse=True)  # the newest in front

            # Starting from the first going down the list.
            for ratio in sorted_ratios:
                if ratio.benchmark == Benchmark.company:
                    price_to_cash_flow = ratio.price_to_cash_flow_mrq
                    break

            if price_to_cash_flow is None:
                price_to_cash_flow = 1000

        else:
            if market_cap is None:
                raise Exception(f"Market cap for {equity.exchange}:{equity.symbol_1}:{equity.id} not available!")

            operating_cash_flow = None
            normalised_operating_cash_flow = None
            multiplier = None
            exchange = None

            # The cash flow of interest
            cash_flow = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.cash_flow, year)

            if cash_flow is not None:
                multiplier = fund_utils.gm.get_measure_unit_multiplier(cash_flow.measure_unit)
                exchange = fund_utils.gm.get_exchange_rate(methods.validate(cash_flow.currency), equity)

                operating_cash_flow = methods.validate(cash_flow.cash_from_operating_activities)

            if operating_cash_flow is not None and multiplier is not None and exchange is not None:
                normalised_operating_cash_flow = operating_cash_flow * multiplier * exchange

            if normalised_operating_cash_flow is not None:
                price_to_cash_flow = market_cap / (normalised_operating_cash_flow + sys.float_info.epsilon)

        return price_to_cash_flow

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

