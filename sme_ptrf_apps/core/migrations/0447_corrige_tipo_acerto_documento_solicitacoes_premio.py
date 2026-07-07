from django.db import migrations


NOME_RECURSO_PREMIO = "Prêmio Excelência Educacional"


def corrige_tipos_acerto_solicitacoes_premio(apps, schema_editor):
    Recurso = apps.get_model("core", "Recurso")
    SolicitacaoAcertoDocumento = apps.get_model(
        "core", "SolicitacaoAcertoDocumento"
    )
    TipoAcertoDocumento = apps.get_model("core", "TipoAcertoDocumento")

    recurso_premio = Recurso.objects.filter(nome=NOME_RECURSO_PREMIO).first()

    if not recurso_premio:
        return

    solicitacoes_inconsistentes = SolicitacaoAcertoDocumento.objects.filter(
        analise_documento__analise_prestacao_conta__prestacao_conta__periodo__recurso=recurso_premio,
    ).exclude(tipo_acerto__recurso=recurso_premio)

    tipos_acerto_origem_ids = solicitacoes_inconsistentes.values_list(
        "tipo_acerto_id", flat=True
    ).distinct()
    tipos_acerto_origem = TipoAcertoDocumento.objects.filter(
        id__in=tipos_acerto_origem_ids
    )

    for tipo_acerto_origem in tipos_acerto_origem.iterator():
        tipo_acerto_premio = TipoAcertoDocumento.objects.filter(
            recurso=recurso_premio,
            nome=tipo_acerto_origem.nome,
            categoria=tipo_acerto_origem.categoria,
        ).order_by("id").first()

        if tipo_acerto_premio is None:
            continue

        solicitacoes_inconsistentes.filter(
            tipo_acerto=tipo_acerto_origem
        ).update(tipo_acerto=tipo_acerto_premio)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0446_tipoacertodocumento_recurso"),
    ]

    operations = [
        migrations.RunPython(
            corrige_tipos_acerto_solicitacoes_premio,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
