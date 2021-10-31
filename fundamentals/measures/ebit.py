from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities import log


def get_ebit(equity, year=None):
    """
    The function returns the company's ebit.

    The ebit is defined as the ...
    """
    try:
        income_statements = equity.fundamentals.income_statement

        #now = datetime.datetime.now()
        if year is None:
            year = methods.get_last_year()

        income_statement_of_interest = None
        for income_statement in income_statements:
            if income_statement.period_ending.year == year and \
                    income_statement.period_length == Timespan.annual:
                income_statement_of_interest = income_statement
                break
        if income_statement_of_interest:
            total_revenue = methods.validate(income_statement_of_interest.total_revenue)
            total_operating_expenses = methods.validate(income_statement_of_interest.total_operating_expenses)

            net_income_before_taxes = methods.validate(income_statement_of_interest.net_income_before_taxes)
            interest_income_expense_net_non_operating = \
                methods.validate(income_statement_of_interest.interest_income_expense_net_non_operating)

        else:
            return None

        ebit = total_revenue - total_operating_expenses
        ebit = net_income_before_taxes + interest_income_expense_net_non_operating

        return ebit

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
