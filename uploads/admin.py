from django.contrib import admin
from .models import IncomeUpload, ExpenseUpload

admin.site.register([IncomeUpload, ExpenseUpload])
# Register your models here.
