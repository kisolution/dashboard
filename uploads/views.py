from django.shortcuts import render, redirect
from .forms import IncomeUploadForm, ExpenseUploadForm
from .models import IncomeUpload, ExpenseUpload
from functions.sample_datas import sample_data
from django.http import HttpResponse
import pandas as pd
from django.contrib import messages
from utils.s3_utils import invalidate_cache
def home_upload_view(request):
    income_types = dict(IncomeUpload.INCOME_TYPES)
    expense_types = dict(ExpenseUpload.EXPENSE_TYPES) 
    income_type_translations = {
        'INC_PREV_MONTH': '전월데이터',
        'INC_DATA_CASE': '건별데이터',
        'INC_MAIN': '당월데이터',
    }  
    expense_type_translations = {
        'EXP_OVERRIDE': '오버라이드',
        'EXP_RETIREMENT':'퇴사자',
        'EXP_SECURITY':'증권번호별',
        'EXP_PREV_MONTH': '전월데이터',
        'EXP_MAIN': '당월데이터'
    }
    income_forms = {income_type: IncomeUploadForm(prefix=f'income_{income_type}') for income_type in income_types}
    expense_forms = {expense_type: ExpenseUploadForm(prefix=f'expense_{expense_type}') for expense_type in expense_types}
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type.startswith('income_'):
            income_type = form_type.split('_', 1)[1]
            form = IncomeUploadForm(request.POST, request.FILES, prefix=f'income_{income_type}')
            if form.is_valid():
                upload = form.save(commit=False)
                
                if check_uploaded_data(request, income_type, form.cleaned_data['file_upload']):
                    upload.user = request.user
                    upload.income_type = income_type
                    upload.save()
                    
                    # Invalidate cache for this income type
                    invalidate_cache(request.user.id, income_type)
                    
                    messages.success(request, f'{income_type_translations.get(income_type, income_type)} uploaded successfully.')
                    return redirect('home')
                else:
                    messages.error(request, 'File validation failed. Please check the file content and try again.')
            else:
                messages.error(request, 'Form is not valid. Please check your inputs.')
                print(f"Form errors for {form_type}:", form.errors)
        
        elif form_type.startswith('expense_'):
            expense_type = form_type.split('_', 1)[1]
            form = ExpenseUploadForm(request.POST, request.FILES, prefix=f'expense_{expense_type}')
            if form.is_valid():
                upload = form.save(commit=False)
                
                if check_uploaded_data(request, expense_type, form.cleaned_data['file_upload']):
                    upload.user = request.user
                    upload.expense_type = expense_type
                    upload.save()
                    
                    # Invalidate cache for this expense type
                    invalidate_cache(request.user.id, expense_type)
                    
                    messages.success(request, f'{expense_type_translations.get(expense_type, expense_type)} uploaded successfully.')
                    return redirect('home')
                else:
                    messages.error(request, 'File validation failed. Please check the file content and try again.')
            else:
                messages.error(request, 'Form is not valid. Please check your inputs.')
                print(f"Form errors for {form_type}:", form.errors)
    
    context = {
        'income_forms': income_forms,
        'expense_forms': expense_forms,
        'income_type_translations': income_type_translations,
        'expense_type_translations': expense_type_translations
    }
    return render(request, 'uploads/home_upload.html', context)
def download_sample(request, upload_type):
    upload_type = upload_type.lower()
    sample_name = f"{upload_type}"
    try:
        df = sample_data(sample_name)
        if df is None:
            return HttpResponse(f"No sample data available for {sample_name}", status=404)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={sample_name}_sample.xlsx'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sample')
        return response
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)
    
def check_uploaded_data(request, file_type, uploaded_file):
    try:
        df = pd.read_excel(uploaded_file, nrows=5)
    except Exception as e:
        messages.error(request, f"Error reading the uploaded file: {str(e)}")
        return False
    file_type = str.lower(file_type)
    col_len = len(df.columns)
    sample_df = sample_data(file_type)

    if sample_df is None:
        messages.error(request, f"Unknown file type: {file_type}")
        return False

    expected_col_len = len(sample_df.columns)
    expected_columns = sample_df.columns.tolist()

    if col_len != expected_col_len:
        messages.warning(request, f"The columns of {file_type} data should be total of {expected_col_len}, but got {col_len}")
        return False

    if not df.columns.equals(sample_df.columns):
        mismatched_columns = set(df.columns).symmetric_difference(set(expected_columns))
        messages.warning(request, f"The data you have uploaded has mismatched columns. Mismatched columns: {', '.join(mismatched_columns)}")
        return False

    # Additional checks can be added here, such as data type validation, range checks, etc.

    return True