# Generated by Django 2.2.10 on 2023-01-20 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0303_merge_20230119_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='prestacaoconta',
            name='status_anterior_a_retificacao',
            field=models.CharField(blank=True, default=None, max_length=20, null=True, verbose_name='Status anterior a retificacao'),
        ),
    ]
