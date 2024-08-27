from celery import shared_task
from django.contrib.auth.models import User
from functions.income_processor import IncomeProcessor
from functions.expense_processor import ExpenseProcessor
from utils.s3_utils import get_static_data, get_latest_income_data, save_processed_data, get_latest_expense_data
import logging
from django.core.exceptions import ObjectDoesNotExist
import traceback

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_income_task(self, user_id):
    logger.info(f"Task started for user_id: {user_id}")
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"User fetched: {user.username}")

        static_data = get_static_data()
        logger.info(f"Static data retrieved")

        income_data = get_latest_income_data(user)
        logger.info(f"Latest income data fetched")

        if income_data is None:
            logger.error("No income data available")
            raise ValueError("No income data available")

        process = IncomeProcessor(static_data, income_data)
        logger.info("IncomeProcessor initialized")

        process.process()
        logger.info("Income data processed")

        final_df = process.get_final_df()
        logger.info(f"Final dataframe obtained. Shape: {final_df.shape}")

        save_processed_data(user, final_df, 'INCOME')
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


logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_expense_task(self, user_id):
    logger.info(f"Task started for user_id: {user_id}")
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"User fetched: {user.username}")

        static_data = get_static_data()
        logger.info(f"Static data retrieved")

        expense_data = get_latest_expense_data(user)
        logger.info(f"Latest income data fetched")

        if expense_data is None:
            logger.error("No income data available")
            raise ValueError("No income data available")

        process = ExpenseProcessor(static_data, expense_data)
        logger.info("Expense initialized")

        process.process()
        logger.info("Expense data processed")

        final_df = process.get_final_df()
        logger.info(f"Final dataframe obtained. Shape: {final_df.shape}")

        save_processed_data(user, final_df, 'EXPENSE')
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