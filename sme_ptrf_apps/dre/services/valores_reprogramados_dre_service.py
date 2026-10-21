from ...core.models import ContaAssociacao, AcaoAssociacao, ValoresReprogramados, FechamentoPeriodo, Associacao
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import \
    APLICACAO_CAPITAL, APLICACAO_CUSTEIO, APLICACAO_LIVRE
from decimal import Decimal
from django.db.models import F
from ...core.services import associacao_pode_implantar_saldo


def get_periodo_inicial_por_recurso(associacao, recurso=None):
    periodo_inicial_associacao = associacao.get_periodo_inicial_associacao(recurso=recurso)
    if periodo_inicial_associacao:
        return periodo_inicial_associacao.periodo_inicial

    if recurso and recurso.legado and associacao.periodo_inicial:
        if associacao.periodo_inicial.recurso_id == recurso.id:
            return associacao.periodo_inicial

    if not recurso and associacao.periodo_inicial:
        return associacao.periodo_inicial

    return None


def salvar_e_concluir_valores_reprogramados(associacao, periodo, dados, visao_selecionada, recurso=None, concluir=False):
    msg = {
        'saldo_salvo': True,
        'codigo_erro': None,
        'mensagem': 'Saldo salvo com sucesso'
    }

    periodo_inicial = get_periodo_inicial_por_recurso(associacao, recurso=recurso)
    if not periodo_inicial:
        return {
            'saldo_salvo': False,
            'codigo_erro': 'periodo_inicial_nao_definido',
            'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.',
        }

    periodo = periodo_inicial

    contas = dados.get('contas', None)

    if not contas:
        msg = {
            'saldo_salvo': False,
            'codigo_erro': 'contas_nao_informadas',
            'mensagem': 'É necessário informar as contas'
        }
        return msg

    for conta in contas:
        try:
            uuid_conta_associacao = conta["conta"]["uuid"]
            obj_conta = ContaAssociacao.objects.get(uuid=conta["conta"]["uuid"])

        except ContaAssociacao.DoesNotExist:
            return {
                'saldo_salvo': False,
                'codigo_erro': 'conta_nao_encontrada',
                'mensagem': f'O objeto ContaAssociacao para o uuid {uuid_conta_associacao} não foi encontrado na base'
            }

        if recurso and obj_conta.tipo_conta.recurso_id != recurso.id:
            return {
                'saldo_salvo': False,
                'codigo_erro': 'conta_nao_pertence_recurso',
                'mensagem': f'A conta {uuid_conta_associacao} não pertence ao recurso selecionado.'
            }

        for acao in conta["conta"]["acoes"]:
            try:
                uuid_acao_associacao = acao["uuid"]
                obj_acao_associacao = AcaoAssociacao.objects.get(uuid=acao["uuid"])
            except AcaoAssociacao.DoesNotExist:
                return {
                    'saldo_salvo': False,
                    'codigo_erro': 'acao_nao_encontrada',
                    'mensagem': f'O objeto AcaoAssociacao para o uuid {uuid_acao_associacao} não foi encontrado na base'
                }

            if recurso and obj_acao_associacao.acao.recurso_id != recurso.id:
                return {
                    'saldo_salvo': False,
                    'codigo_erro': 'acao_nao_pertence_recurso',
                    'mensagem': f'A ação {uuid_acao_associacao} não pertence ao recurso selecionado.'
                }

            custeio = acao.get('custeio', None)
            if custeio:
                valor_ue_custeio = acao["custeio"].get('valor_ue', None)
                valor_dre_custeio = acao["custeio"].get('valor_dre', None)

                valores_reprogramados = ValoresReprogramados.criar(
                    associacao, periodo, obj_conta, obj_acao_associacao, APLICACAO_CUSTEIO, valor_ue_custeio,
                    valor_dre_custeio, visao_selecionada
                )

                if concluir:
                    implantar_saldos(valores_reprogramados, visao_selecionada, periodo=periodo)

            capital = acao.get('capital', None)
            if capital:
                valor_ue_capital = acao["capital"].get('valor_ue', None)
                valor_dre_capital = acao["capital"].get('valor_dre', None)
                valores_reprogramados = ValoresReprogramados.criar(
                    associacao, periodo, obj_conta, obj_acao_associacao, APLICACAO_CAPITAL, valor_ue_capital,
                    valor_dre_capital, visao_selecionada
                )

                if concluir:
                    implantar_saldos(valores_reprogramados, visao_selecionada, periodo=periodo)

            livre = acao.get('livre', None)
            if livre:
                valor_ue_livre = acao["livre"].get('valor_ue', None)
                valor_dre_livre = acao["livre"].get('valor_dre', None)
                valores_reprogramados = ValoresReprogramados.criar(
                    associacao, periodo, obj_conta, obj_acao_associacao, APLICACAO_LIVRE, valor_ue_livre,
                    valor_dre_livre, visao_selecionada
                )

                if concluir:
                    implantar_saldos(valores_reprogramados, visao_selecionada, periodo=periodo)

    if concluir:
        novo_status = calcula_novo_status(associacao, visao_selecionada, recurso=recurso)
        associacao.altera_status_valor_reprogramado(novo_status, recurso=recurso)

    return msg


def implantar_saldos(valores_reprogramados, visao_selecionada, periodo=None):
    saldo = valores_reprogramados.valor_ue if visao_selecionada == "UE" \
        else valores_reprogramados.valor_dre

    if saldo is None:
        return

    periodo_implantacao = periodo or valores_reprogramados.periodo

    FechamentoPeriodo.implanta_saldo(
        acao_associacao=valores_reprogramados.acao_associacao,
        conta_associacao=valores_reprogramados.conta_associacao,
        aplicacao=valores_reprogramados.aplicacao_recurso,
        saldo=Decimal(saldo),
        periodo=periodo_implantacao
    )


def calcula_novo_status(associacao, visao_selecionada, recurso=None):
    """
        Documentacao troca de status

        Visão   | Status Atual          | Vr UE = Vr DRE?   | Novo Status
        UE      | Não finalizado        | Diferentes        | Em conferencia DRE
        DRE     | Não finalizado        |               Apenas leitura
        UE      | Em conferencia DRE    |               Apenas leitura
        DRE     | Em conferencia DRE    | Iguais            | Valores corretos
        DRE     | Em conferencia DRE    | Diferentes        | Em correção UE
        DRE     | Em correção UE        |               Apenas leitura
        UE      | Em correção UE        | Diferentes        | Em conferencia DRE
        UE      | Em correção UE        | Iguais            | Valores corretos
        UE      | Valores corretos      |               Apenas leitura
        DRE     | Valores corretos      | Iguais            | Valores corretos
        DRE     | Valores corretos      | Diferentes        | Em correção UE
    """

    valores_iguais = possui_diferenca(associacao, recurso=recurso)
    status_atual = associacao.get_status_valores_reprogramados(recurso=recurso)
    novo_status = None

    if visao_selecionada == "UE":
        if status_atual == Associacao.STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO:
            if not valores_iguais:
                novo_status = Associacao.STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE
        elif status_atual == Associacao.STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE:
            if not valores_iguais:
                novo_status = Associacao.STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE
            else:
                novo_status = Associacao.STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS
    elif visao_selecionada == "DRE":
        if status_atual == Associacao.STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE:
            if not valores_iguais:
                novo_status = Associacao.STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE
            else:
                novo_status = Associacao.STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS
        elif status_atual == Associacao.STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS:
            if not valores_iguais:
                novo_status = Associacao.STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE
            else:
                novo_status = Associacao.STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS

    return novo_status or status_atual


def possui_diferenca(associacao, recurso=None):
    """
        Com essa logica, é possivel saber se cada registro de valor reprogramado da associacao
        está com valores iguais nos campos de valor_ue e valor_dre.

        Caso todos sejam iguais, as listas terão o mesmo tamanho
    """

    valores_reprogramados = ValoresReprogramados.objects.filter(associacao=associacao)
    if recurso:
        valores_reprogramados = valores_reprogramados.filter(periodo__recurso=recurso)

    busca_valores_iguais = valores_reprogramados.filter(valor_ue=F('valor_dre')).all()

    todos_valores_iguais = valores_reprogramados.count() == busca_valores_iguais.count()

    return todos_valores_iguais


def monta_estrutura_valores_reprogramados(associacao, recurso=None):
    lista_contas = []

    contas_da_associcacao = associacao.contas.all()

    periodo_inicial = get_periodo_inicial_por_recurso(associacao, recurso=recurso)
    if not periodo_inicial:
        return lista_contas

    if recurso:
        contas_da_associcacao = ContaAssociacao.filter_by_recurso(queryset=contas_da_associcacao, recurso=recurso)

    for conta_associacao in contas_da_associcacao:
        if not conta_associacao.ativa_no_periodo(periodo_inicial):
            continue

        acoes = []
        valores_reprogramados_da_conta = ValoresReprogramados.objects.filter(
            associacao=associacao,
            periodo=periodo_inicial,
            conta_associacao=conta_associacao,
        )

        acoes_associacao = associacao.acoes.exclude(acao__e_recursos_proprios=True)
        acoes_associacao = AcaoAssociacao.filter_by_recurso(queryset=acoes_associacao, recurso=recurso) if recurso else acoes_associacao

        for acao_associacao in acoes_associacao:
            dados_acao = {
                "nome": acao_associacao.acao.nome,
                "uuid": f"{acao_associacao.uuid}"
            }

            # Pegando todos os registros para essa conta e acao
            valores_reprogramados = ValoresReprogramados.objects.filter(associacao=associacao).filter(
                periodo=periodo_inicial
            ).filter(conta_associacao=conta_associacao).filter(acao_associacao=acao_associacao).all()

            if acao_associacao.acao.aceita_custeio:
                dados_acao["custeio"] = monta_dados_acao(valores_reprogramados, APLICACAO_CUSTEIO)

            if acao_associacao.acao.aceita_capital:
                dados_acao["capital"] = monta_dados_acao(valores_reprogramados, APLICACAO_CAPITAL)

            if acao_associacao.acao.aceita_livre:
                dados_acao["livre"] = monta_dados_acao(valores_reprogramados, APLICACAO_LIVRE)

            acoes.append(dados_acao)

        dados = {
            "conta": {
                "uuid": f"{conta_associacao.uuid}",
                "tipo_conta": conta_associacao.tipo_conta.nome,
                "acoes": acoes,
                "bloquear_campos_valor": True if conta_associacao.data_encerramento and not valores_reprogramados_da_conta.exists() else False
            }
        }

        lista_contas.append(dados)

    return lista_contas


def monta_dados_acao(valores_reprogramados, aplicacao):
    valor_ue = None
    valor_dre = None

    dados_acao = {
        "nome": aplicacao.lower(),
        "valor_ue": valor_ue,
        "valor_dre": valor_dre,
        "status_conferencia": None
    }

    if valores_reprogramados:
        valor_reprogramado_aplicacao = valores_reprogramados.filter(aplicacao_recurso=aplicacao).first()

        if valor_reprogramado_aplicacao:
            valor_ue = valor_reprogramado_aplicacao.valor_ue
            valor_dre = valor_reprogramado_aplicacao.valor_dre

            dados_acao["nome"] = aplicacao.lower()
            dados_acao["valor_ue"] = valor_ue
            dados_acao["valor_dre"] = valor_dre

            if valor_ue is not None and valor_dre is not None:
                if valor_ue == valor_dre:
                    dados_acao["status_conferencia"] = "correto"
                elif valor_ue != valor_dre:
                    dados_acao["status_conferencia"] = "incorreto"

            return dados_acao

    return dados_acao


def monta_estrutura_associacao(associacao, recurso=None):
    periodo_inicial_por_recurso = get_periodo_inicial_por_recurso(associacao, recurso=recurso)

    dados_associacao = {
        "associacao": {
            "uuid": f"{associacao.uuid}",
            "status_valores_reprogramados": associacao.get_status_valores_reprogramados(recurso=recurso),
            "nome": associacao.nome,
            "codigo_eol": associacao.unidade.codigo_eol,
            "periodo_inicial": {
                "referencia": periodo_inicial_por_recurso.referencia if periodo_inicial_por_recurso else None,
                "data_inicio_realizacao_despesas": periodo_inicial_por_recurso.data_inicio_realizacao_despesas if periodo_inicial_por_recurso else None,
                "data_fim_realizacao_despesas": periodo_inicial_por_recurso.data_fim_realizacao_despesas if periodo_inicial_por_recurso else None
            }
        }
    }

    return dados_associacao


def barra_status(associacao, recurso=None):
    """
        cor 1 = Cinza
        cor 2 = Laranja
        cor 3 = Vermelho
        cor 4 = Verde
    """

    status = {
        "texto": None,
        "cor": None,
        "periodo_fechado": None
    }

    status_valores_reprogramados = associacao.get_status_valores_reprogramados(recurso=recurso)

    if status_valores_reprogramados == Associacao.STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO:
        status["texto"] = "Não finalizado pela Associação"
        status["cor"] = 1
    elif status_valores_reprogramados == Associacao.STATUS_VALORES_REPROGRAMADOS_EM_CONFERENCIA_DRE:
        status["texto"] = "Aguardando conferência da DRE"
        status["cor"] = 2
    elif status_valores_reprogramados == Associacao.STATUS_VALORES_REPROGRAMADOS_EM_CORRECAO_UE:
        status["texto"] = "Aguardando correção pela Associação"
        status["cor"] = 3
    elif status_valores_reprogramados == Associacao.STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS:
        status["texto"] = "Análise concluída: valores corretos"
        status["cor"] = 4

    pode_implantar_saldo = associacao_pode_implantar_saldo(associacao, recurso=recurso)

    if status["texto"] and not pode_implantar_saldo["permite_implantacao"]:
        texto = " **Período fechado**"
        status["texto"] += texto
        status["periodo_fechado"] = True

    return status


def lista_valores_reprogramados(associacoes_dre, recurso=None):
    valores_reprogramados = []
    for associacao in associacoes_dre.all():
        periodo_inicial = get_periodo_inicial_por_recurso(associacao, recurso=recurso)
        if not periodo_inicial:
            continue

        recurso_atual = recurso or periodo_inicial.recurso
        total_conta_um = calcula_total_conta_um(associacao, periodo_inicial, recurso_atual)
        total_conta_dois = calcula_total_conta_dois(associacao, periodo_inicial, recurso_atual)

        if total_conta_um is None and total_conta_dois is None:
            return "Nenhum tipo de conta definida em Parâmetro DRE"

        dados = {
            "associacao": {
                "uuid": f"{associacao.uuid}",
                "nome": associacao.nome,
                "cnpj": associacao.cnpj,
                "status_valores_reprogramados": associacao.get_status_valores_reprogramados(recurso=recurso),
                "unidade": {
                    "uuid": f"{associacao.unidade.uuid}",
                    "codigo_eol": associacao.unidade.codigo_eol,
                    "nome_com_tipo": associacao.unidade.nome_com_tipo,
                    "nome_dre": associacao.unidade.nome_dre
                }
            },
            "periodo": {
                "uuid": f"{periodo_inicial.uuid}",
                "referencia": periodo_inicial.referencia,
                "data_inicio_realizacao_despesas": periodo_inicial.data_inicio_realizacao_despesas,
                "data_fim_realizacao_despesas": periodo_inicial.data_fim_realizacao_despesas,
                "referencia_por_extenso": periodo_inicial.referencia_por_extenso
            },
            "total_conta_um": total_conta_um,
            "nome_conta_um": nome_conta("conta_um", recurso_atual),
            "total_conta_dois": total_conta_dois,
            "nome_conta_dois": nome_conta("conta_dois", recurso_atual),
        }

        valores_reprogramados.append(dados)

    return valores_reprogramados


def calcula_total_conta_um(associacao, periodo_inicial, recurso):
    tipo_conta_um = recurso.tipo_conta_um if recurso else None
    total_conta_um = 0

    if not tipo_conta_um:
        return None

    valores_reprogramados = ValoresReprogramados.objects.filter(
        associacao=associacao,
        periodo=periodo_inicial,
        conta_associacao__tipo_conta=tipo_conta_um
    )

    if valores_reprogramados:
        for valor in valores_reprogramados:
            if valor.valor_ue:
                total_conta_um = total_conta_um + valor.valor_ue

        return total_conta_um
    else:
        return "-"


def calcula_total_conta_dois(associacao, periodo_inicial, recurso):
    tipo_conta_dois = recurso.tipo_conta_dois if recurso else None
    total_conta_dois = 0

    if not tipo_conta_dois:
        return None

    valores_reprogramados = ValoresReprogramados.objects.filter(
        associacao=associacao,
        periodo=periodo_inicial,
        conta_associacao__tipo_conta=tipo_conta_dois
    )

    if valores_reprogramados:
        for valor in valores_reprogramados:
            if valor.valor_ue:
                total_conta_dois = total_conta_dois + valor.valor_ue

        return total_conta_dois
    else:
        return "-"


def nome_conta(conta, recurso):
    if conta == "conta_um":
        if recurso and recurso.tipo_conta_um:
            return recurso.tipo_conta_um.nome

    elif conta == "conta_dois":
        if recurso and recurso.tipo_conta_dois:
            return recurso.tipo_conta_dois.nome

    return None
