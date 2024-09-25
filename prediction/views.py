from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render
from processes.models import ProcessedData
from utils.s3_utils import get_cached_file_data
from functions.income_prediction import PredictIncome
from .models import PredictionData

import datetime
import pandas as pd
from .tasks import predict_income_task, predict_expense_task
from django.contrib.auth.decorators import login_required


@login_required
def initiate_income_prediction(request):
    task1 = predict_income_task.delay(request.user.id)
    return render(request, 'prediction/processing_started.html', {'process_type': 'income'})


@login_required
def initiate_expense_prediction(request):
    task2 = predict_expense_task.delay(request.user.id)
    return render(request, 'prediction/processing_started.html', {'process_type': 'expense'})


def safe_strftime(dt, format='%Y-%m-%d %H:%M:%S'):
    return dt.strftime(format) if pd.notnull(dt) else ''

def format_value(value):
    if pd.isna(value):
        return ''
    elif isinstance(value, (int, float)):
        return round(value,2)
    elif isinstance(value, pd.Timestamp):
        return safe_strftime(value)
    else:
        return value
@login_required   
def display_income_prediction(request):
    user = request.user
    df_name = PredictionData.objects.filter(user = user, data_type = 'INCOME_PRE').order_by('-upload_date').first()
    print(df_name)
    df = get_cached_file_data('INCOME_PRE', user)
    print(df.columns)
    if df is None:
        error = 'First you have to start prediction process'
        return render(request, 'uploads/error_template.html', {'error':error})
    formatted_df = df.applymap(format_value)
    
    currency_columns = ['성과(당월)','성과(누적)', '당월누적수익인식액','당월수익인식액', '1', '2', '3', '4', '5', '6',
       '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
       '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
       '31', '32', '33', '34', '35', '36']  # Replace with your actual currency column names
    for col in currency_columns:
        formatted_df[col] = formatted_df[col].apply(lambda x: f"₩{x:,.0f}")  # Assuming Korean Won, adjust symbol as needed
    
    if request.GET.get('download'):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Filtered Data')
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f"predicted_income_data.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return render(request, 'prediction/display_income_prediction.html', {'df': formatted_df.to_dict('records')})
    
@login_required   
def display_expense_prediction(request):
    user = request.user
    df = get_cached_file_data('EXPENSE_PRE', user)
    if df is None:
        error = 'There is no Data to show, so first please process it'
        return render(request, 'uploads/error_template.html', {'error':error})
    formatted_df = df.applymap(format_value)
    
    currency_columns = ['[지급수수료] 신계약성과(당월)',
       '[지급수수료] 신계약성과(누적)', '당월누적비용인식액', '당월비용인식액', '1', '2', '3', '4', '5',
       '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17',
       '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
       '30', '31', '32', '33', '34', '35', '36']  # Replace with your actual currency column names
    
    for col in currency_columns:
        formatted_df[col] = formatted_df[col].apply(lambda x: f"₩{x:,.0f}") 
         # Assuming Korean Won, adjust symbol as needed
    
    if request.GET.get('download'):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Filtered Data')
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f"predicted_expense_data.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return render(request, 'prediction/display_expense_prediction.html', {'df': formatted_df.to_dict('records')})
    
