def income_report(df, c18_data, c19_data):
    e5 = df['당월정액상각대상수령액'].sum()
    c5 = e5
    c8 = df['당월수익인식액'].sum()
    e8 = c8
    e11 = df['당기환수수익조정'].sum()
    c11 = e11
    c14 = df['기타조정액'].sum()
    e14 = c14
    c18 = c18_data
    c19 = c19_data
    d23 = c18 + c5 - e8 + c14
    e23 = df['기말선수수익'].sum()
    f23 = d23 - e23
    d24 = c19 + c11
    e24 = df['기말환수부채'].sum()
    f24 = d24 - e24
    return {
        'e5': e5, 'c5': c5, 'c8': c8, 'e8': e8, 'e11': e11, 'c11': c11,
        'c14': c14, 'e14': e14, 'c18': c18, 'c19': c19, 'd23': d23,
        'e23': e23, 'f23': f23, 'd24': d24, 'e24': e24, 'f24': f24
    }  


def expense_report(df, c18_data, c19_data):
    e5 = df['당월정액상각대상수지급액'].sum()
    c5 = e5
    c8 = df['당월비용인식액'].sum()
    e8 = c8
    e11 = df['당기환수비용조정'].sum()
    c11 = e11
    c14 = df['기타조정액'].sum()
    e14 = c14
    c18 = c18_data
    c19 = c19_data
    d23 = c18 + c5 - e8 + c14
    e23 = df['기말선급비용'].sum()
    f23 = d23 - e23
    d24 = c19 + c11
    e24 = df['기말환수자산'].sum()
    f24 = d24 - e24
    return {
        'e5': e5, 'c5': c5, 'c8': c8, 'e8': e8, 'e11': e11, 'c11': c11,
        'c14': c14, 'e14': e14, 'c18': c18, 'c19': c19, 'd23': d23,
        'e23': e23, 'f23': f23, 'd24': d24, 'e24': e24, 'f24': f24
    }

