# Generated by Django 2.0.4 on 2018-04-05 18:14

from django.db import migrations, models
import django_multiinfo.models


class Migration(migrations.Migration):

    dependencies = [
        ('django_multiinfo', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='smsmessage',
            old_name='posted',
            new_name='ts',
        ),
        migrations.AlterField(
            model_name='smsmessage',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Created'), (1, 'Posted'), (2, 'Busy')], default=django_multiinfo.models.SmsStatus(0)),
        ),
    ]