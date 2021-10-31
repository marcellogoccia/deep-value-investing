from data_storing.assets.common import Timespan
from utilities.common_methods import getDebugInfo
from utilities import log
import numpy as np
from sklearn.linear_model import LinearRegression

# for polinomial regression
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures


def get_linear_regression_estimate(x, y):
    model = LinearRegression().fit(x, y)
    r_sq = model.score(x, y)
    # print('coefficient of determination:', r_sq)
    # print('intercept:', model.intercept_)
    # print('slope:', model.coef_)
    return model

def predict_growth_linear_regression(x_new, model):
    y_pred = model.predict(x_new)
    # print('predicted response:', y_pred, sep='\n')
    return y_pred

def get_polinomial_regression(x, y):
    # # polynomial regression
    # x_     = PolynomialFeatures(degree=20, include_bias=False).fit_transform(x)
    # x_new_ = PolynomialFeatures(degree=20, include_bias=False).fit_transform(x_new)
    # model = LinearRegression().fit(x_, y)
    # r_sq = model.score(x_, y)
    # print('coefficient of determination:', r_sq)
    # print('intercept:', model.intercept_)
    # print('coefficients:', model.coef_)
    # y_pred = model.predict(x_new_)
    # print('predicted non linear response:', y_pred, sep='\n')
    pass


def get_growth_estimate(equity):
    """
    @function get_growth_estimate
    The function return a growth estimate of the company
    """
    try:
        equity.fundamentals.income_statement.sort(key=lambda x: x.period_ending.year)
        income_statements = equity.fundamentals.income_statement
        revenues = []
        years = []
        for income_statment in income_statements:

            if income_statment.period_length == Timespan.annual:
                revenues.append(income_statment.revenue)
                years.append(income_statment.period_ending.year)

        x = []
        y = []
        for index in range(len(revenues) - 1):
            x.append(years[index])
            value = (revenues[index + 1] - revenues[index]) / revenues[index]
            y.append(value)

        # growths of the previous years.
        x = np.array(x).reshape((-1, 1))
        y = np.array(y)

        # linear regression
        model = get_linear_regression_estimate(x, y)
        x_new = np.array([x[-1] + 1, x[-1] + 2, x[-1] + 3]).reshape((-1, 1))
        growths_prediction = predict_growth_linear_regression(x_new, model)
        average_growth = np.average(growths_prediction)
        return average_growth

    except Exception as e:
        log.error(f"There is a problem in the code!: {e}\n{getDebugInfo()}")
