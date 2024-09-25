import pandas as pd
pd.options.mode.chained_assignment = None

class PredictIncome:
    def __init__(self,income_data_predict):
        self.main_df = None
        self.comission_df = None
        self.retention_df = None
        self.dataframes = {**income_data_predict}
        for key, value in self.dataframes.items():
            setattr(self, key, value)
        self.to_lower_str()
    def apply_dfs(self, func):
        for df_name, df in self.dataframes.items():
            processed_df = func(df)
            self.dataframes[df_name] = processed_df
            setattr(self, df_name, processed_df)
    
    def to_lower_str(self): 
        columns_to_lower = ['보험사명', '보험사', '회사명', '보험사+업적월+시책회차 key', 
                            '보험사+업적월+상품군 key','상품군분류', '보험사+업적월+시책회차 key']
        def lower(df):
            if isinstance(df, pd.DataFrame):
                df.columns = df.columns.astype(str)
                for col in df.columns:
                    if col in columns_to_lower and df[col].dtype == 'object':
                        df[col] = df[col].str.lower()
            return df        
        self.apply_dfs(lower)
        
    def lookup_value(self, lookup_df, base_company_cols, look_company_cols, 
                 number_col, value_cols, add_str_to_col):
        def find_value(row):
            company_match = True
            for base_col, look_col in zip(base_company_cols, look_company_cols):
                company_match &= (lookup_df[look_col] == row[base_col])
            number = row[number_col]
            matches = lookup_df[company_match]
            if not matches.empty and number in value_cols:
                for col in value_cols:
                    if number == col:
                        return matches[add_str_to_col + str(col)].iloc[0]
            return 0
        return self.main_df.apply(find_value, axis=1)

    def prediction(self):
        self.main_df['difference'] = self.main_df['수익비용인식회차']- self.main_df['당기해당회차']
        print('difference')
        for i in range(1, 37):
            col = str(i)
            self.main_df['tempo'] = i
            self.main_df['tempo'] = self.main_df.apply(lambda x: 0 if x['tempo']>x['difference'] else x['tempo'], 
                     axis = 1)
            if i == 1:
                self.main_df[col] = self.main_df['당월누적수익인식액']+self.main_df['당월수익인식액']*self.lookup_value(self.comission_df, ['보험사'],['보험사'], 
                                                                     'tempo', [a for a in range(1,25)], '')*self.lookup_value(self.retention_df, ['보험사'],['회사명'],
                                                                                                                         'tempo', [i for i in range(1,25)], '')
                self.main_df[col] = self.main_df.apply(lambda x: 0 if x['tempo'] == 0 else x[col], axis = 1)
            else:
                col_prev = str(i-1)
                self.main_df[col] = self.main_df[col_prev]+self.main_df['당월수익인식액']*self.lookup_value(self.comission_df, ['보험사'],['보험사'], 
                                                                     'tempo', [a for a in range(1,25)], '')*self.lookup_value(self.retention_df, ['보험사'],['회사명'],
                                                                                                                          'tempo', [i for i in range(1,25)], '')
            self.main_df[col] = self.main_df.apply(lambda x: 0 if x['tempo'] == 0 else x[col], axis = 1)
            self.main_df[col] = self.main_df.apply(lambda x: 0 if x['difference']<i else x[col], axis=1)
        
        return self.main_df    

    def process(self):
        self.comission_df = self.comission_df.ffill(axis = 1).infer_objects()
        self.retention_df = self.retention_df.ffill(axis = 1).infer_objects()
        self.main_df = self.main_df[['보험사+업적월+상품군 key', '마감월', '보험사', '업적월', '당기해당회차', '수익비용인식회차',
       '환수율적용회차', '환수율', '유지율', '성과(당월)','성과(누적)', '당월누적수익인식액','당월수익인식액' ]]
        self.main_df = self.prediction()
        self.main_df = self.main_df.drop(['tempo', 'difference'], axis = 1)

    def get_data(self):
        return self.main_df