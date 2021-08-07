def return_dataframe_lmp_as_df_wsf_asr(year='2019', year_plus1='2019', month='12', month_plus1='01', day='31', day_plus1='01'):
    temp_folder = "/Users/reecelee/Downloads/AS Clearing Prices"
    date1 = year + month + day
    date2 = year_plus1 + month_plus1 + day_plus1
    startDateTime = date1 + 'T07:00-0000'  # yyyymmddThh24:miZ
    start = '&startdatetime=' + startDateTime
    endDateTime = date2 + 'T07:00-0000'  # yyyymmddThh24:miZ
    end = '&enddatetime=' + endDateTime
    df_list = []
    Prices = ['LMP','WSF','ASP','ASR']
    for price in Prices:
        if price == 'LMP':
            url_lmp = url_base + group_lmp + start + version + '&resultformat=6'
            zip_path = "/Users/reecelee/Downloads/" + date1 + "_" + date1 + "_" + "_DAM_LMP_GRP_N_N_v1_csv.zip"
            download_file(url_lmp, zip_path)
            unzip_and_delete(zip_path)
            path_base = "/Users/reecelee/Downloads/AS Clearing Prices/" + date1 + "_" + date1 + "_PRC_LMP_DAM_"
            LMP = pd.read_csv(path_base + price + "_v1.csv")[['OPR_DT', 'OPR_HR', 'NODE', 'MW']].copy()
            LMP.columns = ['Date', 'Hour', 'Node', 'LMP']
            LMP = LMP.sort_values(by=['Node', 'Date', 'Hour'])
            LMP_node1 = LMP[(LMP["Node"] == node1)]
            df_list.append(LMP_node1)
        elif price == 'WSF':
            url_wsf = url_base_single + query_wsf + start + end + version + '&resultformat=6'
            zip_path = "/Users/reecelee/Downloads/" + date1 + "_" + date1 + "_" + query_name_asr + "_N_N_v1_csv.zip"
            download_file(url_wsf, zip_path)
            unzip_and_delete(zip_path)
            path_base = [i for i in glob.glob('/Users/reecelee/Downloads/AS Clearing Prices/*')]
            WSF = pd.read_csv(path_base[0])[['OPR_DT', 'OPR_HR', 'TRADING_HUB', 'RENEWABLE_TYPE', 'RENEW_POS', 'MW', 'MARKET_RUN_ID']].copy()
            WSF.columns = ['Date', 'Hour', 'Trading Hub', 'Renewable Type', 'RENEW_POS', 'Price', 'Market']
            WSF.sort_values(by=['Trading Hub', 'Renewable Type', 'Date', 'Hour'], inplace=True)
            df_list.append(WSF)
        elif price == 'ASP':
            url_asp = url_base + group_as + start + version + '&resultformat=6'
            zip_path = "/Users/reecelee/Downloads/" + date1 + "_" + date1 + "_" + group_id_as + "_N_N_v1_csv.zip"
            download_file(url_asp, zip_path)
            unzip_and_delete(zip_path)
            path_base = "/Users/reecelee/Downloads/AS Clearing Prices/" + date1 + "_" + date1 + "_PRC_AS_DAM"
            AS = pd.read_csv(path_base + "_v1.csv")[['OPR_DT', 'OPR_HR', 'ANC_TYPE', 'ANC_REGION', 'MW']].copy()
            AS.columns = ['Date', 'Hour', 'Service', 'Region', 'Price']
            AS = AS.sort_values(by=['Service', 'Region', 'Date', 'Hour'])
            AS_pivot = AS.groupby(['Date', 'Hour', 'Region', 'Service'])['Price'].aggregate('first').unstack()
            df_list.append(AS_pivot)
        elif price == 'ASR':
            anc_filter = '&as_type=ALL&as_region=ALL'
            url_asr = url_base_single + query_asr + market + anc_filter + start + end + version + '&resultformat=6'
            zip_path = "/Users/reecelee/Downloads/" + date1 + "_" + date1 + "_" + query_name_asr + "_N_N_v1_csv.zip"
            download_file(url_asr, zip_path)
            unzip_and_delete(zip_path)
            path_base = [i for i in glob.glob(temp_folder + '/*')]
            ASR = pd.read_csv(path_base[0])[['OPR_DT', 'OPR_HR', 'ANC_TYPE', 'ANC_REGION', 'MW']].copy()
            ASR.columns = ['Date', 'Hour', 'Service', 'Region', 'Price']
            ASR.sort_values(by=['Service', 'Region', 'Date', 'Hour'], inplace=True)
            type_filter = ['RU', 'RD', 'SP']
            ASR = ASR[ASR['Service'].isin(type_filter)]
            ASR_pivot = ASR.groupby(['Date', 'Region', 'Hour', 'Service'])['Price'].aggregate(['max', 'min']).unstack()
            ASR_pivot.columns = ASR_pivot.columns.map('|'.join).str.strip('|')
            ASR_pivot.reset_index(inplace=True)
            df_list.append(ASR_pivot)

    combined = pd.concat(df_list,axis=1)
    combined.to_csv("/Users/reecelee/Documents/Internship/Project/AS Requirements/" + date1 + "_" + date1 + "_AS_REQ_DAM_v2.csv",index=False)
    delete_files(temp_folder)
    return 0

return_dataframe_lmp_as_df_wsf_asr(year='2019', year_plus1='2019', month='12', month_plus1='12', day='05', day_plus1='06')


class NewCost:

    def __init__(self,debt_cost=8,equity_cost=12,debt_ratio=50,loan_life=20):
        """

        :param debt_cost: int or float, cost of debt (%), default is 8%
        :param equity_cost: int or float, cost of equity (%), default is 12%
        :param debt_ratio: int or float, portion of total capex which will be debt-financed (%), default is 50%
        :param loan_life: int, loan payback period (years), default is 20 years
        """

        # Given data
        self.debt_cost = debt_cost * 0.01
        self.equity_cost = equity_cost * 0.01
        self.debt_ratio = debt_ratio * 0.01
        self.loan_life = loan_life

        # Most recent interest expense and principal payment
        self.ipmt = 0
        self.ppmt = 0

    #  Creates a dataframe from the given dictionary
    def create_df(self, dict):
        df = pd.DataFrame.from_dict(dict, orient="index",
                                    columns=["Year","Debt O/S","Interest Expense","Principal Payment","Levelised Debt Service"])
        df["Year"] = dict.keys()
        return df

    # Creates a dictionary of projected interest and principal payments when the object is initialized
    def create_dict(self,year,cost):
        dict = {}
        # total debt o/s
        principal = cost * self.debt_ratio
        debt_os = principal
        pmt = -np.pmt(self.debt_cost, self.loan_life, principal)
        for i in range(year, year + self.loan_life + 1):
            # adding a year 0 row
            if i == year: dict[i] = {"Debt O/S":0,"Interest Expense":0,"Principal Payment":0,"Levelised Debt Service":0}
            else:
                self.ipmt = -np.ipmt(self.debt_cost, i-year, self.loan_life, principal)
                self.ppmt = -np.ppmt(self.debt_cost, i-year, self.loan_life, principal)
                dict[i] = {"Debt O/S":debt_os,"Interest Expense":self.ipmt,"Principal Payment":self.ppmt,"Levelised Debt Service":pmt}
                debt_os -= self.ppmt
        return dict