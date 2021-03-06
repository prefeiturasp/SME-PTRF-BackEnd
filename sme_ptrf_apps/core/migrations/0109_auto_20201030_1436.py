# Generated by Django 2.2.10 on 2020-10-30 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0108_merge_20201030_0920'),
    ]

    operations = [
        migrations.AddField(
            model_name='previsaorepassesme',
            name='conta_associacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='previsoes_de_repasse_sme_para_a_conta', to='core.ContaAssociacao'),
        ),
        migrations.AddField(
            model_name='previsaorepassesme',
            name='valor_capital',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Valor Capital'),
        ),
        migrations.AddField(
            model_name='previsaorepassesme',
            name='valor_custeio',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Valor Custeio'),
        ),
        migrations.AddField(
            model_name='previsaorepassesme',
            name='valor_livre',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Valor Livre Aplicação'),
        ),
        migrations.AlterUniqueTogether(
            name='previsaorepassesme',
            unique_together={('associacao', 'periodo', 'conta_associacao')},
        ),
        migrations.RemoveField(
            model_name='previsaorepassesme',
            name='valor',
        ),
    ]
