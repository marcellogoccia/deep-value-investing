import numpy as np

from utilities.common_methods import Methods as methods
from utilities.common_methods import getDebugInfo
from utilities import log
import fundamentals.miscellaneous as fund_utils
from data_storing.assets.database_manager import DatabaseManager as db_mngr


class Strategy:

    def __init__(self):

        self.num_stocks_to_invest_in = None
        self.year = None
        self.month = None
        self.countries = None

        self.dates = None
        self.max_price_share = None

        self.list_stocks_to_exclude = fund_utils.gv.list_stocks_to_exclude

        self.equities_momentum = []

        self.market_appreciation = {}
        self.extra_factor = {}

        self.price_variations = {}
        self.price_variations_score = {}

    def set_number_of_equities_invested_in(self, max_number_of_equities_invested_in=25):
        """
        It sets the maximum number of stocks I would like to invest at the same time.

        It no number is passed, the default value is proved equal to 25.
        @param max_number_of_equities_invested_in
        @return Nothing
        """
        self.num_stocks_to_invest_in = max_number_of_equities_invested_in

    def calculate_price_variations(self, input_data=None, equities=None):
        """
        This method decides if the price variation for example in the last 6-7 months is worth to be considered.
        @param input_data the set of equities to investigate.
        @return Nothing
        """
        try:
            year_dates = fund_utils.gm.get_dates_for_period_in_days(365, self.year, self.month)
            six_months_dates = fund_utils.gm.get_dates_for_period_in_days(182, self.year, self.month)

            from backtesting.run_me_to_backtest import methods_momentum

            self.price_variations = dict()

            #self.compute_market_appreciation(year_dates, equities)
            #self.compute_all_country_market_prices_appreciation(year_dates,)

            for method_momentum in methods_momentum:
                self.price_variations[method_momentum] = {}

            self.equities_momentum = []
            for equity_id, equity_score in input_data.items():
                equity = db_mngr.query_equity_by_id(equity_id=equity_id)
                self.equities_momentum.append(equity_id)

                prices_6_months = self.get_prices_in_range_of_dates(equity, six_months_dates)

                if not prices_6_months:
                    continue

                # price appreciation  (last_value / initial_value) - 1
                if 'price_appreciation' in methods_momentum:
                    self.price_variations['price_appreciation'][equity_id] = (prices_6_months[-1]/prices_6_months[0] - 1)
                if 'price_distribution' in methods_momentum:
                    self.price_variations['price_distribution'][equity_id] = Strategy.compute_price_distribution(prices_6_months)
                if 'sma' in methods_momentum:
                    self.price_variations['sma'][equity_id] = Strategy.compute_sma_ratio(prices_6_months)
                if 'appreciation_to_market' in methods_momentum:
                    self.price_variations['appreciation_to_market'][equity_id] = Strategy.compute_appreciation_related_to_market(prices_6_months, equity.country, self.market_appreciation)

            return

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    @staticmethod
    def compute_price_distribution(series_of_prices):
        """
        Given a list of prices, the method returns the distribution of the prices.
        The distribution is computed by dividing the mean of the prices by their variance
        @param series_of_prices a series of prices.
        @return the price distribution
        """
        try:
            # price derivative
            diff_prices = np.diff(series_of_prices)
            if diff_prices.size > 0:
                mean = np.mean(diff_prices)
                variance = np.var(diff_prices)
            else:
                mean = 0
                variance = 1

            if variance == 0:
                mean = 0
                variance = 1

            price_distribution = mean / variance
            return price_distribution
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    @staticmethod
    def compute_sma_ratio(series_of_prices):
        """
        Given a list of prices, the method returns the ratio between single moving average of the sequence and the
        last price value. The higher the better.
        The sma is obtained computing the average of the prices.
        @param series_of_prices a series of prices.
        @return the sma ratio
        """
        try:
            # price average
            average_prices = np.average(series_of_prices)
            sma_ratio = series_of_prices[-1] / average_prices - 1
            return sma_ratio
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def compute_all_country_market_prices_appreciation(self, dates):
        """
        The method scans through all the market to find out how much the market appreciated in the dates passed as input.
        @param dates the start and end date of the appreciation
        """
        try:
            if not self.countries:
                equities = db_mngr.query_all_equities()
                country = 'all_countries'
                self.market_appreciation[country] = self.compute_market_appreciation(equities, dates, country)
            else:
                if isinstance(self.countries, list):
                    equities = []
                    for country in self.countries:
                        equities += db_mngr.query_all_equities_by(country=country)
                        self.market_appreciation[country] = self.compute_market_appreciation(equities, dates, country)

                else:
                    equities = db_mngr.query_all_equities_by(country=self.countries)
                    self.market_appreciation[self.countries] = self.compute_market_appreciation(equities,
                                                                                              dates, self.countries)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def compute_market_appreciation(self, equities, dates, country):
        """
        The method computes the market appreciation
        @param equities the equities on which to compute the market appreciation
        @param dates the start and end date of the appreciation
        @param country the country we are computing the market appreciation.
        @return the value of the market appreciation
        """
        try:
            higher_threshold = 10
            lower_threshold = 0.05

            sum_all_appreciations = 0
            counter = 0
            for temp_equity in equities:
                prices_within_dates = self.get_prices_in_range_of_dates(temp_equity, dates)
                if not prices_within_dates:
                    continue
                try:
                    price_ratio = prices_within_dates[-1] / prices_within_dates[0]
                    # if the price ratio is within the threshold it is ok to add to the market ratios
                    if lower_threshold < price_ratio < higher_threshold:
                        sum_all_appreciations += price_ratio
                        counter += 1
                except ZeroDivisionError:
                    continue

            market_appreciation = sum_all_appreciations / counter
            market_appreciation_percentage = round((market_appreciation - 1) * 100, 2)
            log.info(f"The {country} market appreciation for the year {self.year} is "
                     f"{market_appreciation_percentage}%")
            self.market_appreciation[country] = market_appreciation
            return market_appreciation

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
            return None

    @staticmethod
    def compute_appreciation_related_to_market(series_of_prices, equity_country, market_appreciation):
        """
        THe methods returns the amount the equities appreciated with respect to its all market.
        @param series_of_prices the series of prices of the considered equity.
        @param equity_country the country if the processed equity
        @param market_appreciation is a dictionary where keys are the countries and the values are the market appreciation.
        @return The appreciation value with respect to the whole market.
        """
        try:
            equity_appreciation = series_of_prices[-1] / series_of_prices[0]
            ratio_appreciations = equity_appreciation / market_appreciation[equity_country]
            return ratio_appreciations

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def get_prices_in_range_of_dates(self, equity, dates):  #  TODO : check where dates were taken from, modify from 6 months to a year for investigation
        """
        Given the equity in input it returns the prices for the last six months.
        @param equity the equity we are interested in the dates
        @param dates, the dates among which the prices will be scraped (dates is a dictionary(
        @return the vector with the prices, empty if it was not successful
        """
        if equity.symbol_1 in self.list_stocks_to_exclude:
            return []

        prices = methods.get_prices_in_range_of_dates(equity, dates)

        prices_in_range = []
        for price in prices:
            prices_in_range.append(price.close)

        return prices_in_range

    def score_price_variations(self):
        try:
            momentum_methods = list(self.price_variations.keys())

            for method in momentum_methods:
                self.price_variations[method] = \
                    Strategy.order_dictionary_by_value(self.price_variations[method], reverse=True)

            # assign the score, the lowest the better, 0 is the best score
            for method in momentum_methods:
                for index, (equity_id, value) in enumerate(self.price_variations[method].items()):
                    self.price_variations[method][equity_id] = index

            self.price_variations_score = {}

            num_equities = len(self.equities_momentum)
            average_score = num_equities // 2

            self.price_variations_score = {}

            for equity_id in self.equities_momentum:
                sum_score = 0
                for method in momentum_methods:
                    sum_score += self.price_variations[method].get(equity_id, average_score)

                self.price_variations_score[equity_id] = sum_score

            self.price_variations_score = Strategy.order_dictionary_by_value(self.price_variations_score, reverse=False)

            return

            # #####
            # # order the two scores
            # self.price_appreciation_dict = Strategy.order_dictionary_by_value(self.price_appreciation_dict, reverse=True)
            # self.price_distribution_dict = Strategy.order_dictionary_by_value(self.price_distribution_dict, reverse=True)
            #
            # # assign the score, the lowest the better, 0 is the best score
            # for index, (key, value) in enumerate(self.price_appreciation_dict.items()):
            #     self.price_appreciation_dict[key] = index
            # for index, (key, value) in enumerate(self.price_distribution_dict.items()):
            #     self.price_distribution_dict[key] = index
            #
            # # sum up the scores of the two dictionaries
            # self.price_variations_score = {}
            # for (pa_key, pa_value) in self.price_appreciation_dict.items():
            #     score = self.price_appreciation_dict[pa_key] + self.price_distribution_dict[pa_key]
            #
            #     self.price_variations_score[pa_key] = score
            #
            # # sort the newly generated dictionary, the lowest the best
            # self.price_variations_score = \
            #     Strategy.order_dictionary_by_value(self.price_variations_score, reverse=False)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    @staticmethod
    def preserve_percentage_of_dictionary(input_dict):
        try:
            size = len(input_dict)
            upper_limit = int(0.01 * size) + 1

            # the following will only select the highest 1% of the list!
            return input_dict[0:upper_limit]

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    @staticmethod
    def sort_getter(item, reverse=False):
        value = item[1]
        if value is None:
            if reverse:
                return -1000
            else:
                return 1000
        return value

    @staticmethod
    def order_dictionary_by_value(input_dict, reverse=False):
        try:
            sorted_dict = {}
            from functools import partial

            temp_sorted = sorted(input_dict.items(),
                                 key=partial(Strategy.sort_getter, reverse=reverse), reverse=reverse)

            for k, v in temp_sorted:
                sorted_dict[k] = v
            return sorted_dict
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def reset_factors(self):
        """
        It resets the factors used to store the companies economic data
        @return Nothing
        """
        try:
            self.market_appreciation = {}
            self.extra_factor = {}

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
