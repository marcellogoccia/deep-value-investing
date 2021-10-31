import sys
import fundamentals.miscellaneous as fund_utils
from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities import log


def get_asset_turnover_ratio(equity, year):
    """
    @fn get_asset_turnover_ratio
    @brief The asset turnover ratio is an efficiency ratio that measures a company’s ability to generate
    sales from its assets by comparing net sales with average total assets. In other words, this ratio shows how
    efficiently a company can use its assets to generate sales.
    The asset turnover ratio is calculated by dividing net sales by average total assets.
    The total asset turnover ratio calculates net sales as a percentage of assets to show how many sales are
    generated from each dollar of company assets. For instance, a ratio of .5 means that each dollar of assets
    generates 50 cents of sales.
    """
    try:
        pr_year = year - 1
        income_statement = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.income_statement, year)
        balance_sheet = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.balance_sheet, year)
        balance_sheet_prev_y = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.balance_sheet, pr_year)

        if not income_statement or not balance_sheet or not balance_sheet_prev_y:
            return None

        # get net sales (revenue)
        revenue = methods.validate(income_statement.revenue)  # a.k.a. sales or net sales

        # get the total assets
        total_assets_curr_year = methods.validate(balance_sheet.total_assets)
        total_assets_prev_year = methods.validate(balance_sheet_prev_y.total_assets)

        # check validity of the found items
        asset_turnover_ratio = None
        if revenue is not None and total_assets_curr_year is not None and total_assets_prev_year is not None:
            asset_turnover_ratio = 2 * revenue / (total_assets_curr_year + total_assets_prev_year + sys.float_info.epsilon)

        return asset_turnover_ratio

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
