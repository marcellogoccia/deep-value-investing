from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
import fundamentals.miscellaneous as fund_utils
from utilities import log


def get_ebitda(equity, year=None):
    """
    The function returns the company's ebitda

    The ebitda is defined as the company's earnings before interest, taxes, depreciation and amortization.
    """
    try:
        if year is None:
            year = methods.get_last_year()

        # The income statement of interest.
        income_statement = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.income_statement, year)

        if income_statement:
            operating_income = methods.validate(income_statement.operating_income)
            depreciation_amortization = methods.validate(income_statement.depreciation_amortization)

        else:
            return None

        ebitda = operating_income + depreciation_amortization

        multiplier = fund_utils.gm.get_measure_unit_multiplier(income_statement.measure_unit)
        exchange_rate = fund_utils.gm.get_exchange_rate(methods.validate(income_statement.currency), equity)

        if multiplier is not None:
            ebitda = ebitda * multiplier * exchange_rate
        else:
            ebitda = None

        return ebitda

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
