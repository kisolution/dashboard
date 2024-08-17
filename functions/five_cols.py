import datetime
import pandas as pd
import numpy as np

def add_five_columns(df):
    df = df.dropna(thresh = 10)
    df['계약일'] = pd.to_datetime(df['계약일'], errors = 'coerce').dt.date
    df['계약일'] = df['계약일'].fillna(datetime.date(2000, 1, 1))
    df['이관계약여부'] = df['계약일'].apply(lambda x: "이관계약" if x  < datetime.date(2023, 7, 1) else "회사보유계약")
    df['보험사1'] = df['보험사'] 
    df['업적월'] = pd.to_datetime(df['계약일']).dt.strftime('%Y%m')
    df['상품군분류'] = 'Not Given'
    df['보험사+업적월+시책회차 key'] = df.apply(lambda x: 
                                                      '이관계약' if x['이관계약여부'] == '이관계약' 
                                                      else x['보험사1']+'/'+str(x['업적월']), axis = 1)
 
    
    return df
