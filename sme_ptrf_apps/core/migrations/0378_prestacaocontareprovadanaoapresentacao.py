# Generated by Django 4.2.7 on 2024-03-04 10:33

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0377_remove_parametros_desconsiderar_associacoes_nao_iniciadas"),
    ]

    operations = [
        migrations.CreateModel(
            name="PrestacaoContaReprovadaNaoApresentacao",
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
                    "data_de_reprovacao",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Data da reprovação"
                    ),
                ),
                (
                    "associacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="prestacoes_de_conta_reprovadas_por_nao_apresentacao_da_associacao",
                        to="core.associacao",
                    ),
                ),
                (
                    "periodo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="prestacoes_de_conta_reprovadas_por_nao_apresentacao_do_periodo",
                        to="core.periodo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Prestação de conta reprovada não apresentação",
                "verbose_name_plural": "09.0.1) Prestações de contas reprovadas não apresentação",
                "unique_together": {("associacao", "periodo")},
            },
        ),
    ]