import io
import pandas as pd
from django.core.cache import cache
from django.conf import settings
import boto3
from storages.backends.s3boto3 import S3Boto3Storage
from uploads.models import IncomeUpload, ExpenseUpload
from processes.models import ProcessedData
from polcyprocess.models import PolicyProcessedData
from prediction.models import PredictionData
from policy.models import IncomePolicyUpload
from io import BytesIO
from django.core.cache import cache
import logging
from botocore.exceptions import ClientError
import pickle
s3_storage = S3Boto3Storage()
from django.utils import timezone
from django.core.files.base import ContentFile

file_paths = {
    'commission_data': 'Income/commission_data.xlsx',
    #'retention_data': 'Income/retention_data.xlsx',
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


def load_static_data():
    s3 = get_s3_client()
    logger.info("Loading static data from S3...")
    static_data = {}
    for key, path in file_paths.items():
        obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=path)
        static_data[key] = pd.read_excel(io.BytesIO(obj['Body'].read()))
    logger.info("Static data loaded successfully")
    return static_data

def get_static_data():
    cache_key = "all_static_data"
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        logger.info("Retrieved static data from cache")
        return pickle.loads(cached_data)
    
    logger.info("Cache miss for static data, loading from S3")
    static_data = load_static_data()
    
    # Cache the static_data for 30 days
    cache.set(cache_key, pickle.dumps(static_data), 30 * 24 * 60 * 60)
    
    return static_data

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
    #cache_key = f"{file_type}_{user.id}"
    #cached_data = cache.get(cache_key)
    #
    #if cached_data is not None:
    #    return cached_data
    
    if file_type in [choice[0] for choice in IncomeUpload.INCOME_TYPES]:
        file = IncomeUpload.objects.filter(user=user, income_type=file_type).order_by('-upload_date').first()
    elif file_type in [choice[0] for choice in ExpenseUpload.EXPENSE_TYPES]:
        file = ExpenseUpload.objects.filter(user=user, expense_type=file_type).order_by('-upload_date').first()
    elif file_type in [choice[0] for choice in ProcessedData.DATA_TYPES]:
        file = ProcessedData.objects.filter(user=user, data_type=file_type).order_by('-upload_date').first()
    elif file_type in [choice[0] for choice in IncomePolicyUpload.INCOME_TYPES]:
        file = IncomePolicyUpload.objects.filter(user=user, income_type=file_type).order_by('-upload_date').first()
    elif file_type in [choice[0] for choice in PolicyProcessedData.DATA_TYPES]:
        file = PolicyProcessedData.objects.filter(user=user, data_type=file_type).order_by('-upload_date').first()
    elif file_type in [choice[0] for choice in PredictionData.DATA_TYPES]:
        file = PredictionData.objects.filter(user=user, data_type=file_type).order_by('-upload_date').first()
    else:
        logger.warning(f"Invalid file type: {file_type}")
        return None
    
    if file:
        logger.info(f"Retrieved file for {file_type}: {file.filename}, uploaded at {file.upload_date}")
        df = get_file_from_s3(file.s3_key)
        #if df is not None:
        #    cache.set(cache_key, df, 75600)  # Cache for 1 hour
        return df
    else:
        logger.warning(f"No file found for {file_type}")
    return None

def get_latest_income_data(user):
    income_data = {
        'life_ins_data': get_cached_file_data('INC_LIFE', user),
        'nonlife_ins_data': get_cached_file_data('INC_NON_LIFE', user),
        'prev_month_data': get_cached_file_data('INC_PREV_MONTH', user),
        'main_data': get_cached_file_data('INC_MAIN', user),
        'retention_data':get_cached_file_data('INC_RETENTION', user),
        'commission_data':get_cached_file_data('INC_COMISSION', user),

    }
    
    if any(df is None for df in income_data.values()):
        logger.error("One or more required files are missing or could not be read")
        return None
    
    return income_data

def invalidate_cache(user_id, data_type):
    """Invalidate cache for a specific user and data type."""
    cache_key = f"{data_type}_{user_id}"
    cache.delete(cache_key)

def get_latest_expense_data(user):
    expense_data = {
        'main_df': get_cached_file_data('EXP_MAIN', user),
        'override_df': get_cached_file_data('EXP_OVERRIDE', user),
        'prev_month_df': get_cached_file_data('EXP_PREV_MONTH', user),
        'security_df': get_cached_file_data('EXP_SECURITY', user),
        'retirement_df': get_cached_file_data('EXP_RETIREMENT', user),
        'contract_df': get_cached_file_data('EXP_CONTRACTS', user),
        'commission_df':get_cached_file_data('EXP_COMISSION', user),
        'retention_df':get_cached_file_data('EXP_RETENTION', user)
    }
    
    if any(df is None for df in expense_data.values()):
        logger.error("One or more required expense files are missing or could not be read")
        return None
    
    return expense_data

def get_latest_income_policy_data(user):
    income_policy_data = {
        'inc_p_prev_month': get_cached_file_data('INC_P_PREV_MONTH', user),
        'inc_p_data_case': get_cached_file_data('INC_P_DATA_CASE', user),
        'inc_p_main': get_cached_file_data('INC_P_MAIN', user),
        'inc_p_retention':get_cached_file_data('INC_P_RETENTION', user),
        'inc_p_commission':get_cached_file_data('INC_P_COMISSION', user),}
    if any(df is None for df in income_policy_data.values()):
        logger.error("One or more required files are missing or could not be read")
        return None    
    return income_policy_data

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
def get_policy_processed_data(user):
    processed_data = PolicyProcessedData.objects.filter(user=user, data_type='INCOME_POLICY_PRO').order_by('-upload_date').first()
    if processed_data:
        df = get_cached_file_data('INCOME_POLICY_PRO', user)
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
def save_processed_data(user, df, data_type):
    timestamp = timezone.now()
    filename = f"processed_{data_type.lower()}_data_{timestamp.strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Processed {data_type} Data')
    buffer.seek(0)
    
    processed_data = ProcessedData(
        user=user,
        filename=filename,
        s3_key=f"processed_folder/{filename}",
        data_type=data_type,
        upload_date=timestamp
    )
    
    processed_data.file_upload.save(filename, ContentFile(buffer.getvalue()), save=True)
    print('saved and uploaded as', processed_data.s3_key)
    # Update cache with new data
    cache_key = f"{data_type}_{user.id}"
    cache.set(cache_key, df, 3600)  # Cache for 1 hour

def save_policy_processed_data(user, df, data_type):
    timestamp = timezone.now()
    filename = f"processed_{data_type.lower()}_data_{timestamp.strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Processed Policy {data_type} Data')
    buffer.seek(0)
    
    processed_data = PolicyProcessedData(
        user=user,
        filename=filename,
        s3_key=f"policy_processed_folder/{filename}",
        data_type=data_type,
        upload_date=timestamp
    )
    
    processed_data.file_upload.save(filename, ContentFile(buffer.getvalue()), save=True)
    print('saved and uploaded as', processed_data.s3_key)
    # Update cache with new data
    cache_key = f"{data_type}_{user.id}"
    cache.set(cache_key, df, 3600)  # Cache for 1 hour

def save_predicted_data(user, df, data_type):
    timestamp = timezone.now()
    filename = f"predicted_{data_type.lower()}_data_{timestamp.strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Predicted {data_type} Data')
    buffer.seek(0)
    
    processed_data = PredictionData(
        user=user,
        filename=filename,
        s3_key=f"prediction_folder/{filename}",
        data_type=data_type,
        upload_date=timestamp
    )
    
    processed_data.file_upload.save(filename, ContentFile(buffer.getvalue()), save=True)
    print('saved and uploaded as', processed_data.s3_key)
    # Update cache with new data
    cache_key = f"{data_type}_{user.id}"
    cache.set(cache_key, df, 3600)  # Cache for 1 hour
