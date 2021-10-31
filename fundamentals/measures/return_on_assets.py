import sys
from data_storing.assets.common import Timespan
import fundamentals.miscellaneous as fund_utils
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities import log


def get_return_on_assets(equity, year):
    """
    @fn get_return_on_assets
    @brief This ratio is simply net income dividend by assets.
    It shows how well the assets are being utilized to generate profit.
    """
    try:
        pr_year = year - 1
        balance_sheet_curr_y = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.balance_sheet, year)
        balance_sheet_prev_y = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.balance_sheet, pr_year)
        income_statement = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.income_statement, year)

        if not balance_sheet_curr_y or not balance_sheet_prev_y or not income_statement:
            return None

        # get the net income
        net_income = methods.validate(income_statement.net_income)

        # get the total assets
        total_assets_curr_year = methods.validate(balance_sheet_curr_y.total_assets)
        total_assets_prev_year = methods.validate(balance_sheet_prev_y.total_assets)

        return_on_assets = None
        if net_income is not None and \
                total_assets_curr_year is not None and \
                total_assets_prev_year is not None:
            return_on_assets = 2 * net_income / (total_assets_curr_year + total_assets_prev_year + sys.float_info.epsilon)
        return return_on_assets

        ###### OR QUICKER ######
        # # get the latest return on assets ttm
        # ratios = equity.fundamentals.ratios
        # roa_ttm = methods.validate(ratios.return_on_assets_ttm)
        # return roa_ttm

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
