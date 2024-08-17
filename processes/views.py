from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.cache import cache
from functions.main_processor import IncomeProcessor
from functions.processor_second_main import ExpenseProcessor
from uploads.models import IncomeUpload, ExpenseUpload
from processes.models import ProcessedData
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from io import BytesIO
import pandas as pd
from django_q.tasks import async_task
from django.utils import timezone
from django.core.files.base import ContentFile
import uuid

from utils.s3_utils import get_static_data, get_latest_income_data, get_latest_expense_data, upload_to_s3, get_expense_processed_data, get_income_processed_data
import logging

logger = logging.getLogger(__name__)
@login_required
def display_income(request):
    user = request.user
    cache_key = f"processed_income_{user.id}"
    
    # Try to get processed data from cache
    final_df_html = cache.get(cache_key)
    
    if not final_df_html:
        # If not in cache, try to get from database
        latest_processed = ProcessedData.objects.filter(user=user, data_type='INCOME').order_by('-upload_date').first()
        
        if latest_processed:
            # Read the data from S3 and convert to HTML
            df = pd.read_excel(latest_processed.file_upload.read())
            final_df_html = df.to_html(classes='table table-striped table-hover', index=False)
            
            # Cache the result
            cache.set(cache_key, final_df_html, 3600)  # Cache for 1 hour
        else:
            return render(request, 'processes/no_data.html', {'message': 'No processed data available. Please process the data first.'})
    
    context = {
        'final_df': final_df_html,
    }
    return render(request, 'processes/display_income.html', context)
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
    
    # Try to get processed data from cache
    final_df_html = cache.get(cache_key)
    
    if not final_df_html:
        # If not in cache, try to get from database
        latest_processed = ProcessedData.objects.filter(user=user, data_type='EXPENSE').order_by('-upload_date').first()
        
        if latest_processed:
            # Read the data from S3 and convert to HTML
            df = pd.read_excel(latest_processed.file_upload.read())
            final_df_html = df.to_html(classes='table table-striped table-hover', index=False)
            
            # Cache the result
            cache.set(cache_key, final_df_html, 3600)  # Cache for 1 hour
        else:
            return render(request, 'processes/no_data.html', {'message': 'No processed data available. Please process the data first.'})
    
    context = {
        'final_df': final_df_html,
    }
    return render(request, 'processes/display_expense.html', context)
@login_required
def process_expense(request):
    user = request.user
    cache_key = f"processed_expense_{user.id}"

    try:
        static_data = get_static_data()
        expense_data = get_expense_processed_data(user)
        
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


