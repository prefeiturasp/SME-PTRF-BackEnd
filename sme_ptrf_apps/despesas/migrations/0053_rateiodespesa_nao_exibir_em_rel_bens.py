# Generated by Django 4.2.10 on 2024-03-11 08:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("despesas", "0052_auto_20220906_1331"),
    ]

    operations = [
        migrations.AddField(
            model_name="rateiodespesa",
            name="nao_exibir_em_rel_bens",
            field=models.BooleanField(
                default=False, verbose_name="Não exibir na relação de bens"
            ),
        ),
    ]