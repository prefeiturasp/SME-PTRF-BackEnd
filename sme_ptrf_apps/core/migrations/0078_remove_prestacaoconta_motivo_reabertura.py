# Generated by Django 2.2.10 on 2020-09-02 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0077_auto_20200902_0757'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prestacaoconta',
            name='motivo_reabertura',
        ),
    ]
