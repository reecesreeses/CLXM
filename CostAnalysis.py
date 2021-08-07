import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import seaborn as sns
from Cleaner import DataPreprocesser

class CostAnalysis:

    def __init__(self,filepath,cpvs_before=0.1,cpvs_after=0.1,conversion_rate=0.15,commission_rate=0.15):
        self.dp = DataPreprocesser(filepath)
        self.path = filepath
        self.file = pd.read_csv(self.path)
        self.data = self.dp.return_dataframe()
        self.data_out = self.dp.drop_outlier_IsoForest()
        self.unit_price_before = cpvs_before
        self.unit_price_after = cpvs_after
        self.conv_rate = conversion_rate
        self.comm_rate = commission_rate
        self.y_axis = self.data.Cost_adv # Default

    def cost_as_output(self):
        self.y_axis = self.data.Cost_adv

    def revenue_as_output(self):
        self.y_axis = self.data.Revenue_total

    # Lineplot - average spectator (x-axis), advertisement cost (y-axis)
    def lineplot_spectatorX(self):
        sns.lineplot(x='Spectator_avg',y=self.y_axis,data=self.data_out)
        plt.show()
        return 0

    # Scatterplot - spectator (x-axis), cost (y-axis)
    def scatterplot_spectatorX(self):
        sns.scatterplot(x='Spectator_avg', y=self.y_axis, data=self.data_out)
        plt.show()
        return 0

    # Return dataframe based on new inputs
    def return_cleansed_new(self):
        # Load preprocessed data
        df = self.data

        if (self.unit_price_before == 0.1) & (self.unit_price_after == 0.1) & (self.conv_rate == 0.15) \
                & (self.comm_rate == 0.15):
            return df
        # Re-calculate for new unit price and/or conversion & commission rates
        else:
            df.Funding_before = df.Cycle_before * 10 * df.Spectator_avg * self.unit_price_before
            df_Funding_after = df.Gametime_applied * (60 / 46) * 10 * df.Spectator_avg * self.unit_price_after
            df.Cost_adv = df.Funding_before + df_Funding_after

            df.Funding_converted = df.Cost_adv * self.conv_rate

            # New winner & loser prize money
            df.loc[df.Funding_converted < 100, 'Prize_winner'] = 0
            df.loc[df.Funding_converted < 100, 'Prize_loser'] = 0

            # if file.loc[(file.Funding_converted < 100)]:
            # file["Prize_winner"],file["Prize_loser"] = 0,0

            df.loc[df.Funding_converted < 143, 'Prize_winner'] = 1
            df.loc[df.Funding_converted < 143, 'Prize_loser'] = 0
            # elif file["Funding_converted"] < 143:
            # file["Prize_winner"],file["Prize_loser"] = 1,0

            df.loc[df.Funding_converted < 334, 'Prize_winner'] = df.Funding_converted * 0.7 / 100
            df.loc[df.Funding_converted < 334, 'Prize_loser'] = 1
            # elif file["Funding_converted"] < 334:
            # file["Prize_winner"], file["Prize_loser"] = int(file["Funding_converted"]*0.7/100),1

            df.loc[df.Funding_converted >= 334, 'Prize_winner'] = df.Funding_converted * 0.7 / 100
            df.loc[df.Funding_converted >= 334, 'Prize_loser'] = df.Funding_converted * 0.3 / 100
            # else:
            # file["Prize_winner"],file["Prize_loser"] = int(file["Funding_converted"]*0.7/100),int(file[
            # "Funding_converted"]*0.3/100)

            df.Prize_winner = df.Prize_winner.astype(int)
            df.Prize_loser = df.Prize_loser.astype(int)

            df.Funding_leftover = df.Funding_converted - ((df.Prize_winner
                                                                 + df.Prize_loser) * 100)  # 잉여금 Revenue
            df.Revenue_comm = ((df.Prize_winner + df.Prize_loser) * 100) * self.comm_rate  # 수수료 Revenue
            df.Revenue_total = (df.Cost_adv * (1 - self.conv_rate)) + df.Funding_leftover + df.Revenue_comm  # 총 수
            return df

    # To compare new Sponsor Marketing Fee with scenario 4 sponsor marketing fee
    def fee_comparison(self):
        df_old = self.data[['Cost_adv','Revenue_total']]; df_new = CostAnalysis.return_cleansed_new(self)
        df_new = df_new[['Cost_adv','Revenue_total']]
        df_joined = pd.concat([df_old,df_new],axis=1)
        print(df_joined)
        return df_joined

    def export_excel(self):
        # Export new dataframe to excel sheet
        df = CostAnalysis.return_cleansed_new(self)
        df.to_excel('/Users/reecelee/Documents/Coloxeum/scenario4_edit.xlsx')

    def show(self):
        print(self.data)

    def show_out(self):
        print(self.data_out)

