from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from storages.backends.s3boto3 import S3Boto3Storage
import os

class S3Storage(S3Boto3Storage):
    location = 'uploads'
class ProcessedData(models.Model):
    DATA_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=256)
    s3_key = models.CharField(max_length=256)
    upload_date = models.DateTimeField(default=timezone.now)
    data_type = models.CharField(max_length=10, choices=DATA_TYPES)
    file_upload = models.FileField(
        storage=S3Storage(),
        upload_to='processed_folder',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.data_type} - {self.filename}'

    class Meta:
        verbose_name = 'Processed Data'
        verbose_name_plural = 'Processed Data'


class TaskStatus(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETE', 'Complete'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=50)  # e.g., 'INCOME', 'EXPENSE'
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'task_type')
        verbose_name_plural = 'Task Statuses'

    def __str__(self):
        return f"{self.user.username}'s {self.task_type} task - {self.status}"