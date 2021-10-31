from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
import fundamentals.miscellaneous as fund_utils
from fundamentals.measures.market_cap import get_market_cap
from utilities.exchange_rates import Exchange
from utilities import log


def get_ebitda_ev_ratio(equity, year=None, market_cap=None):
    """
    This ratio can be found by dividing the ebitda by the enterprice value

    The ebitda is defined as the company's earnings before interest, taxes, depreciation and amortization.
    The enterprise value is defined as the
    """
    try:
        pass
    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

