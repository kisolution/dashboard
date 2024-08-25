from django.shortcuts import render, redirect
from django.contrib import messages
from functions.lower_cols import to_lower
from processes.models import ProcessedData
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from io import BytesIO
import pandas as pd

from functions.others import income_report, expense_report

from utils.s3_utils import get_latest_income_data, get_latest_expense_data, get_file_from_s3, get_static_data
import logging
from django.core.cache import cache
from django.utils import timezone
from io import BytesIO
from django.core.files.base import ContentFile

from functions.income_processor import IncomeProcessor
from functions.expense_processor import ExpenseProcessor


logger = logging.getLogger(__name__)




@login_required
def fetch_income_data(request):
    user = request.user
    cache_key = f"income_data_{user.id}"

    try:
        static_data = get_static_data()
        income_data = get_latest_income_data(user)
        
        if income_data is None:
            return render(request, 'uploads/error_template.html', {'error': 'No income data available or error reading from S3'})
        
        # Cache the data for the next step
        cache.set(cache_key, (static_data, income_data), 75600)  # Cache for 1 hour
        
        return render(request, 'processes/process_income.html', {'step': 'process'})
    except Exception as e:
        return render(request, 'uploads/error_template.html', {'error': f"An error occurred while fetching the data: {str(e)}"})
@login_required
def process_income(request):
    user = request.user
    cache_key = f"income_data_{user.id}"
    processed_cache_key = f"processed_income_{user.id}"

    try:
        cached_data = cache.get(cache_key)
        if not cached_data:
            return redirect('fetch_income_data')
        
        static_data, income_data = cached_data
        
        process = IncomeProcessor(static_data, income_data)
        process.process()
        final_df = process.get_final_df()
        
        # Generate a unique filename
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f"processed_income_data_{timestamp}.xlsx"
        
        # Define S3 key
        s3_key = f"processed_folder/{filename}"
        
        # Save to BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='Processed Income Data')
        buffer.seek(0)
        
        # Create ProcessedData instance
        processed_data = ProcessedData(
            user=user,
            filename=filename,
            s3_key=s3_key,
            data_type='INCOME'
        )
        
        # Save file to S3 and update ProcessedData
        processed_data.file_upload.save(filename, ContentFile(buffer.getvalue()), save=True)
        
        # Update cache with processed data
        cache.set(processed_cache_key, final_df.to_dict(), 75600) 

        return redirect('display_income')
    except Exception as e:
        return render(request, 'uploads/error_template.html', {'error': f"An error occurred while processing the data: {str(e)}"})



@login_required
def fetch_expense_data(request):
    user = request.user
    cache_key = f"expense_data_{user.id}"

    try:
        static_data = get_static_data()
        expense_data = get_latest_expense_data(user)
        
        if expense_data is None:
            return render(request, 'uploads/error_template.html', {'error': 'No income data available or error reading from S3'})
        
        # Cache the data for the next step
        cache.set(cache_key, (static_data, expense_data), 3600)  # Cache for 1 hour
        
        return render(request, 'processes/process_expense.html', {'step': 'process'})
    except Exception as e:
        return render(request, 'uploads/error_template.html', {'error': f"An error occurred while fetching the data: {str(e)}"})
@login_required
def process_expense(request):
    user = request.user
    cache_key = f"expense_data_{user.id}"
    processed_cache_key = f"processed_expense_{user.id}"

    try:
        cached_data = cache.get(cache_key)
        if not cached_data:
            return redirect('fetch_expense_data')
        
        static_data, expense_data = cached_data
        
        process = ExpenseProcessor(static_data, expense_data)
        process.process()
        final_df = process.get_final_df()
        
        # Generate a unique filename
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f"processed_income_data_{timestamp}.xlsx"
        
        # Define S3 key
        s3_key = f"processed_folder/{filename}"
        
        # Save to BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='Processed Expense Data')
        buffer.seek(0)
        
        # Create ProcessedData instance
        processed_data = ProcessedData(
            user=user,
            filename=filename,
            s3_key=s3_key,
            data_type='EXPENSE'
        )
        
        # Save file to S3 and update ProcessedData
        processed_data.file_upload.save(filename, ContentFile(buffer.getvalue()), save=True)
        
        # Update cache with processed data
        cache.set(processed_cache_key, final_df.to_dict(), 3600) 

        return redirect('display_expense')
    except Exception as e:
        return render(request, 'uploads/error_template.html', {'error': f"An error occurred while processing the data: {str(e)}"})

@login_required
def display_income(request):
    user = request.user
    
    processed_cache_key = f"processed_income_{user.id}"
    cached_data = cache.get(processed_cache_key)

    if not cached_data:
        # If there's no cached data, check for the latest processed data in the database
        latest_processed = ProcessedData.objects.filter(user=user, data_type='INCOME').order_by('-upload_date').first()
        if not latest_processed:
            return render(request, 'processes/no_data.html', {'process_type': 'income','message': 'No processed data available. Please process the data first.'})
        df = pd.read_excel(BytesIO(latest_processed.file_upload.read()))
    else:
        # If there's cached data, use it
        df = pd.DataFrame(cached_data)

    company_names = df['보험사'].dropna().unique()
    selected_company = request.GET.get('company')
    
    # Fetch previous month data
    income_data = get_latest_income_data(user)
    if income_data is None:
        return render(request, 'processes/no_data.html', {'process_type': 'income','message': 'Previous month data is not accessible'})
    prev_month_df = income_data['prev_month_data']

    if selected_company and selected_company != '':
        df_filtered = df[df['보험사'] == selected_company]
    else:
        df_filtered = df
        selected_company = "All"  # Set a default value for filename
    
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
        'selected_company': selected_company if selected_company != 'All' else ''
    }
    return render(request, 'processes/display_income.html', context)
@login_required
def display_expense(request):
    user = request.user
    processed_cache_key = f"processed_expense_{user.id}"
    cached_data = cache.get(processed_cache_key)

    if not cached_data:
        # If there's no cached data, check for the latest processed data in the database
        latest_processed = ProcessedData.objects.filter(user=user, data_type='EXPENSE').order_by('-upload_date').first()
        if not latest_processed:
            return render(request, 'processes/no_data.html', {'process_type': 'expense','message': 'No processed data available. Please process the data first.'})
        df = pd.read_excel(BytesIO(latest_processed.file_upload.read()))
    else:
        # If there's cached data, use it
        df = pd.DataFrame(cached_data)

    company_names = df['보험사'].dropna().unique()
    selected_company = request.GET.get('company')
    
    expense_data = get_latest_expense_data(user)
    if expense_data is None:
        return render(request, 'processes/no_data.html', {'process_type': 'expense','message': 'Error fetching expense data.'})
    
    prev_month_df = expense_data['prev_month_df']
    
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
  