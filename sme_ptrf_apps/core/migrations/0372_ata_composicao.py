# Generated by Django 4.2.7 on 2024-02-08 07:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("mandatos", "0008_alter_cargocomposicao_substituido_and_more"),
        ("core", "0371_alter_dadosdemonstrativofinanceiro_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="ata",
            name="composicao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="atas_da_composicao",
                to="mandatos.composicao",
                verbose_name="Composição utilizada",
            ),
        ),
    ]