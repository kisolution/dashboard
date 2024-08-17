def income_process(request):
    try:
        static_data = get_static_data()
        income_data = get_latest_income_data(request.user)
        #income_processed_data = get_income_processed_data(request.user)
        #expense_processed_data = get_expense_processed_data(request.user)
        
        if income_data is None:
            logger.error("No income data available or error reading from S3")
            return render(request, 'uploads/error_template.html', {'error': 'No income data available or error reading from S3'})
        
        process = IncomeProcessor(static_data, income_data)
        process.process()
        final_df = process.get_final_df()
        
        
        if  request.GET.get('download'):
            # Generate a unique filename
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            filename = f"processed_income_data_{timestamp}.xlsx"
            
            # Define S3 key
            s3_key = f"processed_folder/{filename}"
            
            # Save to BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Processed Income Data')
            buffer.seek(0)
            
            # Create ProcessedData instance
            processed_data = ProcessedData(
                user=request.user,
                filename=filename,
                s3_key=s3_key,
                data_type='INCOME'
            )
            
            # Save file to S3 and update ProcessedData
            processed_data.file_upload.save(filename, ContentFile(buffer.getvalue()), save=False)
            processed_data.save()
            response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=processed_income_data.xlsx'
            return response
        
        context = {
            'final_df': final_df.to_html(classes='table table-striped table-hover', index=False),
            #'processed_income':income_processed_data.to_html(classes='table table-striped table-hover', index=False),
            #'processed_expense':expense_processed_data.to_html(classes='table table-striped table-hover', index=False),
        }
        return render(request, 'processes/processed_income.html', context)
    except Exception as e:
        logger.exception(f"Error in income_process view: {e}")
        return HttpResponse(f"An error occurred while processing the data: {str(e)}", status=500)
    





def expense_process(request):

    try:
        static_data = get_static_data()
        expense_data = get_latest_expense_data(request.user)
        
        if expense_data is None:
            logger.error("No expense data available or error reading from S3")
            return render(request, 'uploads/error_template.html', {'error': 'No expense data available or error reading from S3'})
        
        # Assuming you have an ExpenseProcessor similar to MainProcessor
        process = ExpenseProcessor(static_data, expense_data)
        process.process()
        final_df = process.get_final_df()

        if request.GET.get('download'):
        # Generate a unique filename
            filename = f"processed_expense_data_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Save to BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Processed EXPENSE Data')
            buffer.seek(0)
            
            # Create ProcessedData instance
            processed_data = ProcessedData(
                user=request.user,
                filename=filename,
                data_type='EXPENSE'
            )
            
            # Save file to S3 and update ProcessedData
            processed_data.file_upload.save(filename, ContentFile(buffer.getvalue()), save=True)
            response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=processed_expense_data.xlsx'
            return response

        context = {
            'final_df': final_df.to_html()
        }
        
        return render(request, 'processes/processed_expense.html', context)
    except Exception as e:
        logger.exception(f"Error in expense_process view: {e}")
        return HttpResponse(f"An error occurred while processing the data: {str(e)}", status=500)
