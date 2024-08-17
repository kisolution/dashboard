import io
import pandas as pd
from django.core.cache import cache
from django.conf import settings
import boto3
from storages.backends.s3boto3 import S3Boto3Storage
from uploads.models import IncomeUpload, ExpenseUpload
from processes.models import ProcessedData
from io import BytesIO
from django.core.cache import cache
import logging
from botocore.exceptions import ClientError
s3_storage = S3Boto3Storage()

file_paths = {
    'commission_data': 'Income/commission_data.xlsx',
    'retention_data': 'Income/retention_data.xlsx',
    'prev_month_data': 'Income/prev_month_data.xlsx',
    'commission_df': 'Payment/commission_df.xlsx',
    'retention_df': 'Payment/retention_df.xlsx',
    'prev_month_df': 'Payment/m_5.xlsx'
}

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        #region_name=settings.AWS_S3_REGION_NAME
    )

#@cache.cache_page(60 * 60)  # Cache for 1 hour
def load_static_data():
    s3 = get_s3_client()
    print("Loading static data...")
    static_data = {}
    for key, path in file_paths.items():
        obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=path)
        static_data[key] = pd.read_excel(io.BytesIO(obj['Body'].read()))
    print("Static data loaded successfully")
    return static_data

def get_static_data():
    return load_static_data()

def create_excel_file(df, filename):
    """Helper function to create an Excel file from a DataFrame"""
    output = io.BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return output, filename


logger = logging.getLogger(__name__)

def get_file_from_s3(s3_key):
    if not s3_key:
        logger.error("Empty S3 key provided")
        return None

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    try:
        # Prepend the 'uploads/' folder to the s3_key
        full_s3_key = f"uploads/{s3_key}"
        response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=full_s3_key)
        logger.info(f"Successfully retrieved object from S3. Content type: {response['ContentType']}")
        data = response['Body'].read()
        df = pd.read_excel(BytesIO(data), engine='openpyxl')
        return df
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.error(f"The specified key does not exist in S3: {full_s3_key}")
        else:
            logger.error(f"An error occurred while accessing S3: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Failed to read from S3 (Key: {full_s3_key}): {str(e)}")
        return None

def get_cached_file_data(file_type, user):
    cache_key = f"{file_type}_{user.id}"
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return cached_data
    
    if file_type in [choice[0] for choice in IncomeUpload.INCOME_TYPES]:
        file = IncomeUpload.objects.filter(user=user, income_type=file_type).order_by('-upload_date').first()
    elif file_type in [choice[0] for choice in ExpenseUpload.EXPENSE_TYPES]:
        file = ExpenseUpload.objects.filter(user=user, expense_type=file_type).order_by('-upload_date').first()
    elif file_type in [choice[0] for choice in ProcessedData.DATA_TYPES]:
        file = ProcessedData.objects.filter(user=user, data_type=file_type).order_by('-upload_date').first()
    else:
        logger.warning(f"Invalid file type: {file_type}")
        return None
    
    if file:
        logger.info(f"Retrieved file for {file_type}: {file.filename}, uploaded at {file.upload_date}")
        df = get_file_from_s3(file.s3_key)
        if df is not None:
            cache.set(cache_key, df, 3600)  # Cache for 1 hour
        return df
    else:
        logger.warning(f"No file found for {file_type}")
    return None

def get_latest_income_data(user):
    income_data = {
        'case_data': get_cached_file_data('INC_DATA_CASE', user),
        'prev_month_data': get_cached_file_data('INC_PREV_MONTH', user),
        'main_data': get_cached_file_data('INC_MAIN', user),
    }
    
    if any(df is None for df in income_data.values()):
        logger.error("One or more required files are missing or could not be read")
        return None
    
    return income_data

def get_latest_expense_data(user):
    expense_data = {
        'main_df': get_cached_file_data('EXP_MAIN', user),
        'override_df': get_cached_file_data('EXP_OVERRIDE', user),
        'prev_month_df': get_cached_file_data('EXP_PREV_MONTH', user),
        'security_df': get_cached_file_data('EXP_SECURITY', user),
        'retirement_df': get_cached_file_data('EXP_RETIREMENT', user),
    }
    
    if any(df is None for df in expense_data.values()):
        logger.error("One or more required expense files are missing or could not be read")
        return None
    
    return expense_data


def get_income_processed_data(user):
    processed_data = ProcessedData.objects.filter(user=user, data_type='INCOME').order_by('-upload_date').first()
    if processed_data:
        df = get_cached_file_data('INCOME', user)
        return df
    return None

def get_expense_processed_data(user):
    processed_data = ProcessedData.objects.filter(user=user, data_type='EXPENSE').order_by('-upload_date').first()
    if processed_data:
        df = get_cached_file_data('EXPENSE', user)
        return df
    return None


def upload_to_s3(file_obj, s3_key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    s3.upload_fileobj(file_obj, settings.AWS_STORAGE_BUCKET_NAME, s3_key)
    
    s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    return s3_url