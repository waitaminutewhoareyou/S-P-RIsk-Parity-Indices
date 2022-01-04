import numpy as np
import pandas as pd
from tqdm import tqdm


data_dir = '../data/consolidated_table_wo_features_SP'
asset_spec_dir = '../data/asset_spec.csv'
start_date = '2013-1-1'
end_date = '2025-1-1'
lag = 1
OUTPUT_DIR = './BackTest/Daily Return.xlsx'
minN = 1260
maxN = 3780
TV = 0.15  # Target volatility


class RiskParitySP:
    def __init__(self):
        # load data
        self.df = pd.read_pickle(data_dir)

        self.asset_specs = pd.read_csv(asset_spec_dir, index_col='Asset number')
        self.indicator = self.asset_specs[['Comm indicator', 'Equity indicator', 'Bond indicator']]

        self.commodity_class = (self.asset_specs['Comm indicator'] == 1).index
        self.equity_class = (self.asset_specs['Equity indicator'] == 1).index
        self.bond_class = (self.asset_specs['Bond indicator'] == 1).index

        self.start_date = start_date
        self.end_date = end_date
        self.lag = lag

        self.ret_full_history = self.df.xs("ret", level='Features')
        mask = (self.ret_full_history.index > start_date) & (self.ret_full_history.index < end_date)
        self.ret = self.ret_full_history[mask]

        self.N = minN
        self.ac_ret = pd.DataFrame()  # asset class return will be calculated and appended later
        self.TV = TV

    def compute_weight(self):

        def compute_volatility_by_column(ret_ser: pd.Series) -> float:
            ret_ser = ret_ser.dropna()
            ret_ser = ret_ser[ret_ser != 0]
            if len(ret_ser) < self.N:
                return np.nan
            else:
                ret_ser = ret_ser.iloc[-self.N:]
                return ret_ser.std() * np.sqrt(252)

        W =pd.DataFrame([])
        for date, row in tqdm(self.ret.iterrows(), total=self.ret.shape[0]):

            w = []
            raw_w = []
            # Calculate the constituent weights in each asset class such that each constituent
            # contributes equally to the asset class volatility
            ret = self.ret_full_history.loc[:date, :]
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
            assert ( (w.dot(self.indicator) - 1).abs() < 1e-3).all(), w.dot(self.indicator)

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

            self.N = min(maxN, self.N + 1)
            W = W.append(raw_w.to_frame(date).transpose())

        print(W)

if __name__ == '__main__':
    rp = RiskParitySP()
    print(rp.compute_weight())
