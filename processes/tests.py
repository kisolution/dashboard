from urllib import response
from urllib.parse import unquote
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from functions.income_processor import IncomeProcessor
from functions.expense_processor import ExpenseProcessor
from functions.lower_cols import to_lower
from processes.models import ProcessedData
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from io import BytesIO
import pandas as pd
from django.utils import timezone
from django.core.files.base import ContentFile

from utils.s3_utils import get_static_data, get_latest_income_data, get_latest_expense_data, upload_to_s3,get_cached_file_data, get_expense_processed_data, get_income_processed_data, get_file_from_s3
import logging

logger = logging.getLogger(__name__)
@login_required
def display_income(request):
    user = request.user
    
    cache_key = f"processed_income_{user.id}"
    latest_processed = ProcessedData.objects.filter(user=user, data_type='INCOME').order_by('-upload_date').first()
    if not latest_processed:
        return render(request, 'processes/no_data.html', {'process_type': 'income','message': 'No processed data available. Please process the data first.'})
    df = pd.read_excel(BytesIO(latest_processed.file_upload.read()))
    company_names = df['보험사'].dropna().unique()
    selected_company = request.GET.get('company')
    income_data = get_latest_income_data(user)
    if income_data is None:
        return render(request, 'processes/no_data.html', {'process_type': 'income','message': 'Previous month data is not accessibe'})
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
    report_data = betta(df_filtered, c18_data=c18, c19_data=c19)
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
        'company_names':company_names,
        'selected_company':selected_company if selected_company!= 'All' else ''
    }
    return render(request, 'processes/display_income.html', context)
def betta(df, c18_data, c19_data):
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


@login_required
def process_income(request):
    user = request.user
    cache_key = f"processed_income_{user.id}"

    try:
        static_data = get_static_data()
        income_data = get_latest_income_data(user)
        
        if income_data is None:
            logger.error("No income data available or error reading from S3")
            return render(request, 'uploads/error_template.html', {'error': 'No income data available or error reading from S3'})
        
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
        
        # Update cache
        final_df_html = final_df.to_html(classes='table table-striped table-hover', index=False)
        cache.set(cache_key, final_df_html, 3600)  # Cache for 1 hour

        return redirect('display_income')
    except Exception as e:
        logger.exception(f"Error in process_income view: {e}")
        return render(request, 'uploads/error_template.html', {'error': f"An error occurred while processing the data: {str(e)}"})


### Expense
@login_required
def display_expense(request):
    user = request.user
    
    cache_key = f"processed_expense_{user.id}"
    latest_processed = ProcessedData.objects.filter(user=user, data_type='EXPENSE').order_by('-upload_date').first()
    if not latest_processed:
        return render(request, 'processes/no_data.html', {'process_type': 'expense','message': 'No processed data available. Please process the data first.'})
    
    df = pd.read_excel(BytesIO(latest_processed.file_upload.read()))
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
    
    report_data = alfa(df_filtered, c18_data=c18, c19_data=c19)
    
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

def alfa(df, c18_data, c19_data):
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

@login_required
def process_expense(request):
    user = request.user
    cache_key = f"processed_expense_{user.id}"

    try:
        static_data = get_static_data()
        expense_data = get_latest_expense_data(user)
        
        if expense_data is None:
            logger.error("No expense data available or error reading from S3")
            return render(request, 'uploads/error_template.html', {'error': 'No income data available or error reading from S3'})
        
        process = ExpenseProcessor(static_data, expense_data)
        process.process()
        final_df = process.get_final_df()
        
        # Generate a unique filename
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        filename = f"processed_expense_data_{timestamp}.xlsx"
        
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
        
        # Update cache
        final_df_html = final_df.to_html(classes='table table-striped table-hover', index=False)
        cache.set(cache_key, final_df_html, 3600)  # Cache for 1 hour

        return redirect('display_expense')
    except Exception as e:
        logger.exception(f"Error in process_income view: {e}")
        return render(request, 'uploads/error_template.html', {'error': f"An error occurred while processing the data: {str(e)}"})
    

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




@login_required
def process_income(request):
    user = request.user
    try:
        # Schedule the background task
        task = process_income_task(user.id)
        # Store the task id in the session
        request.session['income_processing_task_id'] = task.id
        messages.info(request, "Income processing has started. You'll be notified when it's complete.")
        return redirect('income_processing_status')
    except Exception as e:
        logger.error(f"Error in process_income: {str(e)}")
        return render(request, 'uploads/error_template.html', {'error': "An error occurred. Please try again later."})

@login_required
def income_processing_status(request):
    task_id = request.session.get('income_processing_task_id')
    if not task_id:
        messages.warning(request, "No processing task found.")
        return redirect('home')

    try:
        task = Task.objects.get(id=task_id)
        if task.last_error:
            error = task.last_error
            return render(request, 'uploads/error_template.html', {'error': error})
        elif task.locked_by is None and task.locked_at is None:
            # Task is completed
            del request.session['income_processing_task_id']
            return redirect('display_income')
        else:
            # Task is still running
            return render(request, 'uploads/processing_status.html', {'task_id': task_id})
    except Task.DoesNotExist:
        messages.warning(request, "Processing task not found. It may have been completed or removed.")
        return redirect('home')
def check_task_status(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        if task.last_error:
            return JsonResponse({'status': 'FAILURE', 'error': task.last_error})
        elif task.locked_by is None and task.locked_at is None:
            return JsonResponse({'status': 'SUCCESS'})
        else:
            return JsonResponse({'status': 'PENDING'})
    except Task.DoesNotExist:
        return JsonResponse({'status': 'FAILURE', 'error': 'Task not found'})
