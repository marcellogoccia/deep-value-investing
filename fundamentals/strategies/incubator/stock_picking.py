import os
import math

from fundamentals.strategies.basic_strategy.stock_picking import StockPicking
from fundamentals.strategies.incubator.melting_pot import MeltingPot

from utilities.pickle_manager import PickleManager as pckl
from utilities import log
from utilities.common_methods import getDebugInfo


class StockPickingIncubator(StockPicking):

    def __init__(self, **kwargs):
        StockPicking.__init__(self, **kwargs)

        self.mp = MeltingPot()
        max_num_equities = kwargs.get('max_number_of_equities_invested_in')
        self.mp.set_number_of_equities_invested_in(max_num_equities)
        self.mp.countries = self.countries

    def set_investing_year(self, year):
        """
        It sets the year of the testing
        @param year the year to set
        @return  Nothing
        """
        self.year = year
        self.mp.year = year

    def set_investing_month(self, month):
        """
        It sets the month of the testing
        @param month the month to set
        @return  Nothing
        """
        self.month = month
        self.mp.month = month

    def set_number_of_equities_invested_in(self, max_number_of_equities_invested_in=25):
        """
        It sets the maximum number of stocks I would like to invest at the same time.

        It no number is passed, the default value is proved equal to 25.
        @param max_number_of_equities_invested_in
        @return Nothing
        """
        self.num_stocks_to_invest_in = max_number_of_equities_invested_in
        self.mp.set_number_of_equities_invested_in(max_number_of_equities_invested_in)

    def set_investing_dates(self, dates):
        """
        It sets the investing dates, the starting and ending investing dates for the strategy
        @param dates the dates where to invest
        @return Nothing
        """
        self.dates = dates
        self.mp.dates = dates

    def set_max_price_per_share(self, max_price_share):
        """
        It sets the maximum price we are keen to pay for a single share.
        We may not want too spend more than this amount because we do not have enough money.
        @param max_price_share the maximum amount ot spend on a single share.
        @return Nothing
        """
        self.max_price_share = max_price_share
        self.mp.max_price_share = max_price_share

    def set_factor(self, equity, year=None, market_cap=None):
        """
        It sets the factor according to the strategy used.
        @param equity the equity to get the factor from
        @param year the year when to apply the factor
        @param market_cap the market ap of the equity under examination
        @return Nothing
        """
        try:
            # In here I get the melting pot value and add it to the existing dictionary.
            self.mp.set_value(equity, market_cap=market_cap)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def get_scores_investing_stocks(self):
        """
        It sets the scores according to the strategy used.
        @return The scores of the stocks to invest in.
        """
        try:
            # At the end sort them.
            self.mp.sort_equities()
            self.mp.score_equities()

            # remove equity if the price do not match my strategy
            self.mp.discriminate_on_price()

            import itertools

            if self.momentum:
                num_shares_momentum = math.ceil(len(self.mp.global_score) * self.percentage_momentum)
                # remove the eccess of equities, just leave the number of schare equal to num_shares_momentum
                self.mp.global_score = dict(itertools.islice(self.mp.global_score.items(), num_shares_momentum))

                self.mp.calculate_price_variations(self.mp.global_score)
                self.mp.score_price_variations()
                self.mp.global_score = self.mp.price_variations_score

            investable_stocks = dict(itertools.islice(self.mp.global_score.items(), self.num_stocks_to_invest_in))
            return investable_stocks

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def compute_market_appreciation(self, equities, country):
        """
        It calls the strategy method to compute the appreciation of the whole market.
        #@param dates the dates from when to when calculate the appreciation
        @param equities the list of equities representing hte market.
        @param country the country we are computing the market appreciation.
        @return the value computed.
        """
        return self.mp.compute_market_appreciation(equities, self.dates, country)

    def save(self, path=None, country=None):
        """
        Store some data useful so that we do not need to repeat all the test if interrupting.
        """
        try:
            pckl.save(self.mp.am.acquirers_multiple, f'{self.year}_{country}_acquirers_multiple', path=path)
            pckl.save(self.mp.wwows.price_to_book_ratio, f'{self.year}_{country}_price_to_book_ratio', path=path)
            pckl.save(self.mp.wwows.price_to_earnings_ratio, f'{self.year}_{country}_price_to_earnings_ratio', path=path)
            pckl.save(self.mp.wwows.price_to_sales, f'{self.year}_{country}_price_to_sales', path=path)
            pckl.save(self.mp.wwows.ebitda_ev_ratio, f'{self.year}_{country}_ebitda_ev_ratio', path=path)
            pckl.save(self.mp.wwows.price_to_cash_flow, f'{self.year}_{country}_price_to_cash_flow', path=path)
            pckl.save(self.mp.wwows.shareholder_yield, f'{self.year}_{country}_shareholder_yield', path=path)
            pckl.save(self.mp.p9p.piotrosky_score, f'{self.year}_{country}_piotrosky_score', path=path)
            pckl.save(self.mp.extra_factor, f'{self.year}_{country}_extra_factor', path=path)
            pckl.save(self.mp.market_appreciation, f'{self.year}_{country}_market_appreciation', path=path)

            self.mp.am.reset_factors()
            self.mp.wwows.reset_factors()
            self.mp.p9p.reset_factors()
            self.mp.reset_factors()

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def load(self, path=None, country=None):
        """
        Retrieve previously save data to speed up some testing.
        @return Nothing
        """
        try:
            from backtesting.run_me_to_backtest import factors

            for factor in factors:
                self.load_factor(factor, path, country)

            # Extra variables to load.
            file_name = f'{self.year}_{country}_market_appreciation.pkl'
            self.mp.market_appreciation.update(pckl.load(os.path.join(path, file_name)))

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def load_factor(self, factor_name, path=None, country=None):
        try:
            name_pkl = f'{self.year}_{country}_{factor_name}.pkl'
            self.mp.strategy_factors[factor_name].update(pckl.load(os.path.join(path, name_pkl)))
        except Exception as e:
            log.error(f"There is a problem in the code when loading {factor_name} factor!: {e}\n{getDebugInfo()}")

    def lazy_initialization_variables(self, **kwargs):
        """
        If needed a lazy initialization will initialize the variables without breaking the code.
        @param **kwargs any needed variables.
        @return Nothing
        """
        try:
            from backtesting.run_me_to_backtest import factors
            for factor_name in factors:
                self.mp.strategy_factors[factor_name] = {}
        except Exception as e:
            log.error(f"There is a problem in the code when loading a factor!: {e}\n{getDebugInfo()}")


def main():
    try:
        investing_year = None  # None for the last most updated data

        # initialise the algorithm which is entitled to pick the stocks of interest.
        stock_picking = StockPickingIncubator()
        stock_picking.set_investing_year(investing_year)
        stock_picking.set_path_pickles("../../../downloads/test/")
        stock_picking.set_country("Austria")

        stock_picking.run_algorithm()

    except Exception as e:
        log.error(f"There is a problem in the code! : {e}\n{getDebugInfo()}")


if __name__ == "__main__":
    # execute only if run as a script
    main()


