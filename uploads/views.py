from django.shortcuts import render, redirect
from .forms import IncomeUploadForm, ExpenseUploadForm
from .models import IncomeUpload, ExpenseUpload
from functions.sample_datas import sample_data
from django.http import HttpResponse
import pandas as pd
import re


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
            form = IncomeUploadForm(request.POST, request.FILES, prefix=form_type)
            if form.is_valid():
                upload = form.save(commit=False)
                upload.user = request.user
                upload.income_type = income_type
                upload.save()
                return redirect('home')  # Redirect to clear the form
        elif form_type.startswith('expense_'):
            expense_type = form_type.split('_', 1)[1]
            form = ExpenseUploadForm(request.POST, request.FILES, prefix=form_type)
            if form.is_valid():
                upload = form.save(commit=False)
                upload.user = request.user
                upload.expense_type = expense_type
                upload.save()
                return redirect('home')  # Redirect to clear the form
    
    context = {
        'income_forms': income_forms,
        'expense_forms': expense_forms,
        'income_type_translations': income_type_translations,
        'expense_type_translations':expense_type_translations
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