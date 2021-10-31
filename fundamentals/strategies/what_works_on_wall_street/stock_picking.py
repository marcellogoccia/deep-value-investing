from fundamentals.strategies.basic_strategy.stock_picking import StockPicking
from fundamentals.strategies.what_works_on_wall_street.what_works_on_wall_street import WhatWorksOnWallStreet

from utilities.common_methods import getDebugInfo
from utilities import log
from utilities.pickle_manager import PickleManager as pckl


class StockPickingForWhatWorksWallStreet(StockPicking):

    def __init__(self, **kwargs):
        """
        Constructor
        """
        StockPicking.__init__(self, **kwargs)
        self.wwows = WhatWorksOnWallStreet()

        max_num_equities = kwargs.get('max_number_of_equities_invested_in')
        self.wwows.set_number_of_equities_invested_in(max_num_equities)

    def set_investing_year(self, year):
        """
        It sets the year of the testing
        @param year the year to set
        @return  Nothing
        """
        try:
            self.year = year
            self.wwows.year = year
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def set_investing_month(self, month):
        """
        It sets the month of the testing
        @param month the month to set
        @return  Nothing
        """
        try:
            self.month = month
            self.wwows.month = month
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def set_factor(self, equity, year=None, market_cap=None):
        """
        It sets the factor according to the strategy used.
        @param equity the equity to get the factor from
        @param year the year when to apply the factor
        @param market_cap the market ap of the equity under examination
        @return Nothing
        """
        try:
            # In here I get the what work on wall street value and add it to the existing dictionary.
            self.wwows.set_value(equity, year=self.year, market_cap=market_cap)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def get_scores_investing_stocks(self):
        """
        It sets the scores according to the strategy used.
        @return The scores of the stocks to invest in.
        """
        try:
            # At the end sort them.
            self.wwows.sort_equities()
            self.wwows.score_stocks()
            self.wwows.get_all_factors_score()
            self.wwows.get_best_decile()
            self.wwows.get_worst_decile()  # the worst decile considered for testing or for shorting.
            self.wwows.calculate_price_variations(self.wwows.best_decile_dict)
            self.wwows.score_price_variations()

            # return only a subset of scores.
            import itertools
            chosen_equities = dict(itertools.islice(self.wwows.price_variations_score.items(), self.num_stocks_to_invest_in))
            return chosen_equities

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def save(self, path=None, country=None):
        """
        Store some data useful so that we do not need to repeat all the test if interrupting.
        """
        try:
            pckl.save(self.wwows.price_to_book_ratio, f'{self.year}_{country}_price_to_book_ratio', path=path)
            pckl.save(self.wwows.price_to_earnings_ratio, f'{self.year}_{country}_price_to_earnings_ratio', path=path)
            pckl.save(self.wwows.price_to_sales, f'{self.year}_{country}_price_to_sales', path=path)
            pckl.save(self.wwows.ebitda_ev_ratio, f'{self.year}_{country}_ebitda_ev_ratio', path=path)
            pckl.save(self.wwows.price_to_cash_flow, f'{self.year}_{country}_price_to_cash_flow', path=path)
            pckl.save(self.wwows.shareholder_yield, f'{self.year}_{country}_shareholder_yield', path=path)
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def load(self, path=None, country=None):
        """
        Retrieve previouly save data to speed up some testing.
        @return Nothing
        """
        try:
            import os
            self.wwows.price_to_book_ratio = pckl.load(os.path.join(path, f'{self.year}_{country}_price_to_book_ratio.pkl'))
            self.wwows.price_to_earnings_ratio = pckl.load(os.path.join(path, f'{self.year}_{country}_price_to_earnings_ratio.pkl'))
            self.wwows.price_to_sales = pckl.load(os.path.join(path, f'{self.year}_{country}_price_to_sales.pkl'))
            self.wwows.ebitda_ev_ratio = pckl.load(os.path.join(path, f'{self.year}_{country}_ebitda_ev_ratio.pkl'))
            self.wwows.price_to_cash_flow = pckl.load(os.path.join(path, f'{self.year}_{country}_price_to_cash_flow.pkl'))
            self.wwows.shareholder_yield = pckl.load(os.path.join(path, f'{self.year}_{country}_shareholder_yield.pkl'))
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


def main():
    try:
        investing_year = None  # None for the last most updated data

        # initialise the algorithm which is entitled to pick the stocks of interest.
        stock_picking = StockPickingForWhatWorksWallStreet()
        stock_picking.set_investing_year(investing_year)
        stock_picking.set_path_pickles("../../../downloads/test/")
        stock_picking.set_country("Austria")

        stock_picking.run_algorithm()

    except Exception as e:
        log.error(f"There is a problem in the code! : {e}\n{getDebugInfo()}")


if __name__ == "__main__":
    # execute only if run as a script
    main()