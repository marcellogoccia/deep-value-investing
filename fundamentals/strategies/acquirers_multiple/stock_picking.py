from fundamentals.strategies.basic_strategy.stock_picking import StockPicking
from fundamentals.strategies.acquirers_multiple.acquirers_multiple import AcquirersMultiple

from utilities.pickle_manager import PickleManager as pckl
from utilities import log
from utilities.common_methods import getDebugInfo


class StockPickingForAcquirersMultiple(StockPicking):

    def __init__(self, **kwargs):
        """
        Constructor
        """
        StockPicking.__init__(self, **kwargs)
        self.am = AcquirersMultiple()

        max_num_equities = kwargs.get('max_number_of_equities_invested_in')
        self.am.set_number_of_equities_invested_in(max_num_equities)

    def set_investing_year(self, year):
        """
        It sets the year of the testing
        @param year the year to set
        @return  Nothing
        """
        self.year = year
        self.am.year = year

    def set_investing_month(self, month):
        """
        It sets the month of the testing
        @param month the month to set
        @return  Nothing
        """
        self.month = month
        self.am.month = month

    def set_number_of_equities_invested_in(self, max_number_of_equities_invested_in=25):
        """
        It sets the maximum number of stocks I would like to invest at the same time.

        It no number is passed, the default value is proved equal to 25.
        @param max_number_of_equities_invested_in
        @return Nothing
        """
        self.num_stocks_to_invest_in = max_number_of_equities_invested_in
        self.am.set_number_of_equities_invested_in(max_number_of_equities_invested_in)

    def set_factor(self, equity, year=None, market_cap=None):
        """
        It sets the factor according to the strategy used.
        @param equity the equity to get the factor from
        @param year the year when to apply the factor
        @param market_cap the market ap of the equity under examination
        @return Nothing
        """
        try:
            # In here I get the acquirer's multiple value and add it to the existing dictionary.
            self.am.set_value(equity, market_cap=market_cap)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def get_scores_investing_stocks(self):
        """
        It sets the scores according to the strategy used.
        @return The scores of the stocks to invest in.
        """
        try:
            # At the end sort them.
            self.am.sort_equities()

            import itertools
            investing_stocks = dict(itertools.islice(self.am.acquirers_multiple.items(), self.num_stocks_to_invest_in))
            return investing_stocks

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def save(self, path=None, country=None):
        """
        Store some data useful so that we do not need to repeat all the test if interrupting.
        """
        try:
             pckl.save(self.am.acquirers_multiple, f'{self.year}_{country}_acquirers_multiple', path=path)
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def load(self, path=None, country=None):
        """
        Retrieve previouly save data to speed up some testing.
        @return Nothing
        """
        try:
            import os
            self.am.acquirers_multiple = pckl.load(os.path.join(path, f'{self.year}_{country}_acquirers_multiple.pkl'))
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


def main():
    try:
        investing_year = None  # None for the last most updated data

        # initialise the algorithm which is entitled to pick the stocks of interest.
        stock_picking = StockPickingForAcquirersMultiple()
        stock_picking.set_investing_year(investing_year)
        stock_picking.set_path_pickles("../../../downloads/test/")
        stock_picking.set_country("Austria")

        stock_picking.run_algorithm()

    except Exception as e:
        log.error(f"There is a problem in the code! : {e}\n{getDebugInfo()}")


if __name__ == "__main__":
    # execute only if run as a script
    main()


