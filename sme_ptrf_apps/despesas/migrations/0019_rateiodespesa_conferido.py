# Generated by Django 2.2.10 on 2020-05-07 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('despesas', '0018_fornecedor'),
    ]

    operations = [
        migrations.AddField(
            model_name='rateiodespesa',
            name='conferido',
            field=models.BooleanField(default=False, verbose_name='Conferido?'),
        ),
    ]
