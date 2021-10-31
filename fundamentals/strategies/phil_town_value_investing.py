import fundamentals.analysis as analysis
import fundamentals.measures as measures

from utilities.common_methods import getDebugInfo
from utilities import log


class PhilTownConditions:
    """
    @class PhilTownConditions
    It collect all the conditions that must be met for a company to be picked up, according to
    the investing conditions described in the book Invested of Danielle Town.
    """
    def __init__(self):
        pass

    @staticmethod
    def are_the_big_numbers_are_satisfied(equity):
        """
        @function are_the_big_numbers_are_satisfied
        It evaluates the four big numbers if they satisfy the wanted conditions, if they are the function
        returns true, false otherwise.
        """
        try:
            if analysis.NetIncomeIncreasing.is_met(equity) and \
                    analysis.BookValuePlusDividendsIncreasing.is_met(equity) and \
                    analysis.RevenueSalesIncreasing.is_met(equity) and \
                    analysis.CashFromOperatingActivitiesIncreasing.is_met(equity):
                return True
            else:
                return False
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    @staticmethod
    def are_the_management_numbers_satisfied(equity):
        """
        @function are_the_management_numbers_satisfied
        It evaluates the conditions to be considered for a good managing team. If the conditions are met
        the function returns true, false otherwise.
        """
        try:
            year = 2018
            roe = measures.get_return_on_equity(equity, year)
            if roe is None:
                return False
            roic = measures.get_return_on_invested_capital(equity, year)
            if roic is None:
                return False
            roic_v2 = measures.get_return_on_invested_capital_v2(equity, year)
            if roic_v2 is None:
                return False

            if roe > 0.15 and roic_v2 > 0.15:
                return True
            else:
                return False

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
