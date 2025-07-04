# Generated by Django 4.2.20 on 2025-05-20 14:51

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0408_alter_categoriapdde_unique_together_and_more"),
        ("paa", "0003_paa"),
    ]

    operations = [
        migrations.CreateModel(
            name="FonteRecursoPaa",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=160, verbose_name="Nome")),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "alterado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Alterado em"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
            ],
            options={
                "verbose_name": "Fonte Recursos PAA",
                "verbose_name_plural": "Fonte Recursos PAA",
            },
        ),
        migrations.CreateModel(
            name="RecursoProprioPaa",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "alterado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Alterado em"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("data_prevista", models.DateField(default=datetime.date.today)),
                ("descricao", models.CharField(max_length=255)),
                (
                    "valor",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=20, verbose_name="Valor"
                    ),
                ),
                (
                    "associacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="associacao",
                        to="core.associacao",
                    ),
                ),
                (
                    "fonte_recurso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="recurso_proprio",
                        to="paa.fonterecursopaa",
                    ),
                ),
                (
                    "paa",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="paa.paa",
                        verbose_name="PAA",
                    ),
                ),
            ],
            options={
                "verbose_name": "Recurso Próprio do PAA",
                "verbose_name_plural": "Recursos Próprios do PAA",
            },
        ),
        migrations.CreateModel(
            name="ReceitaPrevistaPaa",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "alterado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Alterado em"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "previsao_valor_custeio",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=20,
                        verbose_name="Previsão Valor Custeio",
                    ),
                ),
                (
                    "previsao_valor_capital",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=20,
                        verbose_name="Previsão Valor Capital",
                    ),
                ),
                (
                    "previsao_valor_livre",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=20,
                        verbose_name="Previsão Valor Livre Aplicação",
                    ),
                ),
                (
                    "acao_associacao",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="core.acaoassociacao",
                        verbose_name="Ação de Associação",
                    ),
                ),
                (
                    "paa",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="paa.paa",
                        verbose_name="PAA",
                    ),
                ),
            ],
            options={
                "verbose_name": "Receita Prevista do PAA",
                "verbose_name_plural": "Receitas Previstas do PAA",
            },
        ),
        migrations.CreateModel(
            name="ProgramaPdde",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=160, verbose_name="Nome")),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "alterado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Alterado em"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
            ],
            options={
                "verbose_name": "Programa PDDE",
                "verbose_name_plural": "Programas PDDE",
                "unique_together": {("nome",)},
            },
        ),
        migrations.CreateModel(
            name="AcaoPdde",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=160, verbose_name="Nome")),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "alterado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Alterado em"),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                (
                    "aceita_capital",
                    models.BooleanField(default=False, verbose_name="Aceita capital?"),
                ),
                (
                    "aceita_custeio",
                    models.BooleanField(default=False, verbose_name="Aceita custeio?"),
                ),
                (
                    "aceita_livre_aplicacao",
                    models.BooleanField(
                        default=False, verbose_name="Aceita livre aplicação?"
                    ),
                ),
                (
                    "programa",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="paa.programapdde",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ação PDDE",
                "verbose_name_plural": "Ações PDDE",
                "unique_together": {("nome", "programa")},
            },
        ),
    ]
