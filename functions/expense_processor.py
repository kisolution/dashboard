import pandas as pd
import datetime

class ExpenseProcessor:
    def __init__(self, static_data, expense_data):
        self.main_df = None
        
        # Initialize a dictionary to hold all dataframes
        self.dataframes = {
            #**static_data,
            **expense_data
        }
        
        # Set all dataframes as attributes
        for key, value in self.dataframes.items():
            setattr(self, key, value)
        
        # Apply lower case to relevant columns
        self.to_lower()

    def to_lower(self):
        columns_to_lower = ['보험사명', '보험사', '회사명', '보험사+업적월+시책회차 key', 
                            '보험사+업적월+상품군 key', '보험사+업적월+시책회차 key', '보험사+업적월+채널 key']
        
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
            df['이관계약여부'] = df['계약일'].apply(lambda x: "이관계약" if x < datetime.date(2023, 7, 1) else ('이관계약' if x == '' else "회사보유계약"))
            df['보험사1'] = df['보험사'] if '보험사' in df.columns else 'Unknown'
            df['업적월'] = pd.to_datetime(df['계약일']).dt.strftime('%Y%m')
            df['상품군분류'] = 'Not Given'
            df['보험사+업적월+시책회차 key'] = df.apply(lambda x: 
                '이관계약' if x['이관계약여부'] == '이관계약' 
                else x['보험사1']+'/'+str(x['채널'])+'/'+str(x['업적월']), axis=1)
            return df

        for df_name in df_names:
            if df_name in self.dataframes:
                processed_df = add_columns(self.dataframes[df_name])
                self.dataframes[df_name] = processed_df
                setattr(self, df_name, processed_df)

    def process_main_df(self):
        self.commission_df.columns = self.commission_df.columns.astype(str)
        self.retention_df.columns = self.retention_df.columns.astype(str)
        self.commission_df['전속(직영)/전략(지사)'] = self.commission_df['전속(직영)/전략(지사)'].fillna('전속(직영)/전략(지사)')
        #self.retention_df['전속(직영)/전략(지사)'] = self.retention_df['전속(직영)/전략(지사)'].fillna('전속(직영)/전략(지사)')
        self.main_df['업적월'] = self.main_df['보험사+업적월+채널 key'].str.split('/', expand = True)[2]
        self.main_df['마감월'] = pd.to_datetime(self.main_df['마감월'], format = '%Y%m', errors = 'coerce')
        self.main_df['업적월'] = pd.to_datetime(self.main_df['업적월'], format = "%Y%m", errors = 'coerce')
        self.main_df['당기해당회차'] = self.main_df['마감월'].dt.to_period('M').astype(int)-self.main_df['업적월'].dt.to_period('M').astype(int)+1
        
    def get_m_count(self, add_df, match_columns_base,match_columns_add, value_column, new_column_name):
        self.main_df['_temp_key'] = list(zip(*[self.main_df[col] for col in match_columns_base]))
        add_df['_temp_key'] = list(zip(*[add_df[col] for col in match_columns_add]))
        value_dict = add_df.groupby('_temp_key')[value_column].first().to_dict()
        self.main_df[new_column_name] = self.main_df['_temp_key'].map(value_dict)
        self.main_df.drop('_temp_key', axis=1, inplace=True)
        add_df.drop('_temp_key', axis=1, inplace=True)
        
        return self.main_df
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
    
    def sum_by_company_date(self, add_df, match_columns_base,match_columns_add, value_column, new_column_name):
        self.main_df['_temp_key'] = list(zip(*[self.main_df[col] for col in match_columns_base]))
        add_df['_temp_key'] = list(zip(*[add_df[col] for col in match_columns_add]))
        
        value_dict = add_df.groupby('_temp_key')[value_column].sum().to_dict()
        self.main_df[new_column_name] = self.main_df['_temp_key'].map(value_dict)
        self.main_df[new_column_name] = self.main_df[new_column_name].fillna(0).infer_objects(copy=False)
    
        alfa = self.main_df[new_column_name]
        
        self.main_df.drop(['_temp_key', new_column_name], axis=1, inplace=True)
        add_df.drop('_temp_key', axis=1, inplace=True)
        
        return alfa

    def process(self):
        self.process_main_df()
        self.add_five_columns(['retirement_df', 'override_df', 'security_df'])
        self.get_m_count(self.commission_df, ['보험사','채널'],['보험사','전속(직영)/전략(지사)'], '수익비용인식회차','수익비용인식회차')
        self.get_m_count(self.commission_df, ['보험사','채널'],['보험사','전속(직영)/전략(지사)'], '환수율인식회차','환수율인식회차')
        
        self.main_df['환수율(성과수수료)'] = self.lookup_value(self.commission_df, ['보험사','채널'],['보험사','전속(직영)/전략(지사)'], '당기해당회차', [i for i in range(1,25)], '' )
        self.main_df['환수율(유지성과수수료)'] = self.lookup_value(self.commission_df, ['보험사','채널'],['보험사','전속(직영)/전략(지사)'], '당기해당회차', [i for i in range(13,26)], '유지_' )
        self.main_df['유지율'] = self.lookup_value(self.retention_df, ['보험사'],['회사명'], '당기해당회차', [i for i in range(1,26)], '' )
        
        self.main_df['[지급수수료] 신계약성과(당월)'] = self.sum_by_company_date(self.security_df, ['보험사+업적월+채널 key'], ['보험사+업적월+시책회차 key'], '[지급수수료] 신계약성과', 
                                                                'temporary_col')+self.sum_by_company_date(self.retirement_df, ['보험사+업적월+채널 key'], ['보험사+업적월+시책회차 key'], 
                                                                                                     '[지급수수료] 신계약성과', 'temporary_col')

        self.main_df['[지급수수료] 유지관리(당월)'] = self.sum_by_company_date(self.security_df, ['보험사+업적월+채널 key'], ['보험사+업적월+시책회차 key'], '[지급수수료] 유지관리', 
                                                               'temporary_col')+self.sum_by_company_date(self.retirement_df, ['보험사+업적월+채널 key'], ['보험사+업적월+시책회차 key'],
                                                                                                    '[지급수수료] 유지관리', 'temporary_col')

        self.main_df['[지급수수료] 유지성과(당월)'] = self.sum_by_company_date(self.security_df, ['보험사+업적월+채널 key'], ['보험사+업적월+시책회차 key'], '[지급수수료] 유지성과', 
                                                               'temporary_col')+self.sum_by_company_date(self.retirement_df, ['보험사+업적월+채널 key'], ['보험사+업적월+시책회차 key'], '[지급수수료] 유지성과', 
                                                                                                    'temporary_col')
        
        self.main_df['[지급수수료] 자동차(당월)'] = self.sum_by_company_date(self.security_df, ['보험사+업적월+채널 key'], ['보험사+업적월+시책회차 key'], '[지급수수료] 자동차', 'temporary_col')
        
        self.main_df['[지급수수료] 일반(당월)'] = self.sum_by_company_date(self.security_df, ['보험사+업적월+채널 key'], ['보험사+업적월+시책회차 key'], '[지급수수료] 일반', 'temporary_col')
        
        self.main_df['[지급수수료] 오버라이드성과(당월)'] = self.sum_by_company_date(self.override_df, ['보험사+업적월+채널 key'], ['보험사+업적월+시책회차 key'], '[지급수수료] 성과', 'temporary_col')
        
        self.main_df['[지급수수료] 오버라이드육성(당월)'] = self.sum_by_company_date(self.override_df, ['보험사+업적월+채널 key'], ['보험사+업적월+시책회차 key'], '[지급수수료] 육성', 'temporary_col')
                
        
        self.main_df['[지급수수료] 신계약성과(누적)'] = self.sum_by_company_date(self.prev_month_df, ['보험사+업적월+채널 key'],
                                                        ['보험사+업적월+채널 key'],
                                                        '[지급수수료] 신계약성과(누적)', 
                                                        'temporary_col')+self.main_df['[지급수수료] 신계약성과(당월)']

        self.main_df['[지급수수료] 유지관리(누적)'] = self.sum_by_company_date(self.prev_month_df, ['보험사+업적월+채널 key'],
                                                                ['보험사+업적월+채널 key'],
                                                                '[지급수수료] 유지관리(누적)', 
                                                                'temporary_col')+self.main_df['[지급수수료] 유지관리(당월)']
        
        self.main_df['[지급수수료] 유지성과(누적)'] = self.sum_by_company_date(self.prev_month_df, ['보험사+업적월+채널 key'],
                                                                ['보험사+업적월+채널 key'],
                                                                '[지급수수료] 유지성과(누적)', 
                                                                'temporary_col')+self.main_df['[지급수수료] 유지성과(당월)']
        
        self.main_df['[지급수수료] 자동차(누적)'] = self.sum_by_company_date(self.prev_month_df, ['보험사+업적월+채널 key'],
                                                                ['보험사+업적월+채널 key'],
                                                                '[지급수수료] 자동차(누적)', 
                                                                'temporary_col')+self.main_df['[지급수수료] 자동차(당월)']
        
        self.main_df['[지급수수료] 일반(누적)'] = self.sum_by_company_date(self.prev_month_df, ['보험사+업적월+채널 key'],
                                                                ['보험사+업적월+채널 key'],
                                                                '[지급수수료] 일반(누적)', 
                                                                'temporary_col')+self.main_df['[지급수수료] 일반(당월)']
        
        self.main_df['[지급수수료] 오버라이드성과(누적)'] = self.sum_by_company_date(self.prev_month_df, ['보험사+업적월+채널 key'],
                                                                ['보험사+업적월+채널 key'],
                                                                '[지급수수료] 오버라이드성과(누적)', 
                                                                'temporary_col')+self.main_df['[지급수수료] 오버라이드성과(당월)']
        
        self.main_df['[지급수수료] 오버라이드육성(누적)'] = self.sum_by_company_date(self.prev_month_df, ['보험사+업적월+채널 key'],
                                                                ['보험사+업적월+채널 key'],
                                                                '[지급수수료] 오버라이드육성(누적)', 
                                                                'temporary_col')+self.main_df['[지급수수료] 오버라이드육성(당월)']
        
        self.main_df['기초선급비용'] = self.sum_by_company_date(self.prev_month_df, ['보험사+업적월+채널 key'],
                                                                ['보험사+업적월+채널 key'],
                                                                '기말선급비용', 
                                                                'temporary_col')

        self.main_df['당월정액상각대상수지급액'] = self.main_df[['[지급수수료] 신계약성과(당월)', '[지급수수료] 유지성과(당월)', '[지급수수료] 오버라이드성과(당월)']].sum(axis = 1)

        self.main_df['당월누적비용인식액'] = self.main_df.apply(lambda x: x['[지급수수료] 신계약성과(누적)']+x['[지급수수료] 오버라이드성과(누적)'] if x['당기해당회차']>x['수익비용인식회차'] else 
                         (x['[지급수수료] 신계약성과(누적)']+x['[지급수수료] 오버라이드성과(누적)'])*x['당기해당회차']/x['수익비용인식회차'], axis = 1)
        
        self.main_df['전월누적비용인식액'] = self.sum_by_company_date(self.prev_month_df, ['보험사+업적월+채널 key'],
                                                                ['보험사+업적월+채널 key'],
                                                                '당월누적비용인식액', 
                                                                'temporary_col')
        
        self.main_df['당월비용인식액'] = self.main_df['당월누적비용인식액'] -  self.main_df['전월누적비용인식액']
        
        self.main_df['기타조정액'] = self.main_df.apply(lambda x: -(x['기초선급비용']+x['당월정액상각대상수지급액']-x['당월비용인식액']) if x['기초선급비용']+x['당월정액상각대상수지급액']-x['당월비용인식액'] < 0 else 0, axis = 1)
        
        self.main_df['기말선급비용']=self.main_df.apply(lambda x: x['기초선급비용']+x['당월정액상각대상수지급액']-x['당월비용인식액']+x['기타조정액'], axis = 1)
        
        self.main_df['기초환수자산'] = self.sum_by_company_date(self.prev_month_df, ['보험사+업적월+채널 key'],
                                                                ['보험사+업적월+채널 key'],
                                                                '기말환수자산', 
                                                                'temporary_col')

        self.main_df['당기환수비용조정'] = 0

        self.main_df['기말환수자산'] = self.main_df.apply(lambda x: 
            0 if x['기말선급비용'] == 0 else (
                0 if x['당기해당회차']>x['수익비용인식회차'] else (
                    (x['[지급수수료] 신계약성과(누적)'] + x['[지급수수료] 오버라이드성과(누적)']) * x['환수율(성과수수료)'] * 
                    (1 - x['유지율'])+x['[지급수수료] 유지성과(누적)']*x['환수율(성과수수료)'] * (1 - x['유지율'])
                    if (x['[지급수수료] 신계약성과(누적)'] + x['[지급수수료] 오버라이드성과(누적)']) * x['환수율(성과수수료)'] * 
                    (1 - x['유지율'])+x['[지급수수료] 유지성과(누적)']*x['환수율(성과수수료)'] * (1 - x['유지율']) > 0 else 
                    0
                )
            ),
            axis=1
        )
        
        self.main_df['당기환수비용조정']= self.main_df['기말환수자산']-self.main_df['기초환수자산']
        
        columns_to_modify = [ '당기해당회차', '수익비용인식회차', '환수율적용회차',
               '환수율(성과수수료)', '환수율(유지성과수수료)', '유지율','기초선급비용', '당월정액상각대상수지급액', '당월누적비용인식액',
               '전월누적비용인식액', '당월비용인식액', '기타조정액', '기말선급비용', '기초환수자산', '당기환수비용조정',
               '기말환수자산' ]
        
        self.main_df.loc[self.main_df['보험사+업적월+채널 key'] == '이관계약', columns_to_modify] = 0
        self.main_df['마감월'] = self.main_df['마감월'].dt.date        
        self.main_df['업적월'] = self.main_df['업적월'].dt.date
        
    def get_final_df(self):
        return self.main_df