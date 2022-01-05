import numpy as np
import pandas as pd
from tqdm import tqdm
import datetime as dt
import matplotlib.pyplot as plt
from pandas.tseries.offsets import BMonthBegin

tqdm.pandas(desc="Rebalancing")

SP_pool = [32, 28, 42, 24, 51, 80,
           39, 31, 19, 22,
           36, 21, 40,
           20, 27, 35,
           12, 14, 15,
           11, 4, 5, 50,
           76, 57, 64]

data_folder = '../data/'
data_dir = '../data/consolidated_table_wo_features_SP'
asset_spec_dir = '../data/asset_spec.csv'
start_date = '2018-12-30'
end_date = '2022-1-3'
lag = 1
RESULT_DIR = './result/'
minN = 1260
maxN = 3780
TV = 0.05  # Target volatility


def get_next_n_trading_days(date, n=1):
    increment = 0
    while increment < n:
        date += dt.timedelta(days=1)
        if date.isoweekday():
            increment += 1
    return date


class RiskParitySP:
    def __init__(self):
        # load data
        self.df = pd.read_pickle(data_dir)

        self.asset_specs = pd.read_csv(asset_spec_dir, index_col='Asset number').loc[SP_pool]
        self.indicator = self.asset_specs[['Comm indicator', 'Equity indicator', 'Bond indicator']]

        self.commodity_class = (self.asset_specs['Comm indicator'] == 1).index
        self.equity_class = (self.asset_specs['Equity indicator'] == 1).index
        self.bond_class = (self.asset_specs['Bond indicator'] == 1).index

        self.start_date = start_date
        self.end_date = end_date
        self.lag = lag

        self.ret = self.df.xs("ret", level='Features')
        self.N = minN
        self.ac_ret = pd.DataFrame()  # asset class return will be calculated and appended later
        self.TV = TV

    def compute_weight(self, date):

        def compute_volatility_by_column(ret_ser: pd.Series) -> float:
            ret_ser = ret_ser.dropna()
            ret_ser = ret_ser[ret_ser != 0]
            if len(ret_ser) < self.N:
                return np.nan
            else:
                ret_ser = ret_ser.iloc[-self.N:]
                return ret_ser.std() * np.sqrt(252)

        w = []
        raw_w = []
        # Calculate the constituent weights in each asset class such that each constituent
        # contributes equally to the asset class volatility
        # ret = self.ret_full_history.loc[:date, :]
        ret = self.ret.loc[:date, :]
        RV = ret.apply(compute_volatility_by_column)
        ac_inverse_RV = (1 / RV).replace(np.nan, 0).dot(self.indicator)

        for asset_ix, rv in RV.iteritems():

            asset_class = self.indicator.columns[self.indicator.loc[asset_ix] == 1]

            if asset_class.empty:
                w.append(0)
                continue

            normalization_const = ac_inverse_RV[asset_class].values
            weight = 1 / rv / normalization_const
            w.append(weight.item())

        w = pd.Series(data=w, index=RV.index).replace(np.nan, 0)
        assert ((w.dot(self.indicator) - 1).abs() < 1e-3).all(), w.dot(self.indicator)

        # Calculate asset class weights such that each asset class contributes an equal amount of
        # volatility
        ac_ret = w.multiply(ret).replace(np.nan, 0).dot(self.indicator)
        acRV = ac_ret.apply(compute_volatility_by_column)
        ac_w = (1 / acRV) / (1 / acRV).sum()

        for asset_ix, weight in w.iteritems():

            asset_class = self.indicator.columns[self.indicator.loc[asset_ix] == 1]

            if asset_class.empty:
                raw_w.append(0)
                continue

            normalization_const = ac_w[asset_class].values
            weight *= normalization_const
            raw_w.append(weight.item())
        raw_w = pd.Series(data=raw_w, index=w.index).replace(np.nan, 0)

        # Calculate the multiplier to meet the target volatility
        p_ret = ac_ret.multiply(ac_w)
        p_rv = p_ret.apply(compute_volatility_by_column)
        pM = (self.TV / p_rv).values[0]

        # Calculate weight of each futures contract
        raw_w *= pM

        self.N = min(maxN, self.N + 30)

        return raw_w

    def trade(self):
        start_trading_date = dt.datetime.strptime(self.start_date, "%Y-%m-%d")
        end_trading_date = dt.datetime.strptime(self.end_date, "%Y-%m-%d")

        ret = self.ret[start_trading_date:end_trading_date]
        rebalancing_dates = pd.date_range(self.start_date, self.end_date, freq='BM')
        effecetive_dates = rebalancing_dates.to_series().apply(lambda x: x + BMonthBegin()).apply(
            lambda x: get_next_n_trading_days(x, 2))

        W = rebalancing_dates.to_series().progress_apply(self.compute_weight)
        W = W.set_index(effecetive_dates)
        W = pd.DataFrame(index=ret.index).join(W).ffill(axis=0)

        daily_ret = ret.multiply(W).sum(axis=1)
        daily_ret.to_excel(RESULT_DIR + "data/daily_return.xlsx")

        cum_ret = (1 + daily_ret).cumprod()
        cum_ret.name = 'replicated'
        return cum_ret


if __name__ == '__main__':
    rp = RiskParitySP()
    replicated_curve = rp.trade()

    actual_curve = pd.read_excel(data_folder + 'PerformanceGraphExport.xls', index_col=0)
    actual_curve = (actual_curve.pct_change() + 1).cumprod()
    df = pd.concat([replicated_curve, actual_curve], axis=1)
    df.plot().legend(loc='upper left')
