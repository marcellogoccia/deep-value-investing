from utilities.common_methods import getDebugInfo
from data_storing.assets.common import Benchmark
from utilities import log


def get_price_to_free_cash_flow_ratio(equity, year=None, market_cap=None):
    """
    This ratio can be found by dividing the current price of the stock by its free cash flow per share,

    Easy way is to get it from the ratios object extracted from investing.
    """
    try:
        price_to_free_cash_flow = None

        if year is None:
            # get it from the ratios
            ratios = equity.fundamentals.ratios
            sorted_ratios = sorted(ratios, key=lambda x: x.current_period, reverse=True)  # the newest in front

            # Starting from the first going down the list.
            for ratio in sorted_ratios:
                if ratio.benchmark == Benchmark.company:
                    price_to_free_cash_flow = ratio.price_to_free_cash_flow_ttm
                    break

            if price_to_free_cash_flow is None:
                price_to_free_cash_flow = 1000

        return price_to_free_cash_flow

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

