import pandas as pd
from tqdm import tqdm
import datetime as dt
import matplotlib.pyplot as plt
from pandas.tseries.offsets import BMonthBegin
from RiskParityPrimer import RiskParitySP
tqdm.pandas(desc="Rebalancing")


data_folder = '../data/'
start_date = '2009-12-30'
end_date = '2022-1-3'
lag = 2
RESULT_DIR = './result/'
TV = 0.1  # Target volatility


def get_next_n_trading_days(date, n=1):
    increment = 0
    while increment < n:
        date += dt.timedelta(days=1)
        if date.isoweekday():
            increment += 1
    return date


class Trader(RiskParitySP):
    def __init__(self, TV, start_date, end_date, lag):
        super().__init__(TV, start_date, end_date, lag)
        self.trading_gap = 22
        self.start_date = start_date
        self.end_date = end_date

    def trade(self):

        ret = self.ret[self.start_date:self.end_date]
        rebalancing_dates = pd.bdate_range(self.start_date, self.end_date)
        effecetive_dates = rebalancing_dates.to_series().apply(
            lambda x: get_next_n_trading_days(x, self.lag))

        W = rebalancing_dates.to_series().progress_apply(lambda date: self.compute_weight(date, self.trading_gap))
        W = W.set_index(effecetive_dates)
        W = pd.DataFrame(index=ret.index).join(W).ffill(axis=0)

        daily_ret = ret.multiply(W).sum(axis=1)
        from pathlib import Path
        daily_ret.to_excel(RESULT_DIR + f"data/{Path(__file__).stem} daily_return.xlsx")
        cum_ret = (1 + daily_ret).cumprod()
        cum_ret.name = 'replicated'
        return cum_ret


if __name__ == '__main__':
    trader = Trader(TV, start_date, end_date, lag)
    replicated_curve = trader.trade()

    actual_curve = pd.read_excel(data_folder + 'PerformanceGraphExport.xls', index_col=0)
    actual_curve = (actual_curve.pct_change() + 1).cumprod()
    df = pd.concat([replicated_curve, actual_curve], axis=1)
    df.plot().legend(loc='upper left')
