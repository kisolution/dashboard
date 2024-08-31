from functions.lower_cols import to_lower
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from io import BytesIO
import pandas as pd
from functions.others import income_report, expense_report
from utils.s3_utils import get_file_from_s3, get_cached_file_data
from .models import ProcessedData
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .tasks import process_income_task, process_expense_task
@login_required
def initiate_income_process(request):
    task = process_income_task.delay(request.user.id)
    return render(request, 'processes/processing_started.html', {'process_type': 'income'})

def display_income(request):
    user = request.user
    df = get_cached_file_data('INCOME', user)
    if df is None:
        return render(request, 'uploads/error_template.html', {'message': 'No data available'})
    company_names = df['보험사'].dropna().unique()
    selected_company = request.GET.get('company')
    prev_month_df = get_cached_file_data('INC_PREV_MONTH', user) 
    if selected_company and selected_company != '':
        df_filtered = df[df['보험사'] == selected_company]
    else:
        df_filtered = df
        selected_company = "All"
    if prev_month_df is not None and not prev_month_df.empty:
        prev_month_df = to_lower(prev_month_df)
        if selected_company and selected_company != 'All':
            c18 = prev_month_df[prev_month_df['보험사']==selected_company]['기말선수수익'].sum()
            c19 = prev_month_df[prev_month_df['보험사']==selected_company]['기말환수부채'].sum()
        else:
            c18 = prev_month_df['기말선수수익'].sum()
            c19 = prev_month_df['기말환수부채'].sum()
    else:     
        c18 = c19 = 0
    report_data = income_report(df_filtered, c18_data=c18, c19_data=c19)
    if request.GET.get('download'):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtered.to_excel(writer, index=False, sheet_name='Filtered Data')
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f"income_data{'_' + selected_company if selected_company else ''}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    context = {
        'report_data': report_data,
        'company_names': company_names,
        'selected_company': selected_company if selected_company != 'All' else '',
    }
    return render(request, 'processes/display_income.html', context)

@login_required
def initiate_expense_process(request):
    task1 = process_expense_task.delay(request.user.id)
    return render(request, 'processes/processing_started.html', {'process_type': 'expense'})
@login_required
def display_expense(request):
    user = request.user
    df = get_cached_file_data('EXPENSE', user)
    if df is None:
        return render(request, 'uploads/error_template.html',  {'message': 'No data available'})
    company_names = df['보험사'].dropna().unique()
    selected_company = request.GET.get('company')
    prev_month_df = get_cached_file_data('EXP_PREV_MONTH', user)
    
    
    # Filter data based on selected company
    if selected_company and selected_company != '':
        df_filtered = df[df['보험사'] == selected_company]
    else:
        df_filtered = df
        selected_company = "All"  # Set a default value for filename
    
    # Calculate c18 and c19
    if prev_month_df is not None and not prev_month_df.empty:
        prev_month_df = to_lower(prev_month_df)
        if selected_company and selected_company != 'All':
            c18 = prev_month_df[prev_month_df['보험사']==selected_company]['기말선급비용'].sum()
            c19 = prev_month_df[prev_month_df['보험사']==selected_company]['기말환수자산'].sum()
        else:
            c18 = prev_month_df['기말선급비용'].sum()
            c19 = prev_month_df['기말환수자산'].sum()
    else:     
        c18 = c19 = 0
    
    report_data = expense_report(df_filtered, c18_data=c18, c19_data=c19)
    
    if request.GET.get('download'):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtered.to_excel(writer, index=False, sheet_name='Filtered Data')
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f"expense_data_{selected_company}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    context = {
        'report_data': report_data,
        'company_names': company_names,
        'selected_company': selected_company if selected_company != "All" else ""
    }
    return render(request, 'processes/display_expense.html', context)



@login_required
def show_history(request):
    income_datas = ProcessedData.objects.filter(user = request.user, data_type = 'INCOME').order_by('-upload_date')
    expense_datas = ProcessedData.objects.filter(user = request.user, data_type = 'EXPENSE').order_by('-upload_date')
    context = {'income_datas':income_datas, 'expense_datas':expense_datas}
    return render(request, 'processes/process_history.html', context)

def download_history(request, s3_key):
    try:
        
        s3_key = str.lower(s3_key)
        df = get_file_from_s3(s3_key)
        if df is None:
            return HttpResponse(f"No sample data available for {s3_key}", status=404)
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={s3_key}.xlsx'
        
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sample')
        
        return response
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)
  