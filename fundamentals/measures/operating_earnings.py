from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities.exchange_rates import Exchange
import fundamentals.miscellaneous as fund_utils
from utilities import log


def get_operating_earnings(equity, year=None):
    """
    @function get_operating_earnings
    The function returns the company's operating_earnings.
    The operating_earnings is defined as the ...
    """
    try:
        if year is None:
            year = methods.get_last_year()

        # The income statement of interest.
        income_statement = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.income_statement, year)

        if income_statement:

            operating_income = methods.validate(income_statement.operating_income)
            unusual_expense_income = methods.validate(income_statement.unusual_expense_income)
            operating_earnings = operating_income + unusual_expense_income

            exchange = fund_utils.gm.get_exchange_rate(methods.validate(income_statement.currency), equity)
            multiplier = fund_utils.gm.get_measure_unit_multiplier(income_statement.measure_unit)
            if operating_earnings is not None and exchange is not None and multiplier is None:
                return None
            operating_earnings = operating_earnings * multiplier * exchange
            return operating_earnings

            if 0:
                total_revenue = methods.validate(income_statement.total_revenue)
                cost_of_revenue_total = methods.validate(income_statement.cost_of_revenue_total)
                selling_general_admin_expenses_total = \
                    methods.validate(income_statement.selling_general_admin_expenses_total)
                research_development = methods.validate(income_statement.research_development)
                depreciation_amortization = methods.validate(income_statement.depreciation_amortization)
                other_operating_expenses_total = \
                    methods.validate(income_statement.other_operating_expenses_total)
                print(f'previous operating earnings: {operating_earnings}')
                operating_earnings = total_revenue - \
                                     cost_of_revenue_total - \
                                     selling_general_admin_expenses_total - \
                                     research_development - \
                                     depreciation_amortization - \
                                     other_operating_expenses_total
                print(f'current operating earnings: {operating_earnings}')
                return operating_earnings

        else:
            return None
    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
