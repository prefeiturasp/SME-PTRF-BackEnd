import datetime

from django.db import migrations
from django.db.models import F

DATA_LIMITE_AUDITLOG = datetime.datetime(2025, 8, 5, 0, 0, 0)


def corrige_data_extrato_divergente(apps, schema_editor):
    ObservacaoConciliacao = apps.get_model("core", "ObservacaoConciliacao")
    ContentType = apps.get_model("contenttypes", "ContentType")
    LogEntry = apps.get_model("auditlog", "LogEntry")

    content_type = ContentType.objects.filter(
        app_label="core",
        model="observacaoconciliacao",
    ).first()

    if not content_type:
        return

    observacoes_divergentes = ObservacaoConciliacao.objects.filter(
        data_extrato__isnull=False,
        data_extrato__gt=F("periodo__data_fim_realizacao_despesas"),
        associacao__unidade__isnull=False,
    ).distinct()

    ids_divergentes = list(observacoes_divergentes.values_list("id", flat=True))

    if not ids_divergentes:
        return

    ids_auditados = set(
        LogEntry.objects.filter(
            content_type=content_type,
            timestamp__gte=DATA_LIMITE_AUDITLOG,
            changes__icontains="data_extrato",
            object_pk__in=[str(pk) for pk in ids_divergentes],
        ).values_list("object_pk", flat=True)
    )

    ids_a_corrigir = [pk for pk in ids_divergentes if str(pk) in ids_auditados]

    for observacao in ObservacaoConciliacao.objects.filter(
        id__in=ids_a_corrigir
    ).select_related("periodo"):
        observacao.data_extrato = observacao.periodo.data_fim_realizacao_despesas
        observacao.save(update_fields=["data_extrato"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0458_remove_acao_posicao_nas_pesquisas_and_more"),
    ]

    operations = [
        migrations.RunPython(
            corrige_data_extrato_divergente,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
