# Generated by Django 4.0.2 on 2022-03-09 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_refund_phone_number_report'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='report',
            name='last_name',
        ),
        migrations.AddField(
            model_name='report',
            name='full_name',
            field=models.CharField(default='noname', max_length=200),
        ),
    ]