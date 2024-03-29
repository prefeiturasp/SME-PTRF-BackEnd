# Generated by Django 3.0.14 on 2023-06-20 12:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0334_auto_20230611_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='comentarioanaliseprestacao',
            name='associacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='comentarios_de_analise_da_associacao', to='core.Associacao'),
        ),
        migrations.AddField(
            model_name='comentarioanaliseprestacao',
            name='periodo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='comentarios_de_analise_do_periodo', to='core.Periodo'),
        ),
        migrations.AlterField(
            model_name='comentarioanaliseprestacao',
            name='prestacao_conta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comentarios_de_analise_da_prestacao', to='core.PrestacaoConta'),
        ),
    ]
