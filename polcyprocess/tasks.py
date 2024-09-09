import logging
from django.core.exceptions import ObjectDoesNotExist
import traceback
from celery import shared_task
from functions.policy_processor import PolicyProcessor
from utils.s3_utils import get_latest_income_policy_data, save_policy_processed_data
from .models import PolicyProcessedData
from django.contrib.auth.models import User
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def policy_process_income_task(self, user_id):
    logger.info(f"Task started for user_id: {user_id}")
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"User fetched: {user.username}")

        
        policy_income_data = get_latest_income_policy_data(user)
        logger.info(f"Latest income data fetched")

        if policy_income_data is None:
            logger.error("No income data available")
            raise ValueError("No income data available")

        process = PolicyProcessor(policy_income_data)
        logger.info("IncomeProcessor initialized")

        process.process_start()
        logger.info("Income data processed")

        final_df = process.get_final_df()
        logger.info(f"Final dataframe obtained. Shape: {final_df.shape}")

        save_policy_processed_data(user, final_df, 'INCOME_POLICY_PRO')
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
