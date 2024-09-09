from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from storages.backends.s3boto3 import S3Boto3Storage

class S3Storage(S3Boto3Storage):
    location = 'uploads'
class PolicyProcessedData(models.Model):
    DATA_TYPES = [
        ('INCOME_POLICY_PRO', 'Income'),
        ('EXPENSE_POLICY_PRO', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=256)
    s3_key = models.CharField(max_length=256)
    upload_date = models.DateTimeField(default=timezone.now)
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    file_upload = models.FileField(
        storage=S3Storage(),
        upload_to='policy_processed_folder',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.data_type} - {self.filename}'

    class Meta:
        verbose_name = 'Processed Data'
        verbose_name_plural = 'Processed Data'

