import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest

class DataPreprocesser:

    # 시나리오 4 기준: Cost/view*sec 단가 (0.1원), 전환율 (15%)
    def __init__(self,filepath):
        self.file = pd.read_csv(filepath)

        # Dividing into currency-related columns and just numerical columns
        self.df_numerical = self.file.loc[:, (self.file.dtypes == 'int64').values]
        df_temp = self.file.loc[:, ~(self.file.dtypes == 'int64').values]
        self.df_currency = df_temp.loc[:, [(df_temp[col].str.contains('₩')).any() for col in df_temp.columns]]
        self.df_categorical = df_temp.loc[:, [~(df_temp[col].str.contains('₩')).any() for col in df_temp.columns]]

    # Standardize dataset
    def standardize(self):
        """
        Input:
        Z: 1 dimensional or 2 dimensional array
        Outuput
        copy of Z with columns having mean 0 and variance 1
        """

        z_copy = self.file.copy()
        z_copy = (z_copy - z_copy.mean(axis=0)) / z_copy.std(axis=0)

        std_scaler = StandardScaler()
        min_max_scaler = MinMaxScaler()

        """ 
        1. Standard Scaler method
        fitted = std_scaler.fit(df_avgspec_advcost)
        output = std_scaler.transform(df_avgspec_advcost)

        2. Min Max Scaler method
        fitted = min_max_scaler.fit(df_avgspec_advcost)
        output = min_max_scaler.transform(df_avgspec_advcost)

        3. Splitting dataset into train, test data
        data = df_avgspec_advcost.values
        a) split into input and output elements
        X, y = data[:, :-1], data[:, -1]
        b) split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=1)
        c) summarize the shape of the train and test sets
        print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
        """
        return z_copy

    # Return whole dataframe
    def return_dataframe(self):
        df = self.file

        # Extracting currency related object columns
        df_temp = df.loc[:, ~(df.dtypes == 'int64').values]
        col_temp = df_temp.loc[:, [(df_temp[col].str.contains('₩')).any() for col in df_temp.columns]].columns

        # Modifying currency related columns to numeric elements
        df[col_temp] = df[col_temp].replace('[\₩,]','', regex=True).apply(pd.to_numeric)
        return df

    # Return only numerical dataframe (including 데나, but not currency related columns)
    def return_dataframe_numerical(self):
        return self.df_numerical

    # Return only currency related dataframe
    def return_dataframe_currency(self):
        df = self.df_currency

        # Modifying columns to numeric elements
        df = df.replace('[\₩,]','', regex=True).apply(pd.to_numeric)
        return df

    # Return dataframe with outliers dropped using sklearn Isolation Forest method
    def drop_outlier_IsoForest(self):
        # Extracting columns
        df_avgspec_advcost = self.file[["Spectator_avg", "Cost_adv"]]

        # Outlier Detection
        iso = IsolationForest(contamination=0.1)
        yhat = iso.fit_predict(df_avgspec_advcost)
        # select all rows that are not outliers
        mask = yhat != -1
        return df_avgspec_advcost[mask]




