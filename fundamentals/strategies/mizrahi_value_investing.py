import fundamentals.analysis as analysis
import fundamentals.measures as measures

from utilities.common_methods import getDebugInfo
from utilities import log


class MizrahiConditions:
    """
    @class MizrahiConditions
    It collect all the conditions that must be met for a company to be picked up, according to
    the investing conditions described in the book Invested of Danielle Town.
    """
    def __init__(self):
        pass

    @staticmethod
    def has_the_company_got_the_moat(equity):
        try:
            if analysis.RoeHigherThanIndustry.is_met(equity) and \
                    analysis.NpmHigherThanIndustry.is_met(equity):
                # if got moat, check the company is sound.

                return True
            else:
                return False
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


    @staticmethod
    def are_the_big_numbers_are_satisfied(equity):
        """
        @function are_the_big_numbers_are_satisfied
        It evaluates the four big numbers if they satisfy the wanted conditions, if they are the function
        returns true, false otherwise.
        """
        try:
            # if #something:
            #     return True
            # else:
            #     return False
            pass
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
            roic = measures.get_return_on_invested_capital(equity, year)
            roic_v2 = measures.get_return_on_invested_capital_v2(equity, year)

            if roe > 0.15 and roic_v2 > 0.15:
                return True
            else:
                return False

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")



