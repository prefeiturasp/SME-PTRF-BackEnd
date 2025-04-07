# Generated by Django 4.2.20 on 2025-04-07 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0402_merge_20250324_1256"),
    ]

    operations = [
        migrations.AddField(
            model_name="acaopdde",
            name="previsao_valor_capital",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=20,
                null=True,
                verbose_name="Previsão Valor Capital",
            ),
        ),
        migrations.AddField(
            model_name="acaopdde",
            name="previsao_valor_custeio",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=20,
                null=True,
                verbose_name="Previsão Valor Custeio",
            ),
        ),
        migrations.AddField(
            model_name="acaopdde",
            name="previsao_valor_livre_aplicacao",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=20,
                null=True,
                verbose_name="Previsão Valor Livre Aplicação",
            ),
        ),
        migrations.AddField(
            model_name="acaopdde",
            name="saldo_valor_capital",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=20,
                null=True,
                verbose_name="Saldo Valor Capital",
            ),
        ),
        migrations.AddField(
            model_name="acaopdde",
            name="saldo_valor_custeio",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=20,
                null=True,
                verbose_name="Saldo Valor Custeio",
            ),
        ),
        migrations.AddField(
            model_name="acaopdde",
            name="saldo_valor_livre_aplicacao",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=20,
                null=True,
                verbose_name="Saldo Valor Livre Aplicação",
            ),
        ),
        migrations.AlterField(
            model_name="acaopdde",
            name="categoria",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.categoriapdde",
            ),
        ),
    ]
