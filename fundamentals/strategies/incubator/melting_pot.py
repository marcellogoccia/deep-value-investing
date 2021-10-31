from fundamentals.strategies.basic_strategy.strategy import Strategy
from fundamentals.strategies.what_works_on_wall_street.what_works_on_wall_street import WhatWorksOnWallStreet
from fundamentals.strategies.acquirers_multiple.acquirers_multiple import AcquirersMultiple
from fundamentals.strategies.piotrosky.piotroski_9_points import Piotroski9Points

from data_storing.assets.database_manager import DatabaseManager as db_mngr
from utilities.common_methods import getDebugInfo
from utilities import log


class MeltingPot(Strategy):
    """
    To define. Ideally is a way to mix providing better performance a few back-tested strategies.
    The class is designed to be able to easily switch between factors to include into the strategy to backtest.
    """
    def __init__(self):
        try:

            Strategy.__init__(self)

            # define all the existing strategies
            self.wwows = WhatWorksOnWallStreet()
            self.am = AcquirersMultiple()
            self.p9p = Piotroski9Points()

            self.global_score = {}

            self.strategy_factors = {}

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def set_value(self, equity, market_cap=None):
        try:
            self.wwows.set_value(equity=equity, year=self.year, market_cap=market_cap)
            self.am.set_value(equity=equity, year=self.year, market_cap=market_cap)
            self.p9p.set_value(equity=equity, year=self.year, market_cap=market_cap)
            self.set_extra_values(equity=equity, year=self.year, market_cap=market_cap)
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def set_extra_values(self, equity, year=None, market_cap=None):
        try:

            self.extra_factor = {}

            if equity.symbol_1 in self.list_stocks_to_exclude:
                return None

            # some_measure_I_would_like_to_test = measure.get_the_measure(equity, self.year, market_cap)
            # ...
            # extra needed

            # if some_measure_I_would_like_to_test is None:
            #     self.extra_factor[equity.id] = None
            # else:
            #     self.extra_factor[equity.id] = some_measure_I_would_like_to_test

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def sort_equities(self):
        """
        It sorts the equities to find the ones that are good to invest in.
        @return Nothing
        """
        try:
            list_factors_reverse = ['piotrosky_score', 'ebitda_ev_ratio', 'shareholder_yield']
            reverse = False

            for factor, values in self.strategy_factors.items():
                if factor in list_factors_reverse:
                    reverse = True

                self.strategy_factors[factor] = Strategy.order_dictionary_by_value(values, reverse=reverse)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def score_equities(self):
        """
        It sets the scores according to the strategy used.
        @return The scores of the stocks to invest in.
        """
        try:
            for factor in self.strategy_factors.keys():
                rank = 1
                for equity_id in self.strategy_factors[factor]:
                    self.strategy_factors[factor][equity_id] = rank
                    rank += 1

            self.sum_scores()

            self.order_scores()

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def sum_scores(self):
        try:
            factors = list(self.strategy_factors.keys())

            equity_ids = self.get_unique_equity_ids(factors)

            num_equities = len(equity_ids)
            average_score = num_equities // 2

            self.global_score = {}

            for equity_id in equity_ids:

                sum_score = 0
                for factor in factors:
                    sum_score += self.strategy_factors[factor].get(equity_id, average_score)

                self.global_score[equity_id] = sum_score

            pass

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def get_unique_equity_ids(self, factors):

        try:
            # place the equity ids in different lists (one list for each extracted factor.
            equity_ids = []
            for factor in factors:
                ids = list(self.strategy_factors[factor].keys())
                equity_ids.append(ids)

            # join all the equity ids lists in a single one, so that we have a single list with unique equity ids.
            iter_equity_ids = iter(equity_ids)
            first_iter = next(iter_equity_ids)
            set_equity_ids = set(first_iter)
            for ids in iter_equity_ids:
                set_equity_ids |= set(ids)  # the operation or between sets will

            # convert from se to list
            return list(set_equity_ids)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def order_scores(self):

        try:
            self.global_score = Strategy.order_dictionary_by_value(self.global_score)
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def discriminate_on_price(self):
        try:
            # for equity_id, value in self.global_score.items():
            #     equity = db_mngr.query_equity_by_id(equity_id=equity_id)
            #
            #     if equity.symbol_1 == 'DNLM' and self.year == 2017:
            #         a = 1
            #
            #     for price in equity.prices:
            #         if price.day == self.dates['start_date']:
            #             if price.close > self.max_price_share:
            #                 a = 'not_good'
            #             else:
            #                 continue
            #
            #     a = 1
            pass
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

