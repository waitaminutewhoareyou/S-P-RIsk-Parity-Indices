import pandas as pd
import numpy as np
from tqdm import tqdm
import datetime as dt
import matplotlib.pyplot as plt
from pandas.tseries.offsets import BMonthBegin
from RiskParityPrimer import RiskParitySP
from pathlib import Path
tqdm.pandas(desc="Rebalancing")

data_folder = '../data/'
start_date = '2019-10-25'
end_date = '2021-1-3'
lag = 2
RESULT_DIR = './result/'
TV = 0.1  # Target volatility


def get_next_n_trading_days(date, n=1):
    increment = 0
    while increment <= n and date.isoweekday() not in [1,2,3,4,5]:
        date += dt.timedelta(days=1)
        if date.isoweekday():
            increment += 1
    return date


class Trader(RiskParitySP):
    def __init__(self, TV, start_date, end_date, lag):
        super().__init__(TV, start_date, end_date, lag)
        self.trading_gap = 5
        self.start_date = start_date
        self.end_date = end_date

    def trade(self, trading_day):
        ret = self.ret[self.start_date:self.end_date]
        all_dates = pd.bdate_range(self.start_date, self.end_date)
        all_dates = all_dates.isocalendar()['day']
        rebalancing_dates = all_dates[all_dates == trading_day].index

        effective_dates = rebalancing_dates.to_series().apply(
            lambda x: get_next_n_trading_days(x, self.lag))

        W = rebalancing_dates.to_series().progress_apply(lambda date: self.compute_weight(date, self.trading_gap))

        W = W.set_index(effective_dates)
        W = pd.DataFrame(index=ret.index).join(W).ffill(axis=0)

        daily_ret = ret.multiply(W).sum(axis=1)
        from pathlib import Path
        daily_ret.to_excel(RESULT_DIR + f"data/{Path(__file__).stem} daily_return.xlsx")
        cum_ret = (1 + daily_ret).cumprod()
        cum_ret.name = 'replicated'
        return cum_ret


if __name__ == '__main__':
    trader = Trader(TV, start_date, end_date, lag)
    trading_day = 5  # Monday
    # print(trader.compute_weight('2021-1-6', 5))
    replicated_curve = trader.trade(trading_day)

    fig, ax_left = plt.subplots()
    ax_right = ax_left.twinx()
    ax_left.plot(replicated_curve, label='ret', color='r')
    ax_right.scatter(trader.leverage.index, trader.leverage.values, label='leverage', color='b')
    fig.legend(loc='upper right', bbox_to_anchor=(1,1), bbox_transform=ax_left.transAxes)
    plt.savefig(RESULT_DIR + f'img/{Path(__file__).stem} leverage.jpg')

    actual_curve = pd.read_excel(data_folder + 'PerformanceGraphExport.xls', index_col=0)
    actual_curve = (actual_curve.pct_change() + 1).cumprod()
    df = pd.concat([replicated_curve, actual_curve], axis=1)
    df.plot().legend(loc='upper left')
