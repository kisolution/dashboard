from django.shortcuts import render
from utils.s3_utils import get_policy_processed_data, get_cached_file_data
from functions.policy_processor import PolicyProcessor
from policy.models import IncomePolicyUpload 
from .tasks import policy_process_income_task
from functions.lower_cols import to_lower
from functions.others import policy_income_report
from io import BytesIO
import pandas as pd
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
@login_required
def initiate_policy_process(request):
    policy_process_income_task.delay(request.user.id)
    return render(request, 'policyprocess/policy_process_started.html')
@login_required
def display_policy_income(request):
    user = request.user
    df = get_policy_processed_data(user)
    if df is None:
        error = 'No Data Found for Processing'
        return render(request, 'uploads/error_template.html', {'error':error})
    company_names = df['보험사'].unique()
    selected_company = request.GET.get('company')
    if selected_company and selected_company != '':
        df_filtered = df[df['보험사']==selected_company]
    else: 
        df_filtered = df
        selected_company = 'All'
    prev_month_df = get_cached_file_data('INC_P_PREV_MONTH', user)
    if prev_month_df is not None and not prev_month_df.empty:
        prev_month_df = to_lower(prev_month_df)
        if selected_company and selected_company !='All':
            c_32 = prev_month_df[prev_month_df['보험사']==selected_company]['기말선수수익'].sum()
            c_33 = prev_month_df[prev_month_df['보험사']==selected_company]['기말선급비용'].sum()
            c_34 = prev_month_df[prev_month_df['보험사']==selected_company]['기말환수부채'].sum()
            c_35 = prev_month_df[prev_month_df['보험사']==selected_company]['기말환수자산'].sum()
        else:
            c_32 = prev_month_df['기말선수수익'].sum()
            c_33 = prev_month_df['기말선급비용'].sum()
            c_34 = prev_month_df['기말환수부채'].sum()
            c_35 = prev_month_df['기말환수자산'].sum()
    else:
        c_32 = c_33 = c_34 = c_35 = 0
    
    report_data = policy_income_report(df_filtered, c_32, c_33, c_34, c_35)
    if request.GET.get('download'):
        output = BytesIO()
        with pd.ExcelWriter(output, engine = 'openpyxl') as writer:
            df_filtered.to_excel(writer, index = False, sheet_name = 'Policy Processed')
        output.seek(0)
        response = HttpResponse(output.read(), content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = 'policy_data.xlsx'
        response['Content-Disposition'] = f'attachment; filename = "{filename}"'
        return response
    context = {'report_data': report_data,
               'company_names':company_names,
               'selected_company':selected_company if selected_company != 'All' else ''}
    return render(request, 'policyprocess/processed_policy.html', context = context)