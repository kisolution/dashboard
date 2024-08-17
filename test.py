
from uploads.models import ExpenseUpload, IncomeUpload

def see_keys(request): 

    one_file = ExpenseUpload.objects.filter(user = request.user, expense_type = 'MAIN').order_by('-upload_date').first()
    print(one_file.s3_key)