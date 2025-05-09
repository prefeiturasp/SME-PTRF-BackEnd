# Generated by Django 4.2.11 on 2025-03-10 11:24

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0396_parametros_texto_pagina_paa_ue_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CategoriaPdde",
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
                "verbose_name": "Categoria PDDE",
                "verbose_name_plural": "20.1) Categoria PDDE",
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
                    "categoria",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="core.categoriapdde",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ação PDDE",
                "verbose_name_plural": "20.0) Ações PDDE",
                "unique_together": {("nome", "categoria")},
            },
        ),
    ]