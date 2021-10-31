from data_storing.assets.common import Timespan
import fundamentals.miscellaneous as fund_utils
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities import log


def get_operating_cash_flow(equity, year):
    """
    @fn get_operating_cash_flow
    @brief The operating cash flow is simply the cash flow from operating activities retrieved
    from the cash flow statement.
    """
    try:
        cash_flow = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.cash_flow, year)

        if not cash_flow:
            return None

        cash_from_operating_activities = methods.validate(cash_flow.cash_from_operating_activities)
        return cash_from_operating_activities

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
