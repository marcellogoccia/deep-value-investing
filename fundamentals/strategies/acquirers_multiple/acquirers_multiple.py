from fundamentals.strategies.basic_strategy.strategy import Strategy
import fundamentals.measures as measure
import sys
from utilities.common_methods import getDebugInfo
from utilities import log


class AcquirersMultiple(Strategy):

    def __init__(self):
        try:
            self.acquirers_multiple = {}
            self.enterprise_value = {}
            self.operating_earnings = {}
            Strategy.__init__(self)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def set_value(self, equity, year=None, market_cap=None):
        try:
            if equity.symbol_1 in self.list_stocks_to_exclude:
                return None

            if year is not None:  # if set value brings a
                self.year = year

            enterprise_value = measure.get_enterprise_value(equity, self.year, market_cap)
            operating_earnings = measure.get_operating_earnings(equity, self.year)

            if enterprise_value is None or operating_earnings is None or operating_earnings < 0:
                self.set_default_values(equity)
            else:
                acquirers_multiple = enterprise_value / (operating_earnings + sys.float_info.epsilon)
                self.acquirers_multiple[equity.id] = acquirers_multiple
                self.enterprise_value[equity.id] = enterprise_value
                self.operating_earnings[equity.id] = operating_earnings

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
            self.set_default_values(equity)

    def set_default_values(self, equity):
        """
        It sets he defualt value to the dictionary
        @return
        """
        self.acquirers_multiple[equity.id] = 1000
        self.enterprise_value[equity.id] = 1000
        self.operating_earnings[equity.id] = 1000

    def sort_equities(self):
        """
        It sorts the equities to find the ones that are good to invest in.
        @return Nothing
        """
        self.acquirers_multiple = AcquirersMultiple.order_dictionary_by_value(self.acquirers_multiple)

    def reset_factors(self):
        """
        It resets the factors used to store the companies economic data
        @return Nothing
        """
        try:
            self.acquirers_multiple = {}
            self.enterprise_value = {}
            self.operating_earnings = {}
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    # @staticmethod
    # def sort_getter(item, reverse=False):
    #     value = item[1]['acquirers_multiple']
    #     if value is None:
    #         if reverse:
    #             return -1000
    #         else:
    #             return 1000
    #     return value

