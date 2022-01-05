import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
import datetime as dt

from pandas.tseries.offsets import BMonthBegin
from RiskParityPrimer import RiskParitySP
tqdm.pandas(desc="Rebalancing")


data_folder = '../data/'
start_date = '2011-12-30'
end_date = '2022-1-3'
lag = 2
RESULT_DIR = './result/'
TV = 0.05  # Target volatility


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
        rebalancing_dates = pd.date_range(self.start_date, self.end_date, freq='BM')

        effective_dates = rebalancing_dates.to_series().apply(lambda x: x + BMonthBegin()).apply(
            lambda x: get_next_n_trading_days(x, 2))

        W = rebalancing_dates.to_series().progress_apply(lambda date: self.compute_weight(date, self.trading_gap))
        W = W.set_index(effective_dates)
        W = pd.DataFrame(index=ret.index).join(W).ffill(axis=0)

        daily_ret = ret.multiply(W).sum(axis=1)

        from pathlib import Path
        daily_ret.to_excel(RESULT_DIR + f"data/{Path(__file__).stem} daily_return.xlsx")

        return daily_ret

    def equal_weight(self):
        ret = self.ret[self.start_date:self.end_date].mean(axis=1)
        return ret

if __name__ == '__main__':
    trader = Trader(TV, start_date, end_date, lag)
    replicated_ret = trader.trade().rename("Replicated")
    replicated_ret_cumulative = (1 + replicated_ret).cumprod()

    # actual_ret = pd.read_excel(data_folder + 'PerformanceGraphExport.xls', index_col=0)
    # actual_ret = actual_ret.pct_change()
    # actual_ret_cumulative = (1 + actual_ret).cumprod()
    #
    # equal_weight_ret = trader.equal_weight().rename("Equal Weighting")
    # equal_weight_ret_cumulative = ( 1 + equal_weight_ret).cumprod()
    #
    # print('Correlation table')
    # print(pd.concat([replicated_ret, actual_ret, equal_weight_ret], axis=1).corr().round(2).to_markdown())
    #
    # df = pd.concat([replicated_ret_cumulative, actual_ret_cumulative, equal_weight_ret_cumulative], axis=1)
    # fig, ax = plt.subplots(dpi=150)
    # ax = df.plot(ax=ax).legend(loc='upper left')
    # plt.savefig(RESULT_DIR + 'img/comparison.jpg')