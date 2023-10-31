# Generated by Django 4.1.12 on 2023-10-27 15:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0356_transferenciaeol_periodo_inicial_associacao"),
        ("users", "0023_auto_20230612_1636"),
    ]

    operations = [
        migrations.CreateModel(
            name="AcessoConcedidoSme",
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
                    "unidade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="incluidas_pela_sme",
                        to="core.unidade",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="acessos_habilitados_pela_sme",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Unidade incluida pela SME",
                "verbose_name_plural": "Unidades incluidas pela SME",
                "unique_together": {("unidade", "user")},
            },
        ),
    ]