from celery import shared_task
from django.contrib.auth.models import User
from .models import ProcessedData, TaskStatus
from functions.income_processor import IncomeProcessor
from functions.expense_processor import ExpenseProcessor
from utils.s3_utils import get_static_data, get_latest_income_data, get_latest_expense_data, save_processed_data
from django.core.files.base import ContentFile
from django.utils import timezone
from io import BytesIO
import pandas as pd
from django.shortcuts import render, redirect
@shared_task(schedule=60)
def process_income_task(user_id):
    user = User.objects.get(id=user_id)
    task_status, _ = TaskStatus.objects.get_or_create(user=user, task_type='INCOME')
    task_status.status = 'PROCESSING'
    task_status.save()

    try:
        static_data = get_static_data()
        income_data = get_latest_income_data(user)
        
        if income_data is None:
            raise ValueError("No income data available")

        process = IncomeProcessor(static_data, income_data)
        process.process()
        final_df = process.get_final_df()
        
        save_processed_data(user, final_df, 'INCOME')

        task_status.status = 'COMPLETE'
        task_status.completed_at = timezone.now()
        task_status.save()
    except Exception as e:
        task_status.status = 'FAILED'
        task_status.save()
        raise e

@shared_task(schedule=60)
def process_expense_task(user_id):
    user = User.objects.get(id=user_id)
    task_status, _ = TaskStatus.objects.get_or_create(user=user, task_type='EXPENSE')
    task_status.status = 'PROCESSING'
    task_status.save()

    try:
        static_data = get_static_data()
        expense_data = get_latest_expense_data(user)
        
        if expense_data is None:
            raise ValueError("No expense data available")

        process = ExpenseProcessor(static_data, expense_data)
        process.process()
        final_df = process.get_final_df()
        
        save_processed_data(user, final_df, 'EXPENSE')

        task_status.status = 'COMPLETE'
        task_status.completed_at = timezone.now()
        task_status.save()
    except Exception as e:
        task_status.status = 'FAILED'
        task_status.save()
        raise e