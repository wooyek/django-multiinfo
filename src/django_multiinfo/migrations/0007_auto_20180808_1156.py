# Generated by Django 2.0.7 on 2018-08-08 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_multiinfo', '0006_auto_20180504_1015'),
    ]

    operations = [
        migrations.AddField(
            model_name='smsmessage',
            name='key',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterIndexTogether(
            name='smsmessage',
            index_together={('to', 'key')},
        ),
    ]
