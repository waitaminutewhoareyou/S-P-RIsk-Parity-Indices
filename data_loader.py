import os
import numpy as np
import pandas as pd

pd.set_option('display.max_columns', 5)
pd.set_option('display.max_rows', 60)

SP_pool = [32, 28, 42, 24, 51, 80,
           39, 31, 19, 22,
           36, 21, 40,
           20, 27, 35,
           12, 14, 15,
           11, 4, 5,  50,
           76, 57, 64]

class Dataloader:
    def __init__(self):
        self.data_dir = '../data/Asset/'

    def create_xarray(self):

        time_index, features, columns = [], [], []
        data = []

        for csv_file in os.listdir(self.data_dir):
            if not csv_file.endswith("csv"):
                continue
            # get the number between two parenthesis
            asset_ix = int(csv_file[csv_file.find("(") + 1:csv_file.find(")")])

            # For now, then consider extended futures pool
            if asset_ix > 137:
                continue

            if asset_ix not in SP_pool:
                continue
            columns.append(asset_ix)

            cur_df = pd.read_csv(self.data_dir + csv_file,
                                 parse_dates={'Date': ['Year', 'Month', 'Day']},
                                 infer_datetime_format=True,
                                 keep_date_col=True,
                                 na_values=[-999, '-999'])

            cur_df.set_index('Date', inplace=True)

            # add dollar adjusted return
            def adjust_fx(fx, fxbase):
                if fx == 0:
                    return np.nan
                elif fxbase == 1:
                    return 1 / fx
                elif fxbase == 0:
                    return fx
                else:
                    return np.nan

            cur_df['adjusted fx'] = cur_df[['Fx', 'FxBase']].apply(lambda x: adjust_fx(*x), axis=1)
            cur_df['adjusted fx ret'] = cur_df['adjusted fx'].pct_change(fill_method='ffill')
            cur_df['ret'] = cur_df['%change'] * (1 + cur_df['adjusted fx ret']) /100

            if not len(time_index):
                "Name	Cur	Year	Month	Day	%change	Vol	Px	Fx	FxBase"
                time_index = cur_df.index
                features = cur_df.columns

                iterables = [time_index, features]
                index = pd.MultiIndex.from_product(iterables, names=["Date", "Features"])

            data.append(cur_df.stack(dropna=False).values)

        data = list(map(list, zip(*data)))  # transpose

        matrix = pd.DataFrame(data, index=index, columns=columns)
        return matrix


if __name__ == "__main__":
    loader = Dataloader()
    xarray = loader.create_xarray()
    print(xarray.tail(50))
    xarray.to_pickle("../data/consolidated_table_wo_features_SP")
