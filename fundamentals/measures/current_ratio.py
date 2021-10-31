import sys
import fundamentals.miscellaneous as fund_utils
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities import log


def get_current_ratio(equity, year):
    """
    @fn get_current_ratio
    @brief the Current Ratio is achieved taking the current assets and dividing them by the current liabilities.
    @param equity the equity entity
    @param year the year of which we want to calculate the leverage
    @return the calculated current ratio
    """
    try:
        balance_sheet = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.balance_sheet, year)

        if not balance_sheet:
            return None


        # get the total assets and total liabilities.
        total_current_assets = methods.validate(balance_sheet.total_current_assets)
        total_current_liabilities = methods.validate(balance_sheet.total_current_liabilities)

        if total_current_assets is None or total_current_liabilities is None:
            return None

        else:
            current_ratio = total_current_assets / (total_current_liabilities + sys.float_info.epsilon)
            return current_ratio

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
