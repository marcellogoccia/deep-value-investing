from fundamentals.strategies.basic_strategy.strategy import Strategy

import fundamentals.measures as measure
from utilities.common_methods import getDebugInfo
from utilities import log


class Piotroski9Points(Strategy):
    """
    @class Piotroski9Points
    First the analysis should be narrowed among the stocks with the lowest P/B ratio.
    Maybe 20% lowest B/P ratio according to the industrial average P/B ratio.
    The he applies a series of additional tests of financial strength to these low price/book stocks.
    The analysis is based on accounting fundamentals and consists of awarding one point for each of the following tests:
    - 1) positive earnings [F_ROA]
    - 2) positive cash flow [F_CFO]
    - 3) increasing ROA [F_ΔROA]
    - 4) increasing cash flow from operations [F_ACCRUAL]

    - 5) decreasing long term debt as a proportion of total assets [F_ΔLEVER]
    - 6) increasing current ratio (indicating an increasing ability to pay off short term debt) [F_ΔLIQUID]
    - 7) decreasing or stable numbers of outstanding shares [EQ_OFFER]
    - 8) increasing assets turnover (indicating an increasing sales as a proportion of total assets) [F_ΔTURN]
    - 9) increasing gross margin [Δ_MARGIN]
    All 9 factors added together being summed up leads.
    F_SCORE =[F_ROA]+ [F_CFO]+ [F_ΔROA]+ [F_ACCRUAL]+ [F_ΔLEVER]+ [F_ΔLIQUID]+ [EQ_OFFER]+ [F_ΔTURN]+ [Δ_MARGIN]
    Each company is given either a score 0 or 1. The sum of the variables is between 0 and 9.
    The companies are then ranked from best to worst.
    """
    def __init__(self):
        try:
            self.piotrosky_score = {}
            Strategy.__init__(self)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def set_value(self, equity, year=None, market_cap=None):
        try:
            if year is not None:  # if set value brings a
                self.year = year

            curr_year = self.year
            prev_year = self.year - 1

            # cast to int the boolean variable, a point for the Piotroski points
            factors = []

            # (1) Positive Net Income (1 point)
            net_income_curr_year = measure.get_net_income(equity, curr_year)
            net_income_prev_year = measure.get_net_income(equity, prev_year)
            f_roa = 0
            if net_income_curr_year and net_income_prev_year:
                f_roa = int(net_income_curr_year > 0) and int(net_income_curr_year > net_income_prev_year)
            factors.append(f_roa)

            # (2) Positive operating cash flow in the current year
            ocf_curr_year = measure.get_operating_cash_flow(equity, curr_year)
            ocf_prev_year = measure.get_operating_cash_flow(equity, prev_year)
            f_cfo = 0
            if ocf_curr_year and ocf_prev_year:
                f_cfo = int(ocf_curr_year > 0) and int(ocf_curr_year > ocf_prev_year)
            factors.append(f_cfo)

            # (3) Return on Assets (1 point if it is positive in the current year, 0 otherwise)
            roa_curr_year = measure.get_return_on_assets(equity, curr_year)
            roa_prev_year = measure.get_return_on_assets(equity, prev_year)
            f_d_roa = 0
            if roa_curr_year and roa_prev_year:
                f_d_roa = int(roa_curr_year > 0) and int(roa_curr_year > roa_prev_year)
            factors.append(f_d_roa)

            # (4) Cash flow from operations being greater than net Income (quality of earnings) (1 point)
            cash_flow_from_operations = measure.get_operating_cash_flow(equity, curr_year)
            f_accrual = 0
            if cash_flow_from_operations and net_income_curr_year:
                f_accrual = int(cash_flow_from_operations > net_income_curr_year)
            factors.append(f_accrual)

            # (5) Lower ratio of long term debt in the current period, compared to the previous year (1 point)
            leverage_curr_year = measure.get_debt_to_asset_leverage_ratio(equity, curr_year)
            leverage_prev_year = measure.get_debt_to_asset_leverage_ratio(equity, prev_year)
            f_d_lever = 0
            if leverage_curr_year and leverage_prev_year:
                f_d_lever = int(leverage_curr_year < leverage_prev_year)
            factors.append(f_d_lever)

            # (6) Higher current ratio this year compared to the previous year (more liquidity) (1 point)
            current_ratio_curr_year = measure.get_current_ratio(equity, curr_year)
            current_ratio_prev_year = measure.get_current_ratio(equity, prev_year)
            f_d_liquid = 0
            if current_ratio_curr_year and current_ratio_prev_year:
                f_d_liquid = int(current_ratio_curr_year > current_ratio_prev_year)
            factors.append(f_d_liquid)

            # (7) No new shares were issued in the last year (lack of dilution) (1 point)
            outstanding_shares_curr_year = measure.get_outstanding_common_shares(equity, curr_year)
            outstanding_shares_prev_year = measure.get_outstanding_common_shares(equity, prev_year)
            eq_offer = 0
            if outstanding_shares_curr_year and outstanding_shares_prev_year:
                eq_offer = int(outstanding_shares_curr_year <= outstanding_shares_prev_year)
            factors.append(eq_offer)

            # (8) A higher asset turnover ratio compared to the previous year (1 point)
            asset_turnover_ratio_curr_year = measure.get_asset_turnover_ratio(equity, curr_year)
            asset_turnover_ratio_prev_year = measure.get_asset_turnover_ratio(equity, prev_year)
            f_d_turn = 0
            if asset_turnover_ratio_curr_year and asset_turnover_ratio_prev_year:
                f_d_turn = int(asset_turnover_ratio_curr_year > asset_turnover_ratio_prev_year)
            factors.append(f_d_turn)

            # (9) A higher gross margin compared to the previous year (1 point)
            gross_margin_curr_year = measure.get_gross_margin(equity, curr_year)
            gross_margin_prev_year = measure.get_gross_margin(equity, prev_year)
            d_margin = 0
            if gross_margin_curr_year and gross_margin_prev_year:
                d_margin = int(gross_margin_curr_year > gross_margin_prev_year)
            factors.append(d_margin)

            self.piotrosky_score[equity.id] = sum(factors)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
            return -1

    def sort_equities(self):
        """
        It sorts the equities to find the ones that are good to invest in.
        @return Nothing
        """
        try:
            self.piotrosky_score = Piotroski9Points.order_dictionary_by_value(self.piotrosky_score, reverse=True)

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")

    def reset_factors(self):
        """
        It resets the factors used to store the companies economic data
        @return Nothing
        """
        try:
            self.piotrosky_score = {}

        except Exception as e:
            log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
