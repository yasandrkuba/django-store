# Generated by Django 4.0.2 on 2022-03-10 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_remove_report_first_name_remove_report_last_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='ref_code',
            field=models.CharField(default=1242342121, max_length=10),
        ),
    ]