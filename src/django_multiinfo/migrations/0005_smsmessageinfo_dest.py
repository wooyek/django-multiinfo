# Generated by Django 2.0.4 on 2018-04-27 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_multiinfo', '0004_auto_20180427_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='smsmessageinfo',
            name='dest',
            field=models.CharField(default='A', max_length=15),
            preserve_default=False,
        ),
    ]
