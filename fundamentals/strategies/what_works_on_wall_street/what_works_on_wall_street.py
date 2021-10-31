import itertools
import numpy as np
import sys

from fundamentals.strategies.basic_strategy.strategy import Strategy
from data_storing.assets.database_manager import DatabaseManager as db_mngr

from utilities.common_methods import getDebugInfo
from utilities import log
from utilities.common_methods import Methods as methods

import fundamentals.miscellaneous as fund_utils
import fundamentals.measures as measure


class WhatWorksOnWallStreet(Strategy):

    def __init__(self):
        try:
            self.price_to_book_ratio = {}
            self.price_to_earnings_ratio = {}
            self.price_to_sales = {}
            self.ebitda_ev_ratio = {}
            self.price_to_cash_flow = {}
            self.shareholder_yield       = {}

            self.all_factors_dict = {}

            self.best_decile_dict = {}
            self.worst_decile_dict = {}

            # self.price_appreciation_dict = {}
            # self.price_distribution_dict = {}
            # self.price_variations_score = {}

            Strategy.__init__(self)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def set_value(self, equity, year=None, market_cap=None):
        try:
            ######################
            # 1 - price_to_book_ratio
            ######################
            if not year:
                self.price_to_book_ratio[equity.id] = measure.get_price_to_book_ratio(equity)
            else:
                btm = measure.get_book_to_market_ratio(equity, year=year, market_cap=market_cap)
                if btm is None:
                    price_to_book_ratio = None
                else:
                    price_to_book_ratio = 1 / (btm + sys.float_info.epsilon)
                    if price_to_book_ratio < 0:
                        price_to_book_ratio = None
                self.price_to_book_ratio[equity.id] = price_to_book_ratio

            ######################
            # 2 - price_to_earnings_ratio
            ######################
            if not year:
                self.price_to_earnings_ratio[equity.id] = measure.get_price_to_earnings_ratio(equity)
            else:
                earnyield = measure.get_earnings_yield(equity, year=year, market_cap=market_cap)
                if earnyield is None:
                    price_to_earnings_ratio = None
                else:
                    price_to_earnings_ratio = 1 / (earnyield + sys.float_info.epsilon)
                    if price_to_earnings_ratio < 0:
                        price_to_earnings_ratio = None
                self.price_to_earnings_ratio[equity.id] = price_to_earnings_ratio

            ######################
            # 3 - price_to_sales
            ######################
            if not year:
                self.price_to_sales[equity.id] = measure.get_price_to_sales_ratio(equity)
            else:
                self.price_to_sales[equity.id] = measure.get_price_to_sales_ratio(equity, year=year, market_cap=market_cap)

            ###########################
            # 4 - ebitda / enterprise value
            ###########################
            # TODO use "get_annual_financial_statement" also in other needed methods.
            # TODO integrate ebitda/ev in a single method to solve the problem of the currency exchange rate.
            ebitda = measure.get_ebitda(equity, year=year)
            enterprise_value = measure.get_enterprise_value(equity, year=year, market_cap=market_cap)
            if ebitda is not None and enterprise_value is not None and enterprise_value != 0:
                ebitda_ev_ratio = ebitda / enterprise_value
            else:
                ebitda_ev_ratio = 0  # set the value to 0, which is the worst value for this factor.
            self.ebitda_ev_ratio[equity.id] = ebitda_ev_ratio

            ######################
            # 5 - price_to_cash_flow
            ######################
            if not year:
                self.price_to_cash_flow[equity.id] = measure.get_price_to_cash_flow_ratio(equity)
            else:
                self.price_to_cash_flow[equity.id] = measure.get_price_to_cash_flow_ratio(equity, year=year, market_cap=market_cap)

            ######################
            # 6 - shareholder_yield
            ######################
            if not year:
                self.shareholder_yield[equity.id] = measure.get_shareholder_yield(equity, market_cap=market_cap)
            else:
                self.shareholder_yield[equity.id] = measure.get_shareholder_yield(equity, year=year, market_cap=market_cap)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def sort_equities(self):
        """
        Sort the list according to the value of the factor.

        Some factors requires that the sorting order is reversed.
        @return Nothing
        """
        try:
            self.price_to_book_ratio = WhatWorksOnWallStreet.order_dictionary_by_value(self.price_to_book_ratio)
            self.price_to_earnings_ratio = WhatWorksOnWallStreet.order_dictionary_by_value(self.price_to_earnings_ratio)
            self.price_to_sales = WhatWorksOnWallStreet.order_dictionary_by_value(self.price_to_sales)
            self.ebitda_ev_ratio = WhatWorksOnWallStreet.order_dictionary_by_value(self.ebitda_ev_ratio, reverse=True)
            self.price_to_cash_flow = WhatWorksOnWallStreet.order_dictionary_by_value(self.price_to_cash_flow)
            self.shareholder_yield = WhatWorksOnWallStreet.order_dictionary_by_value(self.shareholder_yield, reverse=True)
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def score_stocks(self):
        """
        The method scores the stocks by assigning a percentile ranking score.

        The method scores the stocks by assigning a percentile ranking score from 1 to 100 for each
        stock present in the dictionary. The score is given so that the stock in the highest 1% position in the
        dictionary receive a rank of 100; viceversa if in the lowest 1% it received a score of 1.
        Some factors requires that the sorting order is reversed.
        @return Nothing
        """
        WhatWorksOnWallStreet.percentile_scoring(self.price_to_book_ratio)
        WhatWorksOnWallStreet.percentile_scoring(self.price_to_earnings_ratio)
        WhatWorksOnWallStreet.percentile_scoring(self.price_to_sales)
        WhatWorksOnWallStreet.percentile_scoring(self.ebitda_ev_ratio)
        WhatWorksOnWallStreet.percentile_scoring(self.price_to_cash_flow)
        WhatWorksOnWallStreet.percentile_scoring(self.shareholder_yield)

    @staticmethod
    def percentile_scoring(input_dct):
        """
        Once the list has been sorted, we assign a percentile ranking (from 1 to 100) for each stock in the list.
        @return Nothing
        """
        try:
            if input_dct is not None:
                size = len(input_dct)
                step = size / 100
                counter = 1
                for index, (key, value) in enumerate(input_dct.items()):
                    cps = counter * step
                    if index >= cps:
                        counter += 1
                    input_dct[key] = 100 - counter + 1
                    # input_dct[key] = {value, {'score': 100 - counter + 1}}
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def get_all_factors_score(self):
        """
        Once all the factors are ranked, we add up all their rankings to generate an all factors score.

        The stocks in the all factors dictionary are sorted so that the highest score are the dist in the dictionary.
        Those with the highest scores are assigned to decile 1, those with lowest scores are assigned to decile 10.
        @return the list with all the factors score.
        """
        try:
            self.all_factors_dict = {}

            for (pb_key, pb_value) in self.price_to_book_ratio.items():
                score = self.price_to_book_ratio[pb_key] + \
                        self.price_to_earnings_ratio[pb_key] + \
                        self.price_to_sales[pb_key] + \
                        self.ebitda_ev_ratio[pb_key] + \
                        self.price_to_cash_flow[pb_key] + \
                        self.shareholder_yield[pb_key]

                self.all_factors_dict[pb_key] = score

            self.all_factors_dict = WhatWorksOnWallStreet.order_dictionary_by_value(self.all_factors_dict, reverse=True)
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def get_best_decile(self):
        """
        It returns a limited dictionary just with the best decile from the all factors dictionary.
        return the best decile dictionary
        """
        try:
            size = len(self.all_factors_dict)
            if size == 0:
                return {}

            best_decile = int(size / 10)
            self.best_decile_dict = dict(itertools.islice(self.all_factors_dict.items(), best_decile))
            return self.best_decile_dict

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def get_worst_decile(self):
        """
        It returns a limited dictionary just with the worst decile from the all factors dictionary.
        return the worst decile dictionary
        """
        try:
            size = len(self.all_factors_dict)
            if size == 0:
                return {}

            worst_decile = size - int(size / 10)
            self.worst_decile_dict = dict(itertools.islice(self.all_factors_dict.items(), worst_decile, None))
            return self.worst_decile_dict

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def reset_factors(self):
        """
        It resets the factors used to store the companies economic data
        @return Nothing
        """
        try:
            self.price_to_book_ratio = {}
            self.price_to_earnings_ratio = {}
            self.price_to_sales = {}
            self.ebitda_ev_ratio = {}
            self.price_to_cash_flow = {}
            self.shareholder_yield = {}

            self.all_factors_dict = {}

            self.best_decile_dict = {}
            self.worst_decile_dict = {}

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    # def calculate_price_variations(self, input_data=None):
    #     """
    #     This method decides if the price variation for example in hte last 6-7 months is worth to be considered.
    #     @param input_data the set of equities to investigate.
    #     @return Nothing
    #     """
    #     try:
    #         if not input_data:
    #             input_data = self.best_decile_dict
    #
    #         dates = fund_utils.gm.get_dates_for_period_in_days(182, self.year, self.month)
    #
    #         self.price_appreciation_dict = {}
    #         self.price_distribution_dict = {}
    #
    #         for equity_id, equity_score in input_data.items():
    #             equity = db_mngr.query_equity_by_id(equity_id=equity_id)
    #
    #             prices_6_months = self.get_last_six_months_prices(equity, dates)
    #
    #             if not prices_6_months:
    #                 continue
    #
    #             # price derivative
    #             diff_prices = np.diff(prices_6_months)
    #             if diff_prices.size > 0:
    #                 mean = np.mean(diff_prices)
    #                 variance = np.var(diff_prices)
    #             else:
    #                 mean = 0
    #                 variance = 1
    #
    #             if variance == 0:
    #                 mean = 0
    #                 variance = 1
    #
    #             # price appreciation  (last_value / initial_value) - 1
    #             self.price_appreciation_dict[equity_id] = (prices_6_months[-1]/prices_6_months[0] - 1)
    #             self.price_distribution_dict[equity_id] = mean / variance
    #
    #         return
    #
    #     except Exception as e:
    #         log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    # def get_last_six_months_prices(self, equity, dates):
    #     """
    #     Given the equity in input it returns the prices for the last six months.
    #     @param equity the equity we are interested in the dates
    #     @param dates, the dates among which the prices will be scraped (dates is a dictionary(
    #     @return the vector with the prices, empty if it was not successful
    #     """
    #     if equity.symbol_1 in self.list_stocks_to_exclude:
    #         return []
    #
    #     prices = methods.get_prices_in_range_of_dates(equity, dates)
    #
    #     prices_in_range = []
    #     for price in prices:
    #         prices_in_range.append(price.close)
    #
    #     # # exclude the equity if when I want to buy, the price of its share is higher than what I can afford to pay.
    #     # if prices_in_range[-1] > self.max_price_share:
    #     #     return []
    #
    #     return prices_in_range

    # def score_price_variations(self):
    #     try:
    #         # order the two scores
    #         self.price_appreciation_dict = \
    #             WhatWorksOnWallStreet.order_dictionary_by_value(self.price_appreciation_dict, reverse=True)
    #         self.price_distribution_dict = \
    #             WhatWorksOnWallStreet.order_dictionary_by_value(self.price_distribution_dict, reverse=True)
    #
    #         # assign the score the lowest the better, 0 is the best score
    #         for index, (key, value) in enumerate(self.price_appreciation_dict.items()):
    #             self.price_appreciation_dict[key] = index
    #         for index, (key, value) in enumerate(self.price_distribution_dict.items()):
    #             self.price_distribution_dict[key] = index
    #
    #         # sum up the scores of the two dictionaries
    #         self.price_variations_score = {}
    #         for (pa_key, pa_value) in self.price_appreciation_dict.items():
    #             score = self.price_appreciation_dict[pa_key] + self.price_distribution_dict[pa_key]
    #
    #             self.price_variations_score[pa_key] = score
    #
    #         # sort the newly generated dictionary, the lowest the best
    #         self.price_variations_score = \
    #             WhatWorksOnWallStreet.order_dictionary_by_value(self.price_variations_score, reverse=False)
    #
    #     except Exception as e:
    #         log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
