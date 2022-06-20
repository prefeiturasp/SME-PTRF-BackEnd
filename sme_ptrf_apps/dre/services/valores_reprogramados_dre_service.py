from ..models import ParametrosDre


def lista_valores_reprogramados(associacoes_dre):
    valores_reprogramados = []
    for associacao in associacoes_dre.all():
        total_conta_um = calcula_total_conta_um(associacao)
        total_conta_dois = calcula_total_conta_dois(associacao)

        if total_conta_um is None and total_conta_dois is None:
            return "Nenhum tipo de conta definida em Parâmetro DRE"

        dados = {
            "associacao": {
                "uuid": f"{associacao.uuid}",
                "nome": associacao.nome,
                "cnpj": associacao.cnpj,
                "status_valores_reprogramados": associacao.status_valores_reprogramados,
                "unidade": {
                    "uuid": f"{associacao.unidade.uuid}",
                    "codigo_eol": associacao.unidade.codigo_eol,
                    "nome_com_tipo": associacao.unidade.nome_com_tipo,
                    "nome_dre": associacao.unidade.nome_dre
                }
            },
            "periodo": {
                "uuid": f"{associacao.periodo_inicial.uuid}",
                "referencia": associacao.periodo_inicial.referencia,
                "data_inicio_realizacao_despesas": associacao.periodo_inicial.data_inicio_realizacao_despesas,
                "data_fim_realizacao_despesas": associacao.periodo_inicial.data_fim_realizacao_despesas,
                "referencia_por_extenso": associacao.periodo_inicial.referencia_por_extenso
            },
            "total_conta_um": total_conta_um,
            "total_conta_dois": total_conta_dois
        }

        valores_reprogramados.append(dados)

    return valores_reprogramados


def calcula_total_conta_um(associacao):
    uuid_conta_um = None
    total_conta_um = 0

    if ParametrosDre.objects.all():
        if ParametrosDre.get().tipo_conta_um:
            uuid_conta_um = ParametrosDre.get().tipo_conta_um.uuid
    else:
        return None

    if uuid_conta_um is not None:
        todos_fechamentos = associacao.fechamentos_associacao.filter(
            status='IMPLANTACAO').filter(conta_associacao__tipo_conta__uuid=uuid_conta_um)

        if todos_fechamentos:
            for fechamento in todos_fechamentos:
                total_conta_um = total_conta_um + fechamento.saldo_reprogramado

            return total_conta_um
        else:
            return "-"

    else:
        return "-"


def calcula_total_conta_dois(associacao):
    uuid_conta_dois = None
    total_conta_dois = 0

    if ParametrosDre.objects.all():
        if ParametrosDre.get().tipo_conta_dois:
            uuid_conta_dois = ParametrosDre.get().tipo_conta_dois.uuid
    else:
        return None

    if uuid_conta_dois is not None:
        todos_fechamentos = associacao.fechamentos_associacao.filter(
            status='IMPLANTACAO').filter(conta_associacao__tipo_conta__uuid=uuid_conta_dois)

        if todos_fechamentos:
            for fechamento in todos_fechamentos:
                total_conta_dois = total_conta_dois + fechamento.saldo_reprogramado

            return total_conta_dois
        else:
            return "-"

    else:
        return "-"
