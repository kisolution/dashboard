from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from storages.backends.s3boto3 import S3Boto3Storage
import os

class S3Storage(S3Boto3Storage):
    location = 'uploads'

class IncomeUpload(models.Model):
    INCOME_TYPES = [
        ('INC_PREV_MONTH', 'Previous Month'),
        ('INC_DATA_CASE', 'Data Case'),
        ('INC_MAIN', 'Main'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    income_type = models.CharField(max_length=20, choices=INCOME_TYPES)
    file_upload = models.FileField(storage=S3Storage(), upload_to='income_folder')
    filename = models.CharField(max_length=255)
    s3_key = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file_upload:
            # Get the original filename and extension
            original_filename = self.file_upload.name
            filename, file_extension = os.path.splitext(original_filename)
            
            # Generate timestamp
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            
            # Create new filename with timestamp
            new_filename = f"{filename}_{timestamp}{file_extension}"
            
            # Update the filename and S3 key
            self.filename = new_filename
            self.s3_key = f"income_folder/{new_filename}"
            
            # Rename the file
            self.file_upload.name = new_filename
            
            print(f"Saving file: {self.filename} with S3 key: {self.s3_key}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.income_type} - {self.filename}"
    
    
class ExpenseUpload(models.Model):
    EXPENSE_TYPES = [
        ('EXP_PREV_MONTH', 'Previous Month'),
        ('EXP_OVERRIDE', 'Override'),
        ('EXP_SECURITY', 'Security'),
        ('EXP_RETIREMENT', 'Retirement'),
        ('EXP_MAIN', 'Main'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    file_upload = models.FileField(storage=S3Storage(), upload_to='expense_folder')
    filename = models.CharField(max_length=255)
    s3_key = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file_upload:
            # Get the original filename and extension
            original_filename = self.file_upload.name
            filename, file_extension = os.path.splitext(original_filename)
            
            # Generate timestamp
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            
            # Create new filename with timestamp
            new_filename = f"{filename}_{timestamp}{file_extension}"
            
            # Update the filename and S3 key
            self.filename = new_filename
            self.s3_key = f"expense_folder/{new_filename}"
            
            # Rename the file
            self.file_upload.name = new_filename
            
            print(f"Saving file: {self.filename} with S3 key: {self.s3_key}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.expense_type} - {self.filename}"

