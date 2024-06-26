# Generated by Django 4.2.11 on 2024-05-20 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("despesas", "0053_rateiodespesa_nao_exibir_em_rel_bens"),
    ]

    operations = [
        migrations.AddField(
            model_name="despesa",
            name="despesa_anterior_ao_uso_do_sistema",
            field=models.BooleanField(
                default=False, verbose_name="É despesa anterior ao uso do sistema?"
            ),
        ),
        migrations.AddField(
            model_name="despesa",
            name="despesa_anterior_ao_uso_do_sistema_pc_concluida",
            field=models.BooleanField(
                default=False,
                verbose_name="Essa Despesa anterior ao uso do sistema já teve alguma PC concluída?",
            ),
        ),
    ]
