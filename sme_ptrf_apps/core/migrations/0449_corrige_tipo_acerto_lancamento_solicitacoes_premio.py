from django.db import migrations


NOME_RECURSO_PREMIO = "Prêmio Excelência Educacional"


def corrige_tipos_acerto_lancamento_solicitacoes_premio(apps, schema_editor):
    Recurso = apps.get_model("core", "Recurso")
    SolicitacaoAcertoLancamento = apps.get_model(
        "core", "SolicitacaoAcertoLancamento"
    )
    TipoAcertoLancamento = apps.get_model("core", "TipoAcertoLancamento")

    recurso_premio = Recurso.objects.filter(nome=NOME_RECURSO_PREMIO).first()

    if not recurso_premio:
        return

    solicitacoes_inconsistentes = SolicitacaoAcertoLancamento.objects.filter(
        analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo__recurso=recurso_premio,
        tipo_acerto__recurso__legado=True,
    )

    tipos_acerto_origem_ids = solicitacoes_inconsistentes.values_list(
        "tipo_acerto_id", flat=True
    ).distinct()
    tipos_acerto_origem = TipoAcertoLancamento.objects.filter(
        id__in=tipos_acerto_origem_ids
    )

    for tipo_acerto_origem in tipos_acerto_origem.iterator():
        tipo_acerto_premio = TipoAcertoLancamento.objects.filter(
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
        ("core", "0448_tipoacertolancamento_recurso"),
    ]

    operations = [
        migrations.RunPython(
            corrige_tipos_acerto_lancamento_solicitacoes_premio,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
