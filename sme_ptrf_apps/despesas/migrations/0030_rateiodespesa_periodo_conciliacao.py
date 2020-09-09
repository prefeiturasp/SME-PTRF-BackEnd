# Generated by Django 2.2.10 on 2020-08-31 17:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0075_observacaoconciliacao'),
        ('despesas', '0029_rateiodespesa_valor_original'),
    ]

    operations = [
        migrations.AddField(
            model_name='rateiodespesa',
            name='periodo_conciliacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='despesas_conciliadas_no_periodo', to='core.Periodo', verbose_name='período de conciliação'),
        ),
    ]
