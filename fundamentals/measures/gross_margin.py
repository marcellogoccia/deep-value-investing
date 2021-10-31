import sys
import fundamentals.miscellaneous as fund_utils
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities import log


def get_gross_margin(equity, year):
    """
    @fn get_gross_margin
    @brief Gross margin is a company's net sales revenue minus its cost of goods sold (COGS)
    as a percentage fo the revenue.
    In other words, it is the sales revenue a company retains after incurring the direct costs
    associated with producing the goods it sells, and the services it provides.
    The higher the gross margin, the more capital a company retains on each dollar of sales,
    which it can then use to pay other costs or satisfy debt obligations.
    """
    try:
        income_statement = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.income_statement, year)

        if not income_statement:
            return None

        # get the cost of good sold (COGS) also knows as cost of sales
        revenue = methods.validate(income_statement.revenue)  # a.k.a. sales or net sales
        gross_profit = methods.validate(income_statement.gross_profit)

        gross_margin = None
        if revenue is not None and gross_profit is not None:
            gross_margin = gross_profit / (revenue + sys.float_info.epsilon)
        return gross_margin

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
