# company pricing
import fundamentals
import fundamentals.company_pricing as cp

from utilities.common_methods import getDebugInfo
from utilities import log

from colorama import Fore, Back, Style


class IntrinsicValue:

    def __init__(self):
        pass

    @staticmethod
    def price_reflects_value(equity):
        """
        @function price_reflects_value
        It looks at the intrinsic value of the company and returns true if the current price
        agrees the intrinsic value calculated, otherwise it returns false.
        """
        price = fundamentals.strategies.IntrinsicValue.get_the_price_of_the_company(equity)
        last_price = equity.overview.last
        if last_price is None or price is None:
            return False

        if last_price <= (price * 1.10):
            log.info(f'{Back.RED}{Fore.WHITE} The equity with symbol {equity.exchange}:{equity.symbol_1}'
                     f' looks great!!!{Style.RESET_ALL}')
            return True
        else:
            return False

    @staticmethod
    def get_the_price_of_the_company(equity):
        """
        @function get_the_price_of_the_company
        It uses a few methods to return the intrinsic value of the company.
        What the price should be to get a good bargain.
        The priced is set as the max of all the found values.
        """
        try:
            pay_back_time_price = cp.get_pay_back_time(equity)
            margin_of_safety = cp.get_margin_of_safety(equity)
            price_mizrahi = cp.get_pricing_mizrahi(equity)

            return max(pay_back_time_price,
                       margin_of_safety,
                       price_mizrahi)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
