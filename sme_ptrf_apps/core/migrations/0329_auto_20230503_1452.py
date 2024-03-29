# Generated by Django 2.2.10 on 2023-05-03 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0328_auto_20230426_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='associacao',
            name='periodo_inicial',
            field=models.ForeignKey(blank=True, help_text='O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='associacoes_iniciadas_no_periodo', to='core.Periodo', verbose_name='período inicial'),
        ),
    ]
