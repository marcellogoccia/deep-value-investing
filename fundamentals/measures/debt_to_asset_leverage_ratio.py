import sys
import fundamentals.miscellaneous as fund_utils
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities import log


def get_debt_to_asset_leverage_ratio(equity, year):
    """
    @fn get_debt_to_asset_leverage_ratio
    @brief The debt to asset leverage ratio is calculated as the total debt / average total assets ratio
    @param equity the equity entity
    @param year the year of which we want to calculate the leverage
    @return the calculated leverage
    """
    try:
        balance_sheet = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.balance_sheet, year)

        if not balance_sheet:
            return None

        # get the total assets and total liabilities.
        total_assets = methods.validate(balance_sheet.total_assets)
        total_liabilities = methods.validate(balance_sheet.total_liabilities)

        if total_assets is None or total_liabilities is None:
            return None

        else:
            leverage_ratio = total_liabilities / (total_assets + sys.float_info.epsilon)
            return leverage_ratio

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
        return None
