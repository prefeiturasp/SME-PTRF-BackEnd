from django.db import migrations


NOME_RECURSO_PTRF = "Programa de Transferência de Recursos Financeiros - PTRF"
NOME_RECURSO_PREMIO = "Prêmio Excelência Educacional"
NOMES_TIPOS_RECEITA = ("Rendimento", "Repasse")


def migra_receitas_premio_tipo_receita(apps, schema_editor):
    Recurso = apps.get_model("core", "Recurso")
    TipoReceita = apps.get_model("receitas", "TipoReceita")
    DetalheTipoReceita = apps.get_model("receitas", "DetalheTipoReceita")
    Receita = apps.get_model("receitas", "Receita")

    recurso_ptrf = Recurso.objects.filter(nome=NOME_RECURSO_PTRF).first()
    recurso_premio = Recurso.objects.filter(nome=NOME_RECURSO_PREMIO).first()

    if not recurso_ptrf or not recurso_premio:
        return

    tipos_ptrf = {
        tipo.nome: tipo
        for tipo in TipoReceita.objects.filter(
            recurso=recurso_ptrf,
            nome__in=NOMES_TIPOS_RECEITA,
        )
    }

    tipos_premio = {
        tipo.nome: tipo
        for tipo in TipoReceita.objects.filter(
            recurso=recurso_premio,
            nome__in=NOMES_TIPOS_RECEITA,
        )
    }

    for nome_tipo_receita in NOMES_TIPOS_RECEITA:
        tipo_ptrf = tipos_ptrf.get(nome_tipo_receita)
        tipo_premio = tipos_premio.get(nome_tipo_receita)

        if not tipo_ptrf or not tipo_premio:
            continue

        detalhes_premio_por_nome = {
            detalhe.nome: detalhe
            for detalhe in DetalheTipoReceita.objects.filter(tipo_receita=tipo_premio)
        }

        receitas_premio_com_tipo_ptrf = Receita.objects.filter(
            tipo_receita=tipo_ptrf,
            conta_associacao__tipo_conta__recurso=recurso_premio,
        ).select_related("detalhe_tipo_receita")

        for receita in receitas_premio_com_tipo_ptrf.iterator():
            detalhe_receita = receita.detalhe_tipo_receita
            detalhe_premio = None

            if detalhe_receita and detalhe_receita.tipo_receita_id == tipo_ptrf.id:
                detalhe_premio = detalhes_premio_por_nome.get(detalhe_receita.nome)
            elif detalhe_receita and detalhe_receita.tipo_receita_id == tipo_premio.id:
                detalhe_premio = detalhe_receita

            receita.tipo_receita = tipo_premio
            receita.detalhe_tipo_receita = detalhe_premio
            receita.save(update_fields=["tipo_receita", "detalhe_tipo_receita", "alterado_em"])

        tipos_conta_premio = tipo_ptrf.tipos_conta.filter(recurso=recurso_premio)
        tipo_ptrf.tipos_conta.remove(*tipos_conta_premio)


class Migration(migrations.Migration):

    dependencies = [
        ("receitas", "0053_alter_receita_detalhe_tipo_receita"),
    ]

    operations = [
        migrations.RunPython(
            migra_receitas_premio_tipo_receita,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
