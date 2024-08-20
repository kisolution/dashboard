from django.shortcuts import render, redirect
from .forms import LeasingInput
import pandas as pd
from datetime import datetime
import numpy as np
from babel.numbers import format_currency
import io
from io import BytesIO
import base64
import os
import pandas as pd
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
file_path = os.path.join(settings.BASE_DIR, 'leasing', 'files', 'leasing_percents.xlsx')
percents_df = pd.read_excel(file_path)
  # Assuming you have this form
@login_required
def process_leasing(request):
    form = LeasingInput(request.POST or None)
    final_df_html = None
    df = pd.DataFrame()

    if request.method == 'POST' and form.is_valid():
        rent_value = form.cleaned_data['first_month_rent_value']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        if end_date > start_date:
            df = generate_lease_table(rent_value, start_date, end_date)
            final_df_html = df.to_html(classes='table table-striped table-hover', index=False)
        # Store DataFrame in session for download
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        buffer.seek(0)
        excel_data = buffer.getvalue()
        
        # Encode the binary data to base64 string
        excel_data_b64 = base64.b64encode(excel_data).decode('utf-8')
        request.session['download_data'] = excel_data_b64

    if request.GET.get('download') == 'true' and 'download_data' in request.session:
        # Decode the base64 string back to binary data
        excel_data = base64.b64decode(request.session['download_data'])
        response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="leasing_data.xlsx"'
        del request.session['download_data']  # Clear the session data after download
        return response

    context = {
        'form': form,
        'final_df': final_df_html,
        'df_empty': df.empty
    }
    return render(request, 'leasing/get_inputs.html', context)
def generate_lease_table(main_value, start_date, end_date):
    
    #start_date = datetime.strptime(start_date_str, '%Y.%m.%d')
    #end_date = datetime.strptime(end_date_str, '%Y.%m.%d')
    
    
    number_of_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
    date_range = pd.date_range(start=start_date, periods=number_of_months, freq='ME')
    
    df = pd.DataFrame({'date': date_range})
    df['main'] = main_value
    
    per = percents_df[percents_df['month'] == len(df['main'])]['percent'].iloc[0]
    df['percent'] = per
    df['month_count'] = df.index
    df['monthly_percent'] = df['percent'] / 12
    df['month_count'] = df['month_count'].astype('int')
    df['rent_pv'] = np.round(df['main'] / ((1 + df['monthly_percent']) ** df['month_count']))

    origin_list = []
    percen_list = []

    for i in df.index:
        if i == 0:
            origin = np.sum(df['rent_pv']) - df.loc[i, 'main']
            percen = origin * df.loc[i, 'monthly_percent']
        elif i > 0:
            origin = origin + percen - df.loc[i, 'main']
            percen = origin * df.loc[i, 'monthly_percent']
        origin_list.append(origin)
        percen_list.append(percen)

    df['main_amount'] = origin_list
    df['main_amount'] = df['main_amount'].astype(int)
    df['percentage_amount'] = percen_list
    df['percentage_amount'] = df['percentage_amount'].astype(int)
    
    df['amortization'] = np.round(np.sum(df['rent_pv']) / len(df['main']))
    df['amortization'] = df['amortization'].astype(int)
    df['accumulated_depr'] = np.cumsum(df['amortization'])
    
    currency_columns = ['main', 'rent_pv', 'main_amount', 'percentage_amount', 'amortization', 'accumulated_depr']
    for col in currency_columns:
        df[col] = df[col].apply(lambda x: format_currency(x, 'KRW', locale='ko_KR'))

    df.columns = ["Date",	"Initial Lease Liability",	"Annual Interest Rate",	"Month Count", "Monthly Interest",	"PV of Lease",	"Remaining Lease Liability",	"Interest Expense",	"Amortization",	"Accumulated Depreciation"]
    
    return df