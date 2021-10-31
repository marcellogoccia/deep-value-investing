import fundamentals.miscellaneous as fund_utils
from utilities.common_methods import getDebugInfo
from utilities.common_methods import Methods as methods
from utilities import log


def get_free_cash_flow(equity):
    """
    @function get_free_cash_flow
    The function return the free cash flow of a company
    """
    try:
        market_cap = methods.validate(equity.overview.market_cap)
        price_to_free_cash_flow = methods.validate(equity.fundamentals.ratios[0].price_to_free_cash_flow_ttm)

        free_cash_flow = market_cap / price_to_free_cash_flow

        return free_cash_flow

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


def get_free_cash_flow_v2(equity):
    """
    @function get_free_cash_flow_v2
    The function return the free cash flow of a company. A different way of calculating it
    with respect to the previous method.
    """
    try:
        last_income_statement = fund_utils.gm.get_last_financial_statement(equity.fundamentals.income_statement)
        last_cash_flow_statement = fund_utils.gm.get_last_financial_statement(equity.fundamentals.cash_flow)

        multiplier_is = fund_utils.gm.get_measure_unit_multiplier(last_income_statement.measure_unit)
        multiplier_cf = fund_utils.gm.get_measure_unit_multiplier(last_cash_flow_statement.measure_unit)

        new_income = methods.validate(last_income_statement.net_income) * multiplier_is
        depreciation_depletion = methods.validate(last_cash_flow_statement.depreciation_depletion) * multiplier_cf
        changes_in_working_capital = methods.validate(last_cash_flow_statement.changes_in_working_capital) * multiplier_cf
        capital_expenditures = methods.validate(last_cash_flow_statement.capital_expenditures) * multiplier_cf

        operating_cash_flow = new_income + depreciation_depletion + changes_in_working_capital

        free_cash_flow = operating_cash_flow - capital_expenditures

        return free_cash_flow

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")


def get_free_cash_flow_v3(equity):
    """
    @fn get_free_cash_flow_v3
    The function return the free cash flow of a company.
    This method calculates the free cash flow according to the book "The five rules for successful stock investing" by
    Pat Dorsey. This method takes the operating cash flow minus the capital expenditure to get the free cash flow.
    free_cash_flow = cash_from_operating_activities - capital_expenditures
    @param equity to equity from database with all the fundamental values in it.
    """
    try:
        last_cash_flow_statement = fund_utils.gm.get_last_financial_statement(equity.fundamentals.cash_flow)

        multiplier_cf = fund_utils.gm.get_measure_unit_multiplier(last_cash_flow_statement.measure_unit)

        cash_from_operating_activities = methods.validate(last_cash_flow_statement.cash_from_operating_activities)
        capital_expenditures = methods.validate(last_cash_flow_statement.capital_expenditures)

        free_cash_flow = (cash_from_operating_activities - capital_expenditures) * multiplier_cf

        return free_cash_flow

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
