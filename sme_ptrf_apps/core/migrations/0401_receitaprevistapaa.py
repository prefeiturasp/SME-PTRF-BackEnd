# Generated by Django 4.2.11 on 2025-03-21 08:59

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0400_funcueplanoanualdeatividade"),
    ]

    operations = [
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
            ],
            options={
                "verbose_name": "Receita Prevista PAA",
                "verbose_name_plural": "21.0) Receitas Previstas PAA",
            },
        ),
    ]
