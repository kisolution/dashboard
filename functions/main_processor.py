import datetime
import pandas as pd
pd.options.mode.chained_assignment = None

class IncomeProcessor:
    
    def __init__(self, static_data, income_data):
        self.main_data = None
        
        # Initialize a dictionary to hold all dataframes
        self.dataframes = {
            **static_data,
            **income_data
        }
        
        # Set all dataframes as attributes
        for key, value in self.dataframes.items():
            setattr(self, key, value)
        
        # Apply lower case to relevant columns
        self.to_lower()

    def to_lower(self):
        columns_to_lower = ['보험사명', '보험사', '회사명', '보험사+업적월+시책회차 key', 
                            '보험사+업적월+상품군 key', '보험사+업적월+시책회차 key']
        
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
            self.dataframes[df_name] = processed_df
            setattr(self, df_name, processed_df)

    def add_five_columns(self, df_names):
        def add_columns(df):
            if not isinstance(df, pd.DataFrame):
                return df
            if '계약일' not in df.columns:
                return df
            
            df = df.dropna(thresh=10)
            df['계약일'] = pd.to_datetime(df['계약일'], errors='coerce').dt.date
            df['계약일'] = df['계약일'].fillna(datetime.date(2000, 1, 1))
            df['이관계약여부'] = df['계약일'].apply(lambda x: "이관계약" if x < datetime.date(2023, 7, 1) else "회사보유계약")
            df['보험사1'] = df['보험사'] if '보험사' in df.columns else 'Unknown'
            df['업적월'] = pd.to_datetime(df['계약일']).dt.strftime('%Y%m')
            df['상품군분류'] = 'Not Given'
            df['보험사+업적월+시책회차 key'] = df.apply(lambda x: 
                '이관계약' if x['이관계약여부'] == '이관계약' 
                else x['보험사1']+'/'+str(x['업적월']), axis=1)
            return df

        for df_name in df_names:
            if df_name in self.dataframes:
                processed_df = add_columns(self.dataframes[df_name])
                self.dataframes[df_name] = processed_df
                setattr(self, df_name, processed_df)
                
    def process_main_data(self):
        self.main_data['업적월'] = self.main_data['보험사+업적월+상품군 key'].str.split('/', expand = True)[1]
        self.main_data['마감월'] = pd.to_datetime(self.main_data['마감월'], format = '%Y%m', errors = 'coerce')
        self.main_data['업적월'] = pd.to_datetime(self.main_data['업적월'], format = "%Y%m", errors = 'coerce')
        self.main_data['당기해당회차'] = self.main_data['마감월'].dt.to_period('M').astype(int)-self.main_data['업적월'].dt.to_period('M').astype(int)+1
        
    def get_m_count(self, add_df, match_columns_base,match_columns_add, value_column, new_column_name):
        self.main_data['_temp_key'] = list(zip(*[self.main_data[col] for col in match_columns_base]))
        add_df['_temp_key'] = list(zip(*[add_df[col] for col in match_columns_add]))
        value_dict = add_df.groupby('_temp_key')[value_column].first().to_dict()
        self.main_data[new_column_name] = self.main_data['_temp_key'].map(value_dict)
        self.main_data.drop('_temp_key', axis=1, inplace=True)
        add_df.drop('_temp_key', axis=1, inplace=True)
        
        return self.main_data

    def lookup_value(self, lookup_df, base_company_col, look_company_col,  number_col, value_cols, add_str_to_col):
        def find_value(row):
            company = row[base_company_col]
            number = row[number_col]
            matches = lookup_df[lookup_df[look_company_col] == company]
            if not matches.empty and number in value_cols:
                for col in value_cols:
                    if number == col:
                        return matches[add_str_to_col+str(col)].iloc[0]
            return 0  
        return self.main_data.apply(find_value, axis=1)

    def sum_by_company_date(self, add_df, match_columns_base,match_columns_add, value_column, new_column_name):
        self.main_data['_temp_key'] = list(zip(*[self.main_data[col] for col in match_columns_base]))
        add_df['_temp_key'] = list(zip(*[add_df[col] for col in match_columns_add]))
        
        value_dict = add_df.groupby('_temp_key')[value_column].sum().to_dict()
        self.main_data[new_column_name] = self.main_data['_temp_key'].map(value_dict)
        self.main_data[new_column_name] = self.main_data[new_column_name].fillna(0)
    
        alfa = self.main_data[new_column_name]
        
        self.main_data.drop(['_temp_key', new_column_name], axis=1, inplace=True)
        add_df.drop('_temp_key', axis=1, inplace=True)
        
        return alfa
    def process(self):
        self.process_main_data()
        self.add_five_columns(['case_data'])
        self.get_m_count(self.commission_data, ['보험사'],['회사명'], '상품군상품명_수익인식기준회차','수익비용인식회차')
        self.get_m_count(self.commission_data, ['보험사'],['회사명'], '통합_환산성적_환수율적용회차','환수율적용회차')
        self.main_data[['환수율적용회차'  ]] = self.main_data[['환수율적용회차'  ]].fillna(0)
        
        self.main_data['환수율'] = self.lookup_value(self.commission_data, '보험사', '회사명', '당기해당회차', [i for i in range(25)], '성과수수료_' )/100
        self.main_data['유지율'] = self.lookup_value(self.retention_data, '보험사', '회사명', '당기해당회차', [i for i in range(25)], '' )
        self.main_data[['환수율','유지율'  ]] = self.main_data[['환수율','유지율']].fillna(0)
        
        self.main_data['성과(당월)'] = self.sum_by_company_date(self.case_data,['보험사+업적월+상품군 key'], ['보험사+업적월+시책회차 key'], '성과', 'tempo_col'  )
        self.main_data['계약관리(당월)'] = self.sum_by_company_date(self.case_data,['보험사+업적월+상품군 key'], ['보험사+업적월+시책회차 key'], '계약관리', 'tempo_col'  )
        self.main_data['수금(당월)'] = self.sum_by_company_date(self.case_data,['보험사+업적월+상품군 key'], ['보험사+업적월+시책회차 key'], '수금', 'tempo_col'  )
        self.main_data['운영(당월)'] = self.sum_by_company_date(self.case_data,['보험사+업적월+상품군 key'], ['보험사+업적월+시책회차 key'], '운영', 'tempo_col'  )
        self.main_data['기타(당월)'] = self.sum_by_company_date(self.case_data,['보험사+업적월+상품군 key'], ['보험사+업적월+시책회차 key'], '기타', 'tempo_col'  )
        
        self.main_data['성과(누적)'] = self.sum_by_company_date(self.prev_month_data,
                                             ['보험사+업적월+상품군 key'], ['보험사+업적월+상품군 key'],
                                             '성과(누적)', 'tempo_col'  ) + self.main_data['성과(당월)']
        self.main_data['계약관리(누적)'] = self.sum_by_company_date(self.prev_month_data,
                                             ['보험사+업적월+상품군 key'], ['보험사+업적월+상품군 key'],
                                             '계약관리(누적)', 'tempo_col'  ) + self.main_data['계약관리(당월)']
        self.main_data['수금(누적)'] = self.sum_by_company_date(self.prev_month_data,
                                             ['보험사+업적월+상품군 key'], ['보험사+업적월+상품군 key'],
                                             '수금(누적)', 'tempo_col'  ) + self.main_data['수금(당월)']
        self.main_data['운영(누적)'] = self.sum_by_company_date(self.prev_month_data,
                                             ['보험사+업적월+상품군 key'], ['보험사+업적월+상품군 key'],
                                             '운영(누적)', 'tempo_col'  ) + self.main_data['운영(당월)']
        self.main_data['기타(누적)'] = self.sum_by_company_date(self.prev_month_data,
                                             ['보험사+업적월+상품군 key'], ['보험사+업적월+상품군 key'],
                                             '기타(누적)', 'tempo_col'  ) + self.main_data['기타(당월)']
        self.main_data['기초선수수익'] = self.sum_by_company_date(self.prev_month_data,
                                             ['보험사+업적월+상품군 key'], ['보험사+업적월+상품군 key'],
                                             '기말선수수익', 'tempo_col'  )
        self.main_data['당월정액상각대상수령액'] = self.main_data['성과(당월)']
        
        self.main_data['당월누적수익인식액'] = self.main_data.apply(lambda x: x['성과(누적)'] if x['당기해당회차']>x['수익비용인식회차'] else x['성과(누적)']*x['당기해당회차']/x['수익비용인식회차'], axis = 1 )
        self.main_data['전월누적수익인식액'] = self.sum_by_company_date(self.prev_month_data,
                                             ['보험사+업적월+상품군 key'], ['보험사+업적월+상품군 key'],
                                             '당월누적수익인식액', 'tempo_col'  ) 
        self.main_data['당월수익인식액'] = self.main_data['당월누적수익인식액']-self.main_data['전월누적수익인식액']
        self.main_data['기타조정액'] = 0
        self.main_data['기말선수수익'] = self.main_data.apply(lambda x: 0 if x['당기해당회차']>x['수익비용인식회차'] else x['성과(누적)']-x['당월누적수익인식액'], axis = 1 )
        self.main_data['기타조정액'] = self.main_data['기말선수수익']+self.main_data['당월수익인식액']-self.main_data['기초선수수익']-self.main_data['당월정액상각대상수령액']
        self.main_data['기초환수부채'] = self.sum_by_company_date(self.prev_month_data,
                                             ['보험사+업적월+상품군 key'], ['보험사+업적월+상품군 key'],
                                             '기말환수부채', 'tempo_col'  ) 
        self.main_data['당기환수수익조정'] = 0
        
        self.main_data['기말환수부채'] = self.main_data.apply(lambda x: 
                0 if x['기말선수수익'] == 0 else (
                    0 if x['당기해당회차'] > x['수익비용인식회차'] else (
                        x['성과(누적)'] * x['환수율'] * (1 - x['유지율'])
                        if x['성과(누적)'] * x['환수율'] * (1 - x['유지율']) > 0
                        else 0
                    )
                ),
                axis=1
            )
        self.main_data['당기환수수익조정'] = self.main_data['기말환수부채']-self.main_data['기초환수부채']
        
        cols_to_mod = ['당기해당회차', '수익비용인식회차', '환수율적용회차',
        '환수율', '유지율', '기초선수수익','당월정액상각대상수령액', '당월누적수익인식액', '전월누적수익인식액', '당월수익인식액', '기말선수수익', '기타조정액',
        '기초환수부채', '당기환수수익조정', '기말환수부채']
        self.main_data.loc[self.main_data['보험사+업적월+상품군 key'] == '이관계약', cols_to_mod] = 0

        
        self.main_data['마감월'] = self.main_data['마감월'].dt.date        
        self.main_data['업적월'] = self.main_data['업적월'].dt.date
        
        
    def get_final_df(self):
        return self.main_data
        