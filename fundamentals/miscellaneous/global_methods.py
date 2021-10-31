from colorama import Fore, Back
from data_storing.assets.common import Timespan, MeasureUnit
import fundamentals.miscellaneous as fund_utils
from utilities.exchange_rates import Exchange
from utilities.common_methods import Methods as methods
from utilities import log
from utilities.common_methods import getDebugInfo
from utilities.globals import websites
from datetime import datetime, date
from data_storing.assets.database_manager import DatabaseManager as db_mngr
from data_storing.assets.tables import Equity


def get_last_financial_statement(financial_statements):
    try:
        last_financial_statement = None
        last_year = 0
        for financial_statement in financial_statements:
            if financial_statement.period_length == Timespan.annual and \
                    financial_statement.period_ending.year > last_year:
                last_financial_statement = financial_statement
                last_year = financial_statement.period_ending.year

        return last_financial_statement
    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


def get_annual_financial_statement(financial_statements, year):
    try:
        financial_statement_of_interest = None
        for financial_statement in financial_statements:
            if financial_statement.period_ending.year == year and \
                    financial_statement.period_length == Timespan.annual:
                financial_statement_of_interest = financial_statement
                break

        return financial_statement_of_interest
    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


def get_measure_unit_multiplier(measure_unit):
    try:
        multiplier = None
        if measure_unit == MeasureUnit.billion:
            multiplier = 1000000000
        elif measure_unit == MeasureUnit.million:
            multiplier = 1000000
        elif measure_unit == MeasureUnit.thousand:
            multiplier = 1000
        return multiplier
    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


def get_exchange_rate(input_var, equity=None):
    """
    The method returns the exchange rate of the equity's country with respect to the USD
    @param input_var it could be equity to get the exchange rate from of it could be the currency itself.
    @param equity passed in case in the input_var is empty, we use  the overview currency
    @return the exchange rate which was found.
    """
    try:
        # if the input_var is the equity get it from the stock exchange country
        if isinstance(input_var, Equity):
            currency = Exchange.country.get(input_var.country)
        # else the input_var is a currency, then get it, but if it is empty, then again get it from the stock exchange.
        elif isinstance(input_var, str):
            currency = input_var
            if not currency and equity is not None:
                currency = methods.validate(equity.overview.currency)
        else:
            raise Exception("Not correct input to the method get_exchange_rate")

        if currency is None:
            return None

        exchange_rate = 1
        if currency != 'USD':
            exchange_rate = Exchange.get_rate(currency)
        return exchange_rate
    except Exception as e:
        str_input_var = str(input_var)
        info = str(equity)
        log.error(f"There is a problem in the code!: input_var = {str_input_var} and {info} {e}\n{getDebugInfo()}")
        return None


def is_equity_undesirable(equity):
    """
    The method return true, if the equity is in the list of undesirable type
    @param equity the equity to investigate.
    @return true if the equity is of the undesirable type
    """
    try:
        # Do not include financial sector
        #
        sector = equity.sector.lower()
        industry = equity.industry.lower()
        equity_type = equity.equity_type.lower()
        if sector in fund_utils.gv.sector_to_avoid or \
                industry in fund_utils.gv.industry_to_avoid or \
                equity_type in fund_utils.gv.equity_type_to_avoid:
            return True
        else:
            return False

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


def get_dates_for_period_in_days(num_days, year, month):
    """
    Given the number of days, the year and the month it returns the dates in between
    @param num_days the number of days for the period
    @param year the year of interest
    @param month the month when to start taking the date.
    @return the range of period, starting date, and ending dates
    """
    try:
        dates = {}
        if not year:
            dates['end_date'] = datetime.now().date()
        else:
            dates['end_date'] = date(year + 1, month - 1, 1)  # self.year, self.month
        dates['start_date'] = methods.backward_days(dates['end_date'], num_days)
        return dates
    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


def get_testing_year_date_range(year, month):
    """
    Given the equity in input it returns the range of dates for the investing year.
    @param equity the equity we are interested in the dates
    @return the range of period, starting date, and ending dates
    """
    try:
        dates = {}
        if not year:
            dates['end_date'] = datetime.now().date()
            dates['start_date'] = methods.backward_days(dates['end_date'], 365)
        else:
            dates['start_date'] = date(year + 1, month, 1)
            dates['end_date'] = methods.forward_days(dates['start_date'], 364 + 0)  # 28

        #dates['start_date_str'] = dates['start_date'].strftime("%m/%d/%Y")
        #dates['end_date_str'] = dates['end_date'].strftime("%m/%d/%Y")
        return dates
    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


def get_next_month_date_given_date(input_date):
    """
    The method takes in input a date and it returns the date of the following month.
    @param input_date the date in input to modify
    @return the input date of the following month
    """
    next_month_date = None

    try:
        next_month_date = input_date.replace(month=input_date.month + 1)
    except ValueError:
        if input_date.month == 12:
            next_month_date = input_date.replace(year=input_date.year + 1, month=1)
        else:
            # next month is too short to have "same date"
            # pick your own heuristic, or re-raise the exception:
            raise Exception("Something wrong with the date to calculate the following month")
    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
    finally:
        return next_month_date


def get_color_and_keyword_gain_loss(delta_capital):
    try:
        if delta_capital > 0:
            color_back = Back.GREEN
            color_fore = Fore.BLACK
            keyword = "gained"
        elif delta_capital < 0:
            color_back = Back.RED
            color_fore = Fore.WHITE
            keyword = "lost"
        else:  # The same
            color_back = ""
            color_fore = ""
            keyword = "stable"

        return color_fore, color_back, keyword
    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


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
        from website_scraping.investing_dot_com.scraping_prices import ScrapingPrices
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
        scraping_prices = open_browser_driver()

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
                    # newest_date = newest.day.strftime("1/%-m/%Y")
                    # today_date = date.now().strftime("1/%-m/%Y")
                    scrape_monthly_prices(scraping_prices, equity)
            else:
                scrape_monthly_prices(scraping_prices, equity)
    except Exception as e:
        log.error(f"There is a problem extracting the prices: {e}\n{getDebugInfo()}")
#######
# END #
#######
