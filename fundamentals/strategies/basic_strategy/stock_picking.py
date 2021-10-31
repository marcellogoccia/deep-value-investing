import time
from utilities.common_methods import getDebugInfo
from utilities import log
from utilities.common_methods import Methods as methods
from utilities.globals import websites

from data_storing.assets.database_manager import DatabaseManager as db_mngr

import fundamentals.miscellaneous as fund_utils
from fundamentals.measures import market_cap as mc

from website_scraping.investing_dot_com.scraping_prices import ScrapingPrices

minimum_market_cap = 15.0 * 1000000  # al least 15M market cap.
maximum_market_cap = 1000 * 1000.0 * 1000000000  # maximum 1T market cap  (100 000 000  000 000)


class StockPicking:

    def __init__(self, **kwargs):
        """
        Constructor
        """
        self.year = None
        self.month = None

        if kwargs.get("scraping_prices_from_internet"):
            self.scraping_prices = fund_utils.gm.open_browser_driver()
        else:
            self.scraping_prices = None

        self.strategy = None
        self.dates = None
        self.max_price_share = 0
        self.counter = 0

        self.score_or_rank = kwargs.get("score_or_rank")
        self.countries = kwargs.get("countries")
        self.momentum = kwargs.get("enable_momentum")
        self.pickle_path = kwargs.get("path_pickles")
        self.num_stocks_to_invest_in = kwargs.get('max_number_of_equities_invested_in')
        self.percentage_momentum = kwargs.get('percentage_momentum')

    def initialise_strategy(self):
        """
        Do here any operations needed to initialise the algorithm.
        :return:
        """
        pass

    def set_investing_year(self, year):
        """
        It sets the year of the testing
        @param year the year to set
        @return  Nothing
        """
        self.year = year

    def set_investing_month(self, month):
        """
        It sets the month of the testing
        @param month the month to set
        @return  Nothing
        """
        self.month = month

    def set_investing_dates(self, dates):
        """
        It sets the investing dates, the starting and ending investing dates for the strategy
        @param dates the dates where to invest
        @return Nothing
        """
        self.dates = dates

    def set_max_price_per_share(self, max_price_share):
        """
        It sets the maximum price we are keen to pay for a single share.
        We may not want too spend more than this amount because we do not have enough money.
        @param max_price_share the maximum amount ot spend on a single share.
        @return Nothing
        """
        self.max_price_share = max_price_share

    def set_percentage_momentum(self, percentage_momentum=0.1):
        """
        It sets the percentage of the stocks to be included for the momentum calculation
        The percentage is expresses as a float number.
        If no number is passed, the default value is proved equal to 0.1
        A value of 1 means all included.
        @param percentage_momentum the percentage to use.
        @return Nothing
        """
        self.percentage_momentum = percentage_momentum

    def set_path_pickles(self, path):
        """
        It sets the path where the pickle files will be stored.
        @param path the path where to store the pickle files
        @return Nothing
        """
        self.pickle_path = path

    def set_country(self, countries=None):
        """
        It set the country where the algorithm will look for interesting equities.

        It no country is passed, the algorithm will scan for everything.
        @param country
        @return Nothing
        """
        self.countries = countries

    def set_number_of_equities_invested_in(self, max_number_of_equities_invested_in=25):
        """
        It sets the maximum number of stocks I would like to invest at the same time.

        It no number is passed, the default value is proved equal to 25.
        @param max_number_of_equities_invested_in
        @return Nothing
        """
        self.num_stocks_to_invest_in = max_number_of_equities_invested_in

    def use_momentum(self, use_it):
        """
        When use_it is true we are looking at the price appreciation of the last months ofr the equity
        @param use_it if true the momenti is used
        @return Nothing
        """
        self.momentum = use_it

    def set_strategy_class(self, strategy):
        self.strategy = strategy

    def get_all_equities_based_on_countries(self):
        """
        The method parses the list of countries to extract all the equities belonging to the country of interest.
        @return the equities of interest.
        """
        try:

            if not self.countries:
                equities = db_mngr.query_all_equities()
            else:
                if isinstance(self.countries, list):
                    equities = []
                    for country in self.countries:
                        equities += db_mngr.query_all_equities_by(country=country)
                else:
                    equities = db_mngr.query_all_equities_by(country=self.countries)

            return equities
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def run_algorithm(self):
        """
        The method scans through the equities to find the best ones
        @return The equities found.
        """
        try:
            # first step consists in applying the composite value factor two to all the equities, second step is
            # to rank all the equities according to the factors and get the equities in the first decile (best 10%).
            # Then select the equities which have the best 6-month momentum.

            # ############
            # # Here is the call to the algorithm to score the equities country by country
            # ############
            if 'score' in self.score_or_rank:
                self.score_equities_country_by_country()

            #############
            # # Here is the call to the algorithm to rank the equities for all the available countries.
            #############
            if 'rank' in self.score_or_rank:
                return self.rank_equities_country_by_country()

            return []

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
            return []

    def score_equities_country_by_country(self):
        """
        Here is the algorithm which calls the algorithm to score the equities country by country
        @return Nothing
        """
        try:
            start_time_process_equities = time.monotonic()
            print(f"Start scoring!!")

            equities = []
            for country in self.countries:

                log.info(f"Getting scores for the country {country} in the year {self.year}")
                equities = db_mngr.query_all_equities_by(country=country)

                # ############
                # MARKET APPRECIATION CALCULATION
                # ############
                log.info(f"Starting calculating the market appreciation for {country}")
                self.compute_market_appreciation(equities, country)
                log.info(f"Done market appreciation!")

                counter = 0
                for equity in equities:
                    # #############
                    self.meet_the_conditions(equity)
                    # #############
                    counter += 1
                    if counter % 200 == 0:
                        log.info(f"So far done {counter} equities of {country} in the year {self.year}")

                self.save_data(path=self.pickle_path, country=country)

            elapsed_time_process_equities = time.monotonic() - start_time_process_equities
            log.info(f"It took {elapsed_time_process_equities} seconds to process all of the {len(equities)} "
                     f"available equities")

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def rank_equities_country_by_country(self):
        """
        Here is the algorithm which calls the algorithm to rank the equities for all the available countries.
        @return Nothing
        """
        try:
            start_time_process_equities = time.monotonic()

            print(f"Start ranking!!")

            self.lazy_initialization_variables()

            for country in self.countries:
                self.load_data(path=self.pickle_path, country=country)

            log.info(f"Started ranking for the year {self.year}")
            # #############
            chosen_equities, score_equities = self.rank_all_equities()
            # #############

            elapsed_time_process_equities = time.monotonic() - start_time_process_equities
            print(f"There are {len(chosen_equities)} equities that could be included"
                  f" in my portfolio.\nIt took {elapsed_time_process_equities} to process "
                  f"all of the scores available")

            return chosen_equities

        except Exception as e:
                log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def meet_the_conditions(self, equity):
        """
        It evaluates some conditions, and if satisfied, the equity could be interesting for an investing approach
        @param the equity under examination
        @return Nothing
        """
        try:
            if fund_utils.gm.is_equity_undesirable(equity):
                return False

            if self.year is None:
                year = methods.get_last_year()
            else:
                year = self.year

            # this is just to test the balance_sheet exists. I do not want to uselessly extract the prices.
            balance_sheet = fund_utils.gm.get_annual_financial_statement(equity.fundamentals.balance_sheet, year)
            if balance_sheet is None:
                return False
            if not equity.prices and self.scraping_prices is not None:
                fund_utils.gm.scrape_monthly_prices(self.scraping_prices, equity)  # actual prices scraping.

            # Take the end of the year financial statements then, the price of december that year will make it.
            market_cap = mc.get_market_cap(equity, year=self.year)

            if not market_cap or market_cap == 0 or market_cap < minimum_market_cap or market_cap > maximum_market_cap:
                return False

            # if equity.symbol_1 == 'RRE':  #  and self.year == 2016
            #     a = 1

            if self.is_purchasing_price_higher_than_maximum(equity):
                return False

            if methods.are_variations_in_purchasing_prices_unlikely(equity, self.dates):
                return False

            self.set_factor(equity, year=self.year, market_cap=market_cap)

            self.counter += 1
            if self.counter % 100 == 0:
                print(f"So far done {self.counter} equities")

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def is_purchasing_price_higher_than_maximum(self, equity):
        """
        It checks if the price of the equity when I am going to buy it will be higher that what I can afford. If it is
        just skip the equity.
        @param equity the equity I am considering right now.
        @return True if the price is too high, false otherwise.
        """
        try:
            for price in equity.prices:
                if price.day == self.dates['start_date']:
                    if price.close > self.max_price_share:
                        return True
                    else:
                        continue
            return False
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
            return True

    def set_factor(self, equity, year=None, market_cap=None):
        """
        It sets the factor according to the strategy used.
        @param equity the equity to get the factor from
        @param year the year when to apply the factor
        @param market_cap the market ap of the equity under examination
        @return Nothing
        """
        raise NotImplementedError("Implement the method according to the factor used.")

    def rank_all_equities(self):
        """
        The method takes as input a wwows and ranks them according to the method described in the book what works on
        wall street.
        @param wwows the object of whatworksonwallstreet which contains all the scores
        @return Nothing
        """
        try:
            score_investing_stock = self.get_scores_investing_stocks()
            stocks_to_invest_in = self.list_equities_to_invest_in(score_investing_stock)
            return stocks_to_invest_in, score_investing_stock
        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def get_scores_investing_stocks(self):
        """
        It sets the scores according to the strategy used.
        @return The scores to invest in.
        """
        raise NotImplementedError("Implement the method according to the score used.")

    def list_equities_to_invest_in(self, score_investing_stock):
        """
        The method scan through the list of equities computed in the previous steps and it prints them.

        It also returns a list with only the equities to invest in, no score is passed
        @param score_investing_stock is a dictionary with key the equity id and the value the score obtained.
        @return the list of only the stocks where is convenient to invest in. No score is passed.
        """
        try:
            stocks_to_invest_in = []
            print(f"Results, invest in the following {len(score_investing_stock)} stocks:")
            for equity_id, value in score_investing_stock.items():
                equity = db_mngr.query_equity_by_id(equity_id=equity_id)
                stocks_to_invest_in.append(equity)
                print(f"{equity.exchange}: {equity.symbol_1}:{equity.id}")

            return stocks_to_invest_in

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def save_data(self, country=None, path='./test'):
        """
        Store some data useful so that we do not need to repeat all the test if interrupting.
        """
        try:
            import os
            path = os.path.join(path, country)

            if not os.path.exists(path):
                os.makedirs(path)

            self.save(path, country)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def load_data(self, country=None, path=None):
        """
        Retrieve previouly save data to speed up some testing.
        @return Nothing
        """
        try:
            if path is None:
                path = f'./test/{country}'
            else:
                import os
                path = os.path.join(path, country)

            self.load(path, country)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def lazy_initialization_variables(self, **kwargs):
        """
        If needed a lazy initialization will initialize the variables without breaking the code.
        @param **kwargs any needed variables.
        @return Nothing
        """
        raise NotImplementedError("Implement the method according to the factor used.")

    def compute_market_appreciation(self, equities, country):
        """
        It calls the strategy method to compute the appreciation of the whole market.
        #@param dates the dates from when to when calculate the appreciation
        @param equities the list of equities representing hte market.
        @param country the country we are computing the market appreciation.
        @return the value computed.
        """
        raise NotImplementedError("Implement the method according to the factor used.")

    def save(self, path, country):
        raise NotImplementedError("Implement the method according to the factor used.")

    def load(self, path, country):
        raise NotImplementedError("Implement the method according to the factor used.")


######################################
# Code for getting the equity prices #
######################################
def open_browser_driver():
    """
    The method opens the driver of the browser to be ready to scrape date from the website
    @return the scraping object with the driver of the browser in it.
    """
    try:
        # scrape the prices  only if we do not have them.
        scraping_prices = ScrapingPrices()
        scraping_prices.instantiate_driver(invisible=False)
        scraping_prices.add_cookies(websites.investing_dot_com)
        return scraping_prices
    except Exception as e:
        log.error(f"There is a problem opening the browser driver: {e}\n{getDebugInfo()}")


def scrape_monthly_prices(scraping_prices, equity):
    """
    The method access the investing website of the equity, to extract  monthly recent prices
    @param scraping_prices the scraping object with the driver of the browser in it.
    @param equity the equity to extract the prices
    @return Nothing
    """
    try:
        scraping_prices.retrieve_monthly_company_historical_data(equity, starting_date="01/01/2014")
    except Exception as e:
        log.error(f"There is a problem extracting the equity prices: {e}\n{getDebugInfo()}")


def scrape_prices(decile_dictionary):
    """
    Method used to scrape the prices from the website, it checks if the proces are available, it not it scrape them.
    @param decile_dictionary the dictionary of the equity to get the prices.
    @return Nothing
    """
    try:
        # needed to scrape the missing equity prices.
        scraping_prices = fund_utils.gm.open_browser_driver()

        counter = 0

        for equity_id, equity_score in decile_dictionary.items():

            counter += 1
            print(f"counter = {counter}")
            equity = db_mngr.query_equity_by_id(equity_id=equity_id)

            if equity.prices:
                from datetime import date

                # oldest = min(equity.prices, key=lambda price: price.day)
                newest_date = max(equity.prices, key=lambda price: price.day)
                current_month = date(date.today().year, date.today().month, 1)

                if current_month > newest_date.day:
                    fund_utils.gm.scrape_monthly_prices(scraping_prices, equity)
            else:
                fund_utils.gm.scrape_monthly_prices(scraping_prices, equity)
    except Exception as e:
        log.error(f"There is a problem extracting the prices: {e}\n{getDebugInfo()}")
#######
# END #
#######
