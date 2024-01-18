# Generated by Django 4.2.7 on 2024-01-11 08:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("sme", "0002_parametrossme_valida_unidades_login"),
    ]

    operations = [
        migrations.CreateModel(
            name="TipoUnidadeAdministrativa",
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
                    "tipo_unidade_administrativa",
                    models.PositiveIntegerField(
                        verbose_name="Tipo unidade administrativa"
                    ),
                ),
                (
                    "inicio_codigo_eol",
                    models.CharField(
                        blank=True,
                        help_text="Deixe vazio para considerar qualquer código eol",
                        max_length=6,
                        verbose_name="Inicio do código eol que deve ser validado",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tipo unidade administrativa",
                "verbose_name_plural": "02.0) Tipos unidades administrativas",
                "unique_together": {("tipo_unidade_administrativa",)},
            },
        ),
    ]
