import pandas as pd
import numpy as np
import datetime
pd.options.mode.chained_assignment = None
class PolicyProcessor:
    def __init__(self, income_policy_data):
        self.inc_p_prev_month = None
        self.inc_p_data_case= None
        self.inc_p_main= None
        self.inc_p_retention= None
        self.inc_p_commission= None
        self.dataframes = {
            **income_policy_data
        }
        for key, value in self.dataframes.items():
            setattr(self, key, value)
        self.to_lower()
        self.change_value()
    
    def to_lower(self):
        columns_to_lower = ['보험사명','기시기말숫자코드', '보험사', '회사명', '보험사+업적월+시책회차 key', 
                            '보험사+업적월+상품군 key','상품군분류', '보험사+업적월+시책회차 key']
        def lower_columns(df):
            if isinstance(df, pd.DataFrame):
                for col in df.columns:
                    if col in columns_to_lower and df[col].dtype == 'object':
                        df[col] = df[col].str.lower()
            return df
        self.apply_to_dataframes(lower_columns)
    def apply_to_dataframes(self, func):
        for df_name, df in self.dataframes.items():
            processed_df = func(df)
            self.dataframes[df_name]=processed_df
            setattr(self, df_name, processed_df)
    def change_value(self):
        def kb_life(df):
            df.replace('KB라이프생명', 'KB라이프', inplace = True)
            return df
        self.apply_to_dataframes(kb_life)
        
    def add_to_case_data(self, df):
        #print(df['업적시작월'].value_counts())
        df['key'] = df['보험사'].astype(str)+'/'+df['업적시작월'].astype(str)+'/'+df['시책구분'].astype(str)
        #print(df.head())
    def get_m_count(self, add_df, match_columns_base,match_columns_add, value_column, new_column_name):
        self.inc_p_main['_temp_key'] = list(zip(*[self.inc_p_main[col] for col in match_columns_base]))
        add_df['_temp_key'] = list(zip(*[add_df[col] for col in match_columns_add]))
        value_dict = add_df.groupby('_temp_key')[value_column].first().to_dict()
        self.inc_p_main[new_column_name] = self.inc_p_main['_temp_key'].map(value_dict)
        self.inc_p_main.drop('_temp_key', axis=1, inplace=True)
        add_df.drop('_temp_key', axis=1, inplace=True)  
        return self.inc_p_main
    
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
        return self.inc_p_main.apply(find_value, axis=1)
    
    def sum_by_company_date(self, add_df, match_columns_base,match_columns_add, value_column, new_column_name):
        self.inc_p_main['_temp_key'] = list(zip(*[self.inc_p_main[col] for col in match_columns_base]))
        add_df['_temp_key'] = list(zip(*[add_df[col] for col in match_columns_add]))
        
        value_dict = add_df.groupby('_temp_key')[value_column].sum().to_dict()
        self.inc_p_main[new_column_name] = self.inc_p_main['_temp_key'].map(value_dict)
        self.inc_p_main[new_column_name] = self.inc_p_main[new_column_name].fillna(0).infer_objects(copy=False)
    
        alfa = self.inc_p_main[new_column_name]
        
        self.inc_p_main.drop(['_temp_key', new_column_name], axis=1, inplace=True)
        add_df.drop('_temp_key', axis=1, inplace=True)        
        return alfa
    

    def process_inc_p_main(self):
        self.inc_p_retention.columns = self.inc_p_retention.columns.astype(str)
        self.inc_p_commission.columns = self.inc_p_commission.columns.astype(str) 
        self.inc_p_main[['보험사', '업적월', '시책계산방식']] = self.inc_p_main['보험사+업적월+시책회차 key'].str.split('/', n=3, expand = True)
        self.inc_p_main['마감월'] = pd.to_datetime(self.inc_p_main['마감월'], format = '%Y%m', errors = 'coerce')
        self.inc_p_main['업적월'] = pd.to_datetime(self.inc_p_main['업적월'], format = "%Y%m", errors = 'coerce')
        self.inc_p_main['당기해당회차'] = self.inc_p_main['마감월'].dt.to_period('M').astype(int)-self.inc_p_main['업적월'].dt.to_period('M').astype(int)+1
        self.inc_p_main['당기해당회차'] = self.inc_p_main.apply(lambda x: x['당기해당회차'] if x['시책계산방식'] == '1차년도' else (x['당기해당회차']-12 if x['당기해당회차']-12>0 else 0), axis = 1)

    def process_start(self):
        self.add_to_case_data(self.inc_p_data_case)
        self.process_inc_p_main()
        self.get_m_count(self.inc_p_commission, ['보험사+업적월+시책회차 key'],['기시기말숫자코드'],'환수율적용회차','수익비용인식회차')
        self.inc_p_main['수익비용인식회차'] = self.inc_p_main['수익비용인식회차'].fillna(0)
        self.inc_p_main['환수율'] = self.lookup_value(self.inc_p_commission, ['보험사+업적월+시책회차 key'],['기시기말숫자코드'], '당기해당회차', [i for i in range(25)], '' )    
        self.inc_p_main['유지율'] = self.lookup_value(self.inc_p_retention, ['보험사'],['회사명'], '당기해당회차', [i for i in range(25)], '' )    
        self.inc_p_main['시책수령액(당월)'] = self.sum_by_company_date(add_df=self.inc_p_data_case[self.inc_p_data_case['내용구분']=='법인'], 
                                match_columns_base=['보험사+업적월+시책회차 key'],
                                match_columns_add= ['key'],
                                value_column='금액_1',
                                new_column_name='alfabet')
        self.inc_p_main['시책수령환수액(당월)'] = self.sum_by_company_date(add_df=self.inc_p_data_case[self.inc_p_data_case['내용구분']=='법인환수'],
                                match_columns_base=['보험사+업적월+시책회차 key'],
                                match_columns_add= ['key'],
                                value_column='금액_1',
                                new_column_name='alfabet')
        self.inc_p_main['시책수령액(누적)'] = self.sum_by_company_date(self.inc_p_prev_month,['보험사+업적월+시책회차 key'],
                                                                ['보험사+업적월+시책회차 key'],'시책수령액(누적)','tempor')+self.inc_p_main['시책수령액(당월)']

        self.inc_p_main['시책수령환수액(누적)'] = self.sum_by_company_date(self.inc_p_prev_month,['보험사+업적월+시책회차 key'],
                                                                ['보험사+업적월+시책회차 key'],'시책수령환수액(누적)','tempor')+self.inc_p_main['시책수령환수액(당월)']

        #Second
        self.inc_p_main['시책지급액(당월)'] = self.sum_by_company_date(add_df=self.inc_p_data_case[self.inc_p_data_case['내용구분']=='사용인'], 
                                match_columns_base=['보험사+업적월+시책회차 key'],
                                match_columns_add= ['key'],
                                value_column='금액_2',
                                new_column_name='alfabet')
        self.inc_p_main['시책지급환수액(당월)'] = self.sum_by_company_date(add_df=self.inc_p_data_case[self.inc_p_data_case['내용구분']=='사용인환수'], 
                                match_columns_base=['보험사+업적월+시책회차 key'],
                                match_columns_add= ['key'],
                                value_column='금액_2',
                                new_column_name='alfabet')
        self.inc_p_main['시책지급액(누적)'] = self.sum_by_company_date(self.inc_p_prev_month,['보험사+업적월+시책회차 key'],
                                                                ['보험사+업적월+시책회차 key'],'시책지급액(누적)','tempor')+self.inc_p_main['시책지급액(당월)']

        self.inc_p_main['시책지급환수액(누적)'] = self.sum_by_company_date(self.inc_p_prev_month,['보험사+업적월+시책회차 key'],
                                                                ['보험사+업적월+시책회차 key'],'시책지급환수액(누적)','tempor')+self.inc_p_main['시책지급환수액(당월)']
        #####
        self.inc_p_main['기초선수수익'] = self.sum_by_company_date(self.inc_p_prev_month,['보험사+업적월+시책회차 key'],
                                                                ['보험사+업적월+시책회차 key'],'기말선수수익','tempor')
        
        self.inc_p_main['당월시책수령액'] = self.inc_p_main['시책수령액(당월)']
        self.inc_p_main['당월시책수령환수액'] = self.inc_p_main['시책수령환수액(당월)']
        self.inc_p_main['당월누적수익인식액'] = self.inc_p_main.apply(lambda x: x['시책수령액(누적)']+x['시책수령환수액(누적)'] if x['당기해당회차']>x['수익비용인식회차'] else
                                                              (x['시책수령액(누적)']+x['시책수령환수액(누적)'])*x['당기해당회차']/x['수익비용인식회차'], axis = 1)
        self.inc_p_main['전월누적수익인식액'] = self.sum_by_company_date(self.inc_p_prev_month,['보험사+업적월+시책회차 key'],
                                                                ['보험사+업적월+시책회차 key'],'당월누적수익인식액','tempor')
        self.inc_p_main['당월수익인식액'] = self.inc_p_main['당월누적수익인식액']-self.inc_p_main['전월누적수익인식액']
        self.inc_p_main['선수수익 기타조정액'] = 0
        self.inc_p_main['기말선수수익'] = self.inc_p_main.apply(lambda x: 0 if x['당기해당회차']>x['수익비용인식회차'] else
                                                              (x['시책수령액(누적)']+x['시책수령환수액(누적)']-x['당월누적수익인식액']), axis = 1)
        self.inc_p_main['선수수익 기타조정액'] =self.inc_p_main['기말선수수익']+self.inc_p_main['당월수익인식액']-self.inc_p_main['기초선수수익']-self.inc_p_main['당월시책수령액']-self.inc_p_main['당월시책수령환수액']         

        ### Second
        self.inc_p_main['기초선급비용'] = self.sum_by_company_date(self.inc_p_prev_month,['보험사+업적월+시책회차 key'],
                                                                ['보험사+업적월+시책회차 key'],'기말선급비용','tempor')
        
        self.inc_p_main['당월시책지급액'] = self.inc_p_main['시책지급액(당월)']
        self.inc_p_main['당월시책지급환수액'] = self.inc_p_main['시책지급환수액(당월)']
        self.inc_p_main['당월누적비용인식액'] = self.inc_p_main.apply(lambda x: x['시책지급액(누적)']+x['시책지급환수액(누적)'] if x['당기해당회차']>x['수익비용인식회차'] else
                                                              (x['시책지급액(누적)']+x['시책지급환수액(누적)'])*x['당기해당회차']/x['수익비용인식회차'], axis = 1)
        self.inc_p_main['전월누적비용인식액'] = self.sum_by_company_date(self.inc_p_prev_month,['보험사+업적월+시책회차 key'],
                                                                ['보험사+업적월+시책회차 key'],'당월누적비용인식액','tempor')
        self.inc_p_main['당월비용인식액'] = self.inc_p_main['당월누적비용인식액']-self.inc_p_main['전월누적비용인식액']
        self.inc_p_main['선급비용 기타조정액'] = 0
        self.inc_p_main['기말선급비용'] = self.inc_p_main.apply(lambda x: 0 if x['당기해당회차']>x['수익비용인식회차'] else
                                                              (x['시책지급액(누적)']+x['시책지급환수액(누적)']-x['당월누적비용인식액']), axis = 1)
        self.inc_p_main['선급비용 기타조정액'] =self.inc_p_main['기말선급비용']+self.inc_p_main['당월비용인식액']-self.inc_p_main['기초선급비용']-self.inc_p_main['당월시책지급액']-self.inc_p_main['당월시책지급환수액']    
    
        self.inc_p_main['기초환수부채'] = self.sum_by_company_date(self.inc_p_prev_month,['보험사+업적월+시책회차 key'],
                                                                ['보험사+업적월+시책회차 key'],'기말환수부채','tempor')
        self.inc_p_main['당기환수수익조정'] = 0
        self.inc_p_main['기말환수부채'] = self.inc_p_main.apply(lambda x: 0 if x['기말선수수익'] == 0 else (0 if x['당기해당회차']>x['수익비용인식회차'] else 
                                                                                                (0 if (x['시책수령액(누적)']+x['시책수령환수액(누적)'])*x['환수율']*(1-x['유지율'])<0 else (x['시책수령액(누적)']+x['시책수령환수액(누적)'])*x['환수율']*(1-x['유지율']))), axis = 1)
        self.inc_p_main['당기환수수익조정'] = self.inc_p_main['기말환수부채']-self.inc_p_main['기초환수부채']

        self.inc_p_main['기초환수자산'] = self.sum_by_company_date(self.inc_p_prev_month,['보험사+업적월+시책회차 key'],
                                                                ['보험사+업적월+시책회차 key'],'기말환수자산','tempor')
        self.inc_p_main['당기환수비용조정'] = 0
        self.inc_p_main['기말환수자산'] = self.inc_p_main.apply(lambda x: 0 if x['기말선급비용'] == 0 else (0 if x['당기해당회차']>x['수익비용인식회차'] else 
                                                                                                (0 if (x['시책지급액(누적)']+x['시책지급환수액(누적)'])*x['환수율']*(1-x['유지율'])<0 else (x['시책지급액(누적)']+x['시책지급환수액(누적)'])*x['환수율']*(1-x['유지율']))), axis = 1)
        self.inc_p_main['당기환수비용조정'] = self.inc_p_main['기말환수자산']-self.inc_p_main['기초환수자산']
         
    
    def get_final_df(self):
        return self.inc_p_main