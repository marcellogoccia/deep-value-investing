import fundamentals.miscellaneous as fund_utils
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities import log


def get_outstanding_common_shares(equity, year):
    """
    @fn get_outstanding_common_shares
    @brief It returns the number of common outstanding shares for the year passed as input
    @param equity the equity entity
    @param year the year of which we want to calculate the leverage
    @return the outstanding shares
    """
    try:
        balance_sheet = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.balance_sheet, year)

        if not balance_sheet:
            return None

        # get the number of the total common shares outstanding
        total_common_shares_outstanding = methods.validate(balance_sheet.total_common_shares_outstanding)
        return total_common_shares_outstanding

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
