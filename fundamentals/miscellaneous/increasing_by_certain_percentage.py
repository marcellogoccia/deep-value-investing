from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from utilities import log


def is_met(financial_statements, financial_key, percentage_improvement):
    """
    function is_met
    It scans through the financial statements passed as input to see if the financial key passed as input
    increases by a percentage (passed as input) a year.
    """
    try:
        previous = 0
        good_fundamentals_counter = 0
        number_years = 0
        complementary_percentage = 1 - percentage_improvement

        if not financial_statements:
            return False

        # scanning through the financial statements.
        for statement in financial_statements:

            if statement.period_length == Timespan.annual:

                number_years += 1  # keep tracks of how many financial statements I have.

                globals_vars = {'statement': statement}
                local_vars = {}

                exec(f"value_financial_key = statement.{financial_key}", globals_vars, local_vars)
                current = local_vars['value_financial_key']

                if current:  # if it is not None
                    current_minus_improvement = current * complementary_percentage
                    if previous < current_minus_improvement:
                        good_fundamentals_counter += 1
                    previous = current

        if good_fundamentals_counter == number_years:  # increased every year
            return True
        else:
            return False

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

