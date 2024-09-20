from celery import shared_task
from functions.income_prediction import PredictIncome
from functions.expense_prediction import PredictExpense
from utils.s3_utils import get_cached_file_data, save_predicted_data 
from django.contrib.auth.models import User
import logging
from django.core.exceptions import ObjectDoesNotExist
import traceback
from functions.policy_processor import PolicyProcessor


logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def predict_income_task(self, user_id):
    logger.info(f"Task started for user_id: {user_id}")
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"User fetched: {user.username}")
        main_data = get_cached_file_data('INCOME', user)
        retention_data= get_cached_file_data('INC_RETENTION', user)
        commission_data = get_cached_file_data('INC_COMISSION', user)
        logger.info(f"Latest income data fetched")
        
        income_data_predict = {'main_df':main_data, 
                           'comission_df':commission_data, 
                           'retention_df':retention_data}
        if main_data is None:
            logger.error("No income data available")
            raise ValueError("No income data available")

        process = PredictIncome(income_data_predict)
        logger.info("IncomeProcessor initialized")

        process.process()
        logger.info("Income data processed")

        final_df = process.get_data()
        logger.info(f"Final dataframe obtained. Shape: {final_df.shape}")

        logger.info("Processed data saved successfully")
        save_predicted_data(user, final_df, 'INCOME_PRE')
        logger.info("Processed data saved successfully")

    except ObjectDoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        self.retry(exc=e, countdown=60)  # Retry after 60 seconds

    logger.info(f"Task completed for user_id: {user_id}")
    return "Income processing completed successfully"


@shared_task(bind=True, max_retries=3)
def predict_expense_task(self, user_id):
    logger.info(f"Expense Task started for user_id: {user_id}")
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"User fetched: {user.username}")
        main_data = get_cached_file_data('EXPENSE', user)
        retention_data= get_cached_file_data('EXP_RETENTION', user)
        commission_data = get_cached_file_data('EXP_COMISSION', user)
        logger.info(f"Latest expense data fetched")
        
        expense_data_predict = {'main_df':main_data, 
                           'comission_df':commission_data, 
                           'retention_df':retention_data}
        if main_data is None:
            logger.error("No expense data available")
            raise ValueError("No expene data available")

        process = PredictExpense(expense_data_predict)
        logger.info("ExpenseProcessor initialized")

        process.process()
        logger.info("Expense data processed")

        final_df = process.get_data()
        logger.info(f"Final dataframe obtained. Shape: {final_df.shape}")

        logger.info("Processed data saved successfully")
        save_predicted_data(user, final_df, 'EXPENSE_PRE')
        logger.info("Processed data saved successfully")

    except ObjectDoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        self.retry(exc=e, countdown=60)  # Retry after 60 seconds

    logger.info(f"Task completed for user_id: {user_id}")
    return "Expense processing completed successfully"