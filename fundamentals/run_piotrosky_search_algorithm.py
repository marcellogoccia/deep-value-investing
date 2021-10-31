import time
from utilities.common_methods import Methods as methods
from data_storing.assets.database_manager import DatabaseManager as db_mngr
from fundamentals.strategies import Piotroski9Points
from utilities import log
from utilities.common_methods import getDebugInfo


def main():
    try:
        #equities = db_mngr.query_all_equities()
        equities = db_mngr.query_all_equities_by(country="United States")  # country="United States" 'Bahrain')

        list_equities_score = []
        start_time_process_equities = time.monotonic()

        print(f"Start!!")
        counter = 0
        for equity in equities:

            # Do not include financial sector
            sector = equity.sector.lower()
            equity_type = equity.equity_type.lower()
            if sector == u'financial' or equity_type == 'preferred':
                continue

            # Do not consider equities according to certain market capitalisation
            market_cap = methods.validate(equity.overview.market_cap)

            if market_cap == 0:
                continue

            # if market_cap < minimum_market_cap:
            #     continue
            if market_cap < minimum_market_cap or market_cap > maximum_market_cap:
                continue

            fs = Piotroski9Points.get_value(equity, 2018)
            equity_id = equity.id

            fscore_dict = {'fscore': fs, 'equity_id': equity_id}

            if fs >= 8 or 0 <= fs <= 1:
                list_equities_score.append(fscore_dict)

            counter += 1
            if counter % 100 == 0:
                print(f"So far done {counter} equities")

            # if counter == 3000:
            #     break

        sorted_equities = sorted(list_equities_score, key=lambda k: k['fscore'])

        # printing_list = sorted_equities[:400]
        printing_list = sorted_equities
        for element in printing_list:

            equity = db_mngr.query_equity_by_id(element['equity_id'])
            fscore = element['fscore']

            log.info(f"fscore = {fscore} "
                     f"-> {equity.exchange}:{equity.symbol_1}:{equity.id}")

        elapsed_time_process_equities = time.monotonic() - start_time_process_equities
        log.info(f"It took {elapsed_time_process_equities} seconds to process all of the {len(equities)} equities available")

    except Exception as e:
        log.error(f"There is a problem in the code! "
                  f"Processed {equity.exchange}:{equity.symbol_1}:{equity.id}: {e}\n{getDebugInfo()}")

# run the program
if __name__ == "__main__":
    main()

