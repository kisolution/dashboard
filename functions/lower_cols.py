def to_lower(df):
    columns_to_lower = ['보험사명', '보험사', '회사명', '보험사+업적월+시책회차 key', 
                        '보험사+업적월+상품군 key', '보험사+업적월+시책회차 key']
    for col in df.columns:
        if col in columns_to_lower and df[col].dtype == 'object':
            df[col] = df[col].str.lower()
    return df