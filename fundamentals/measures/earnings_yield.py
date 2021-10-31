from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
import fundamentals.miscellaneous as fund_utils
from fundamentals.measures.market_cap import get_market_cap
from utilities.exchange_rates import Exchange
from utilities import log


def get_earnings_yield(equity, year=None, market_cap=None):
    """
    This ratio can be found by dividing the current earning per share by its price

    The earning is defined as the net-income
    Instead of using the current price per share we use the market capitalisation.
    """
    try:
        if year is None:
            # get it from the ratios
            ratios = equity.fundamentals.ratios
            if ratios:
                sorted_ratios = sorted(ratios, key=lambda x: x.current_period, reverse=True)  # the newest in front
                pe_ratio_ttm = sorted_ratios[0].pe_ratio_ttm
                earnings_yield_from_ratios = None
                if pe_ratio_ttm is not None:
                    earnings_yield_from_ratios = 1 / pe_ratio_ttm
            # only get the current market cap if the year is not provided.
            market_cap = get_market_cap(equity)

        if market_cap is None:
            raise Exception(f"Market cap for {equity.exchange}:{equity.symbol_1}:{equity.id} not available!")

        normalised_net_income = None

        total_net_income = 0
        multiplier = None
        exchange = None
        earnings_yield = None

        # The income statement of interest.
        income_statement = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.income_statement, year)

        #############
        # The following commented code is used to the total_net_income as the sum of the
        # last four quarter total_net_incomes from the income statements.
        #############
        # # sort them, the newest at the beginning of the list.
        # sorted_income_statements = sorted(income_statements, key=lambda x: x.period_ending, reverse=True)
        #
        # counter = 0
        # # find the first quarterly income statement
        # for income_statement in sorted_income_statements:
        #     if income_statement.period_length == Timespan.quarterly:
        #
        #         if not older_period_ending:
        #             older_period_ending = income_statement.period_ending
        #
        #         else:
        #             if (older_period_ending - income_statement.period_ending).days < 100:
        #                 older_period_ending = income_statement.period_ending
        #             else:
        #                 total_net_income = None
        #                 break
        #
        #         net_income = methods.validate(income_statement.net_income)
        #         total_net_income += net_income
        #         counter += 1
        #
        #         if counter == 4:  # once we reach 4 income statement break
        #             break
        #
        # if counter < 4:
        #     total_net_income = None

        if income_statement:
            multiplier = fund_utils.gm.get_measure_unit_multiplier(income_statement.measure_unit)
            exchange = fund_utils.gm.get_exchange_rate(methods.validate(income_statement.currency), equity)

            total_net_income = methods.validate(income_statement.net_income)

        if total_net_income is not None and multiplier is not None and exchange is not None:
            normalised_net_income = total_net_income * multiplier * exchange

        if normalised_net_income is not None:
            earnings_yield = normalised_net_income / market_cap

        return earnings_yield

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

