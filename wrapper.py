from Cleaner import DataPreprocesser
from CostAnalysis import CostAnalysis

path = '/Users/reecelee/Documents/Coloxeum/scenario4_raw.csv'

#dp = DataPreprocesser(path)
cx = CostAnalysis(path,0.1,0.1,0.2,0.2)

#cx.cost_as_output()
cx.scatterplot_spectatorX()


#print(dp.return_dataframe().dtypes)
#print()
#print(dp.return_dataframe_numerical())
#print()
#print(dp.return_dataframe_currency())







