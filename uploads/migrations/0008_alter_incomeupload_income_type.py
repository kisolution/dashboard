# Generated by Django 5.1 on 2024-08-30 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploads', '0007_alter_incomeupload_income_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomeupload',
            name='income_type',
            field=models.CharField(choices=[('INC_PREV_MONTH', 'Previous Month'), ('INC_DATA_CASE', 'Data Case'), ('INC_MAIN', 'Main'), ('INC_RETENTION', 'Retention'), ('INC_COMISSION', 'Comission')], max_length=20),
        ),
    ]
