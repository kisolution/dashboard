# Generated by Django 5.1 on 2024-08-16 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploads', '0004_alter_expenseupload_file_upload_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenseupload',
            name='expense_type',
            field=models.CharField(choices=[('PREV_MONTH', 'Previous Month'), ('OVERRIDE', 'Override'), ('SECURITY', 'Security'), ('RETIREMENT', 'Retirement'), ('MAIN', 'Main')], max_length=20),
        ),
    ]
