# Generated by Django 4.2.11 on 2025-02-27 05:55

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0395_arquivo_tipo_de_conta"),
    ]

    operations = [
        migrations.AddField(
            model_name="parametros",
            name="texto_pagina_paa_ue",
            field=ckeditor.fields.RichTextField(
                null=True, verbose_name="Texto da página de PAA (UE)"
            ),
        ),
        migrations.AlterField(
            model_name="arquivo",
            name="tipo_carga",
            field=models.CharField(
                choices=[
                    ("REPASSE_REALIZADO", "Repasses realizados"),
                    ("CARGA_PERIODO_INICIAL", "Carga período inicial"),
                    ("REPASSE_PREVISTO", "Repasses previstos"),
                    ("CARGA_ASSOCIACOES", "Carga de Associações"),
                    ("CARGA_CONTAS_ASSOCIACOES", "Carga de Contas de Associações"),
                    ("CARGA_ACOES_ASSOCIACOES", "Carga acões de Associações"),
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
            model_name="contaassociacao",
            name="associacao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="contas",
                to="core.associacao",
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
                    ("CARGA_CONTAS_ASSOCIACOES", "Carga de Contas de Associações"),
                    ("CARGA_ACOES_ASSOCIACOES", "Carga acões de Associações"),
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
