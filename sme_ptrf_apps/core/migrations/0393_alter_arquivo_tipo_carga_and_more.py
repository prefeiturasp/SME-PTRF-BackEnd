# Generated by Django 4.2.7 on 2024-05-15 11:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0392_alter_arquivo_tipo_carga_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="arquivo",
            name="tipo_carga",
            field=models.CharField(
                choices=[
                    ("REPASSE_REALIZADO", "Repasses realizados"),
                    ("CARGA_PERIODO_INICIAL", "Carga período inicial"),
                    ("REPASSE_PREVISTO", "Repasses previstos"),
                    ("CARGA_ASSOCIACOES", "Carga de Associações"),
                    ("CARGA_USUARIOS", "Carga de usuários"),
                    ("CARGA_CENSO", "Carga de censo"),
                    ("CARGA_REPASSE_PREVISTO_SME", "Repasses previstos sme"),
                    ("CARGA_DEVOLUCAO_TESOURO", "Devoluções ao Tesouro"),
                    (
                        "CARGA_MATERIAIS_SERVICOS",
                        "Especificações de Materiais e Serviços",
                    ),
                ],
                default="REPASSE_REALIZADO",
                max_length=35,
                verbose_name="tipo de carga",
            ),
        ),
        migrations.AlterField(
            model_name="modelocarga",
            name="tipo_carga",
            field=models.CharField(
                choices=[
                    ("REPASSE_REALIZADO", "Repasses realizados"),
                    ("CARGA_PERIODO_INICIAL", "Carga período inicial"),
                    ("REPASSE_PREVISTO", "Repasses previstos"),
                    ("CARGA_ASSOCIACOES", "Carga de Associações"),
                    ("CARGA_USUARIOS", "Carga de usuários"),
                    ("CARGA_CENSO", "Carga de censo"),
                    ("CARGA_REPASSE_PREVISTO_SME", "Repasses previstos sme"),
                    ("CARGA_DEVOLUCAO_TESOURO", "Devoluções ao Tesouro"),
                    (
                        "CARGA_MATERIAIS_SERVICOS",
                        "Especificações de Materiais e Serviços",
                    ),
                ],
                default="CARGA_ASSOCIACOES",
                max_length=35,
                unique=True,
                verbose_name="tipo de carga",
            ),
        ),
    ]
