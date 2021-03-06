# Generated by Django 2.0.4 on 2018-04-27 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_multiinfo', '0003_auto_20180427_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smsmessageinfo',
            name='message_status',
            field=models.PositiveSmallIntegerField(choices=[('0', 'Wiadomość przyjęta do przetwarzania'), ('1', 'Wiadomość w trakcie przetwarzania'), ('11', 'Błąd fatalny, wysyłanie nieudane'), ('12', 'Wiadomość przedawniona'), ('13', 'Wiadomość usunięta'), ('21', 'Wiadomość przesłana pomyślnie'), ('3', 'Wiadomość przekazana do SMSC, oczekiwanie potwierdzenie doręczenia wiadomości'), ('7', 'Wiadomość wstrzymana z powodu przekroczenia limitu')]),
        ),
    ]
