from django.shortcuts import render
from processes.models import ProcessedData
from utils.s3_utils import get_cached_file_data, get_file_from_s3

def income_prediction(request):
    user = request.user
    main_data = get_cached_file_data('INCOME', user)
    if main_data is None:
        return render(request, 'uploads/error_template.html', {'message': 'No data available'})
    retention_data= get_cached_file_data('INC_RETENTION', user)
    commission_data = get_cached_file_data('INC_COMISSION', user)
    