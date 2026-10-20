from django.db import migrations, models


STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS = "VALORES_CORRETOS"


def popular_status_por_recurso(apps, schema_editor):
    Associacao = apps.get_model("core", "Associacao")
    PeriodoInicialAssociacao = apps.get_model("core", "PeriodoInicialAssociacao")

    for periodo_inicial_associacao in PeriodoInicialAssociacao.objects.select_related("associacao").all().iterator():
        associacao = periodo_inicial_associacao.associacao
        status_global = (
            associacao.status_valores_reprogramados
            if associacao and associacao.status_valores_reprogramados
            else STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS
        )
        periodo_inicial_associacao.status_valores_reprogramados = status_global
        periodo_inicial_associacao.save(update_fields=["status_valores_reprogramados"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0434_remove_recurso_logo_alter_recurso_legado"),
    ]

    operations = [
        migrations.AddField(
            model_name="periodoinicialassociacao",
            name="status_valores_reprogramados",
            field=models.CharField(
                choices=[
                    ("NAO_FINALIZADO", "Não finalizado"),
                    ("EM_CONFERENCIA_DRE", "Em conferência DRE"),
                    ("EM_CORRECAO_UE", "Em correção UE"),
                    ("VALORES_CORRETOS", "Valores corretos"),
                ],
                default="VALORES_CORRETOS",
                max_length=20,
                verbose_name="Status dos valores reprogramados",
            ),
        ),
        migrations.RunPython(popular_status_por_recurso, noop_reverse),
    ]
