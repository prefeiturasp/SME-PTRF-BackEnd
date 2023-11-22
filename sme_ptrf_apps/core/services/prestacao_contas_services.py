import logging

from django.db import transaction
from django.db.models import Q, Sum, Count, Max

from ..models import (
    PrestacaoConta,
    FechamentoPeriodo,
    Associacao,
    DemonstrativoFinanceiro,
    ObservacaoConciliacao,
    AnaliseLancamentoPrestacaoConta,
    SolicitacaoAcertoLancamento,
    TipoAcertoLancamento,
    TipoDevolucaoAoTesouro,
    TipoDocumentoPrestacaoConta,
    AnaliseDocumentoPrestacaoConta,
    ContaAssociacao,
    TipoAcertoDocumento,
    SolicitacaoAcertoDocumento, SolicitacaoDevolucaoAoTesouro, Parametros, FalhaGeracaoPc
)
from ..services import info_acoes_associacao_no_periodo
from ..services.relacao_bens import gerar_arquivo_relacao_de_bens, apagar_previas_relacao_de_bens
from ..services.processos_services import get_processo_sei_da_prestacao, get_processo_sei_da_associacao_no_periodo
from ...despesas.models import RateioDespesa, Despesa
from ...receitas.models import Receita
from ..tasks import gerar_previa_demonstrativo_financeiro_async

from ..services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro
from .demonstrativo_financeiro_pdf_service import gerar_arquivo_demonstrativo_financeiro_pdf
from ..services.persistencia_dados_demo_financeiro_service import PersistenciaDadosDemoFinanceiro
from ..services.recuperacao_dados_persistindos_demo_financeiro_service import RecuperaDadosDemoFinanceiro
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO, STATUS_INCOMPLETO

from ..api.serializers.associacao_serializer import AssociacaoCompletoSerializer
from celery import Celery

logger = logging.getLogger(__name__)


def pc_requer_geracao_fechamentos(prestacao):
    if prestacao.status in (
        PrestacaoConta.STATUS_NAO_RECEBIDA,
        PrestacaoConta.STATUS_RECEBIDA,
        PrestacaoConta.STATUS_EM_ANALISE,
        PrestacaoConta.STATUS_APROVADA,
        PrestacaoConta.STATUS_APROVADA_RESSALVA,
        PrestacaoConta.STATUS_REPROVADA,
        PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA,
    ):
        return False

    if prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA:
        ultima_analise = prestacao.analises_da_prestacao.last()
        return ultima_analise is not None and ultima_analise.requer_geracao_fechamentos
    else:
        return True

def pc_requer_geracao_documentos(prestacao):
    if prestacao.status in (
        PrestacaoConta.STATUS_NAO_RECEBIDA,
        PrestacaoConta.STATUS_RECEBIDA,
        PrestacaoConta.STATUS_EM_ANALISE,
        PrestacaoConta.STATUS_APROVADA,
        PrestacaoConta.STATUS_APROVADA_RESSALVA,
        PrestacaoConta.STATUS_REPROVADA,
        PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA,
    ):
        return False

    if prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA:
        ultima_analise = prestacao.analises_da_prestacao.last()
        return ultima_analise is not None and ultima_analise.requer_alteracao_em_lancamentos
    else:
        return True


def pc_requer_acerto_em_extrato(prestacao):

    if prestacao.status in (
        PrestacaoConta.STATUS_NAO_RECEBIDA,
        PrestacaoConta.STATUS_RECEBIDA,
        PrestacaoConta.STATUS_EM_ANALISE,
        PrestacaoConta.STATUS_APROVADA,
        PrestacaoConta.STATUS_APROVADA_RESSALVA,
        PrestacaoConta.STATUS_REPROVADA,
        PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA,
    ):
        return False

    if prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA:
        ultima_analise = prestacao.analises_da_prestacao.last()
        return ultima_analise is not None and ultima_analise.requer_acertos_em_extrato
    else:
        return True


@transaction.atomic
def concluir_prestacao_de_contas(periodo, associacao, usuario=None, monitoraPc=False):
    prestacao = PrestacaoConta.abrir(periodo=periodo, associacao=associacao)
    logger.info(f'Aberta a prestação de contas {prestacao}.')

    e_retorno_devolucao = prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA
    requer_geracao_documentos = pc_requer_geracao_documentos(prestacao)
    requer_geracao_fechamentos = pc_requer_geracao_fechamentos(prestacao)
    requer_acertos_em_extrato = pc_requer_acerto_em_extrato(prestacao)

    if prestacao.status in (PrestacaoConta.STATUS_EM_PROCESSAMENTO, PrestacaoConta.STATUS_A_PROCESSAR):
        return {
            "prestacao": prestacao,
            "e_retorno_devolucao": e_retorno_devolucao,
            "requer_geracao_documentos": requer_geracao_documentos,
            "requer_geracao_fechamentos": requer_geracao_fechamentos,
            "erro": "A pc já está em processamento, não é possivel alterar o status para em processamento."
        }

    prestacao.a_processar()
    if monitoraPc:
        MonitoraPC(prestacao_de_contas=prestacao, usuario=usuario, associacao=associacao)

    logger.info(f'Prestação de contas aguardando processamento {prestacao}.')

    return {
        "prestacao": prestacao,
        "e_retorno_devolucao": e_retorno_devolucao,
        "requer_geracao_documentos": requer_geracao_documentos,
        "requer_geracao_fechamentos": requer_geracao_fechamentos,
        "requer_acertos_em_extrato": requer_acertos_em_extrato,
        "erro": None
    }


def gerar_doc_previa_demonstrativo_financeiro(acoes, conta, periodo):
    logger.info(f'Criando assincronamente prévia de demonstrativo financeiro do período {periodo} e conta {conta}...')
    gerar_previa_demonstrativo_financeiro_async.delay(acoes=acoes, periodo=periodo, conta_associacao=conta)


def _criar_fechamentos(acoes, contas, periodo, prestacao):
    logger.info(f'Criando fechamentos do período {periodo} e prestacao {prestacao}...')
    for conta in contas:
        logger.info(f'Criando fechamentos da conta {conta}.')
        for acao in acoes:
            logger.info(f'Criando fechamentos da ação {acao}.')
            totais_receitas = Receita.totais_por_acao_associacao_no_periodo(acao_associacao=acao, periodo=periodo,
                                                                            conta=conta)
            totais_despesas = RateioDespesa.totais_por_acao_associacao_no_periodo(acao_associacao=acao, periodo=periodo,
                                                                                  conta=conta)
            especificacoes_despesas = RateioDespesa.especificacoes_dos_rateios_da_acao_associacao_no_periodo(
                acao_associacao=acao, periodo=periodo)
            FechamentoPeriodo.criar(
                prestacao_conta=prestacao,
                acao_associacao=acao,
                conta_associacao=conta,
                total_receitas_capital=totais_receitas['total_receitas_capital'],
                total_receitas_devolucao_capital=totais_receitas['total_receitas_devolucao_capital'],
                total_repasses_capital=totais_receitas['total_repasses_capital'],
                total_receitas_custeio=totais_receitas['total_receitas_custeio'],
                total_receitas_devolucao_custeio=totais_receitas['total_receitas_devolucao_custeio'],
                total_receitas_devolucao_livre=totais_receitas['total_receitas_devolucao_livre'],
                total_repasses_custeio=totais_receitas['total_repasses_custeio'],
                total_despesas_capital=totais_despesas['total_despesas_capital'],
                total_despesas_custeio=totais_despesas['total_despesas_custeio'],
                total_receitas_livre=totais_receitas['total_receitas_livre'],
                total_repasses_livre=totais_receitas['total_repasses_livre'],
                total_receitas_nao_conciliadas_capital=totais_receitas['total_receitas_nao_conciliadas_capital'],
                total_receitas_nao_conciliadas_custeio=totais_receitas['total_receitas_nao_conciliadas_custeio'],
                total_receitas_nao_conciliadas_livre=totais_receitas['total_receitas_nao_conciliadas_livre'],
                total_despesas_nao_conciliadas_capital=totais_despesas['total_despesas_nao_conciliadas_capital'],
                total_despesas_nao_conciliadas_custeio=totais_despesas['total_despesas_nao_conciliadas_custeio'],
                especificacoes_despesas=especificacoes_despesas
            )


def _criar_documentos(acoes, contas, periodo, prestacao, usuario, criar_arquivos=True):
    logger.info(f'Criando documentos do período {periodo} e prestacao {prestacao}...')

    for conta in contas:
        logger.info(f'Gerando relação de bens da conta {conta}.')
        gerar_arquivo_relacao_de_bens(
            periodo=periodo,
            conta_associacao=conta,
            usuario=usuario,
            prestacao=prestacao,
            criar_arquivos=criar_arquivos
        )

        logger.info(f'Gerando demonstrativo financeiro da conta {conta}.')
        _gerar_arquivos_demonstrativo_financeiro(
            acoes=acoes,
            periodo=periodo,
            conta_associacao=conta,
            usuario=usuario,
            prestacao=prestacao,
            criar_arquivos=criar_arquivos
        )


def _criar_previa_demonstrativo_financeiro(acoes, conta, periodo, usuario):
    logger.info(f'Gerando prévias do demonstrativo financeiro da conta {conta}.')

    _gerar_arquivos_demonstrativo_financeiro(
        acoes=acoes,
        periodo=periodo,
        conta_associacao=conta,
        prestacao=None,
        usuario=usuario,
        previa=True,
    )


def _criar_previa_relacao_de_bens(conta, periodo, usuario):
    logger.info(f'Criando prévia de demonstrativo financeiro do período {periodo} e conta {conta}...')
    gerar_arquivo_relacao_de_bens(periodo=periodo, conta_associacao=conta, previa=True, usuario=usuario)


def apagar_previas_demonstrativo_financeiro(periodo, conta_associacao):
    DemonstrativoFinanceiro.objects.filter(periodo_previa=periodo, conta_associacao=conta_associacao).delete()


def _apagar_previas_documentos(contas, periodo, prestacao):
    logger.info(f'Apagando prévias de documentos do período {periodo} e prestacao {prestacao}...')
    for conta in contas:
        logger.info(f'Apagando prévias de relações de bens da conta {conta}.')
        apagar_previas_relacao_de_bens(periodo=periodo, conta_associacao=conta)

        logger.info(f'Apagando prévias demonstrativo financeiro da conta {conta}.')
        apagar_previas_demonstrativo_financeiro(periodo=periodo, conta_associacao=conta)


def _apagar_previas_relacao_bens(conta, periodo):
    logger.info(f'Apagando prévias de relações de bens do período {periodo} e conta {conta}...')
    apagar_previas_relacao_de_bens(periodo=periodo, conta_associacao=conta)
    logger.info(f'Apagadas as prévias de relações de bens do período {periodo} e conta {conta}...')


def _apagar_previas_demonstrativo_financeiro(conta, periodo):
    logger.info(f'Apagando prévias de demonstrativos financeiros do período {periodo} e conta {conta}...')
    apagar_previas_demonstrativo_financeiro(periodo=periodo, conta_associacao=conta)
    logger.info(f'Apagadas prévias de demonstrativos financeiros do período {periodo} e conta {conta}...')


def reabrir_prestacao_de_contas(prestacao_contas_uuid):
    logger.info(f'Reabrindo a prestação de contas de uuid {prestacao_contas_uuid}.')
    concluido = PrestacaoConta.reabrir(uuid=prestacao_contas_uuid)
    if concluido:
        logger.info(f'Prestação de contas de uuid {prestacao_contas_uuid} foi reaberta. Seus registros foram apagados.')
    return concluido


def devolver_prestacao_de_contas(prestacao_contas_uuid):
    logger.info(f'Devolvendo a prestação de contas de uuid {prestacao_contas_uuid}.')
    prestacao = PrestacaoConta.devolver(uuid=prestacao_contas_uuid)
    return prestacao


def informacoes_financeiras_para_atas(prestacao_contas):
    def totaliza_info_acoes(info_acoes):
        totalizador = {
            'saldo_reprogramado': 0,
            'saldo_reprogramado_capital': 0,
            'saldo_reprogramado_custeio': 0,
            'saldo_reprogramado_livre': 0,

            'receitas_no_periodo': 0,

            'receitas_devolucao_no_periodo': 0,
            'receitas_devolucao_no_periodo_custeio': 0,
            'receitas_devolucao_no_periodo_capital': 0,
            'receitas_devolucao_no_periodo_livre': 0,

            'repasses_no_periodo': 0,
            'repasses_no_periodo_capital': 0,
            'repasses_no_periodo_custeio': 0,
            'repasses_no_periodo_livre': 0,

            'outras_receitas_no_periodo': 0,
            'outras_receitas_no_periodo_capital': 0,
            'outras_receitas_no_periodo_custeio': 0,
            'outras_receitas_no_periodo_livre': 0,

            'despesas_no_periodo': 0,
            'despesas_no_periodo_capital': 0,
            'despesas_no_periodo_custeio': 0,

            'despesas_nao_conciliadas': 0,
            'despesas_nao_conciliadas_capital': 0,
            'despesas_nao_conciliadas_custeio': 0,

            'despesas_nao_conciliadas_anteriores': 0,
            'despesas_nao_conciliadas_anteriores_capital': 0,
            'despesas_nao_conciliadas_anteriores_custeio': 0,

            'despesas_conciliadas': 0,
            'despesas_conciliadas_capital': 0,
            'despesas_conciliadas_custeio': 0,

            'receitas_nao_conciliadas': 0,
            'receitas_nao_conciliadas_capital': 0,
            'receitas_nao_conciliadas_custeio': 0,
            'receitas_nao_conciliadas_livre': 0,

            'saldo_atual_custeio': 0,
            'saldo_atual_capital': 0,
            'saldo_atual_livre': 0,
            'saldo_atual_total': 0,

            'repasses_nao_realizados_capital': 0,
            'repasses_nao_realizados_custeio': 0,
            'repasses_nao_realizados_livre': 0,

            # Saldo Atual + Despesas Não demonstradas no período + Despesas não demonstradas períodos anteriores
            'saldo_bancario_custeio': 0,
            'saldo_bancario_capital': 0,
            'saldo_bancario_livre': 0,
            'saldo_bancario_total': 0,
        }
        for info_acao in info_acoes:
            for key in totalizador.keys():
                totalizador[key] += info_acao[key]

        return totalizador

    logger.info(
        f'Get info financeiras para ata. Associacao:{prestacao_contas.associacao.uuid} Período:{prestacao_contas.periodo}')

    info_contas = []
    for conta_associacao in prestacao_contas.contas_ativas_no_periodo():
        logger.info(
            f'Get info financeiras por conta para a ata. Associacao:{prestacao_contas.associacao.uuid} Conta:{conta_associacao}')
        info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=prestacao_contas.associacao.uuid,
                                                      periodo=prestacao_contas.periodo,
                                                      conta=conta_associacao)

        info_acoes = [info for info in info_acoes if
                      info['saldo_reprogramado'] or info['receitas_no_periodo'] or info['despesas_no_periodo']]

        info_contas.append(
            {
                'conta_associacao': {
                    'uuid': f'{conta_associacao.uuid}',
                    'nome': f'{conta_associacao.tipo_conta.nome}',
                    'banco_nome': f'{conta_associacao.banco_nome}',
                    'agencia': f'{conta_associacao.agencia}',
                    'numero_conta': f'{conta_associacao.numero_conta}',
                },
                'acoes': info_acoes,
                'totais': totaliza_info_acoes(info_acoes),
            }
        )

    info = {
        'uuid': prestacao_contas.uuid,
        'contas': info_contas,
    }

    return info


def lista_prestacoes_de_conta_nao_recebidas(
    dre,
    periodo,
    filtro_nome=None, filtro_tipo_unidade=None, filtro_status=[]
):
    associacoes_da_dre = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo, dre=dre).order_by(
        'unidade__tipo_unidade', 'unidade__nome')

    if filtro_nome is not None:
        associacoes_da_dre = associacoes_da_dre.filter(Q(nome__unaccent__icontains=filtro_nome) | Q(
            unidade__nome__unaccent__icontains=filtro_nome))

    if filtro_tipo_unidade is not None:
        associacoes_da_dre = associacoes_da_dre.filter(unidade__tipo_unidade=filtro_tipo_unidade)

    prestacoes = []
    for associacao in associacoes_da_dre:
        prestacao_conta = PrestacaoConta.objects.filter(associacao=associacao, periodo=periodo).first()

        # Devem entrar apenas Prestações de contas não apresentadas ou não recebidas
        if prestacao_conta and prestacao_conta.status not in [PrestacaoConta.STATUS_NAO_APRESENTADA,
                                                              PrestacaoConta.STATUS_NAO_RECEBIDA]:
            continue

        # Aplica o filtro por status
        if filtro_status:
            if PrestacaoConta.STATUS_NAO_APRESENTADA not in filtro_status:
                if not prestacao_conta or prestacao_conta.status not in filtro_status:
                    continue
            else:
                if prestacao_conta and prestacao_conta.status not in filtro_status:
                    continue

        if prestacao_conta:
            processo_sei = get_processo_sei_da_prestacao(prestacao_contas=prestacao_conta)
        else:
            processo_sei = get_processo_sei_da_associacao_no_periodo(associacao=associacao, periodo=periodo)

        info_prestacao = {
            'periodo_uuid': f'{periodo.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': prestacao_conta.data_ultima_analise if prestacao_conta else None,
            'processo_sei': processo_sei,
            'status': prestacao_conta.status if prestacao_conta else PrestacaoConta.STATUS_NAO_APRESENTADA,
            'tecnico_responsavel': prestacao_conta.tecnico_responsavel.nome if prestacao_conta and prestacao_conta.tecnico_responsavel else '',
            'unidade_eol': associacao.unidade.codigo_eol,
            'unidade_nome': associacao.unidade.nome,
            'unidade_tipo_unidade': associacao.unidade.tipo_unidade,
            'uuid': f'{prestacao_conta.uuid}' if prestacao_conta else '',
            'associacao_uuid': f'{associacao.uuid}',
            'devolucao_ao_tesouro': prestacao_conta.total_devolucao_ao_tesouro_str if prestacao_conta else 'Não',
            'associacao': AssociacaoCompletoSerializer(associacao, many=False).data,
        }

        prestacoes.append(info_prestacao)

    return prestacoes


def lista_prestacoes_de_conta_todos_os_status(
    dre,
    periodo,
    filtro_nome=None,
    filtro_tipo_unidade=None,
    filtro_por_devolucao_tesouro=None,
    filtro_por_status=[]
):
    associacoes_da_dre = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo, dre=dre).order_by('unidade__tipo_unidade', 'unidade__nome')

    if filtro_nome is not None:
        associacoes_da_dre = associacoes_da_dre.filter(Q(nome__unaccent__icontains=filtro_nome) | Q(
            unidade__nome__unaccent__icontains=filtro_nome))

    if filtro_tipo_unidade is not None:
        associacoes_da_dre = associacoes_da_dre.filter(unidade__tipo_unidade=filtro_tipo_unidade)

    prestacoes = []
    for associacao in associacoes_da_dre:
        prestacao_conta: PrestacaoConta = PrestacaoConta.objects.filter(associacao=associacao, periodo=periodo).first()

        if filtro_por_status and not prestacao_conta and PrestacaoConta.STATUS_NAO_APRESENTADA not in filtro_por_status:
            # Pula PCs não apresentadas se existir um filtro por status e não contiver o status não apresentada
            continue

        if filtro_por_status and prestacao_conta and prestacao_conta.status not in filtro_por_status:
            # Pula PCs apresentadas se existir um filtro por status e não contiver o status da PC
            continue

        if filtro_por_devolucao_tesouro and filtro_por_devolucao_tesouro == '1':
            if not prestacao_conta or not prestacao_conta.devolucoes_ao_tesouro_da_prestacao.exists():
                continue

        if filtro_por_devolucao_tesouro and filtro_por_devolucao_tesouro == '0':
            if prestacao_conta and prestacao_conta.devolucoes_ao_tesouro_da_prestacao.exists():
                continue

        info_prestacao = {
            'periodo_uuid': f'{periodo.uuid}',
            'data_recebimento': prestacao_conta.data_recebimento if prestacao_conta else None,
            'data_ultima_analise': prestacao_conta.data_ultima_analise if prestacao_conta else None,
            'processo_sei': get_processo_sei_da_prestacao(prestacao_contas=prestacao_conta) if prestacao_conta else '',
            'status': prestacao_conta.status if prestacao_conta else PrestacaoConta.STATUS_NAO_APRESENTADA,
            'tecnico_responsavel': prestacao_conta.tecnico_responsavel.nome if prestacao_conta and prestacao_conta.tecnico_responsavel else '',
            'unidade_eol': associacao.unidade.codigo_eol,
            'unidade_nome': associacao.unidade.nome,
            'unidade_tipo_unidade': associacao.unidade.tipo_unidade,
            'uuid': f'{prestacao_conta.uuid}' if prestacao_conta else '',
            'associacao_uuid': f'{associacao.uuid}',
            'devolucao_ao_tesouro': prestacao_conta.total_devolucao_ao_tesouro_str if prestacao_conta else 'Não',
            'associacao': AssociacaoCompletoSerializer(associacao, many=False).data,
        }

        prestacoes.append(info_prestacao)

    return prestacoes


def _gerar_arquivos_demonstrativo_financeiro(acoes, periodo, conta_associacao, prestacao=None, usuario="",
                                             previa=False, criar_arquivos=True):
    logger.info(f'Criando registro do demonstrativo financeiro da conta {conta_associacao}.')
    demonstrativo, _ = DemonstrativoFinanceiro.objects.update_or_create(
        conta_associacao=conta_associacao,
        prestacao_conta=prestacao,
        periodo_previa=None if prestacao else periodo,
        versao=DemonstrativoFinanceiro.VERSAO_PREVIA if previa else DemonstrativoFinanceiro.VERSAO_FINAL,
        status=DemonstrativoFinanceiro.STATUS_EM_PROCESSAMENTO,
    )

    try:
        observacao_conciliacao = ObservacaoConciliacao.objects.filter(periodo__uuid=periodo.uuid, conta_associacao__uuid=conta_associacao.uuid).first()
    except Exception:
        observacao_conciliacao = None

    logger.info(f'Gerando demonstrativo financeiro em PDF da conta {conta_associacao}.')
    dados_demonstrativo = gerar_dados_demonstrativo_financeiro(usuario, acoes, periodo, conta_associacao,
                                                               prestacao, observacao_conciliacao=observacao_conciliacao,
                                                               previa=previa)

    PersistenciaDadosDemoFinanceiro(dados=dados_demonstrativo, demonstrativo=demonstrativo)
    dados_recuperados = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

    if criar_arquivos:
        gerar_arquivo_demonstrativo_financeiro_pdf(dados_recuperados, demonstrativo)

    demonstrativo.arquivo_concluido()

    return demonstrativo


def tem_solicitacao_acerto_do_tipo(analise_lancamento, tipo_acerto):
    return analise_lancamento.solicitacoes_de_ajuste_da_analise.filter(tipo_acerto=tipo_acerto).exists()


def retorna_lancamentos_despesas_ordenadas_por_imposto(despesas, conta_associacao, analise_prestacao_conta, tipo_acerto,
                                                       com_ajustes, prestacao_conta, DespesaDocumentoMestreSerializer,
                                                       RateioDespesaConciliacaoSerializer, DespesaImpostoSerializer,
                                                       AnaliseLancamentoPrestacaoContaRetrieveSerializer):
    # Iniciar a lista de lançamentos com a lista de despesas ordenada
    lancamentos = []
    for despesa in despesas:

        max_notificar_dias_nao_conferido = 0
        for rateio in despesa.rateios.filter(status=STATUS_COMPLETO, conta_associacao=conta_associacao):
            if rateio.notificar_dias_nao_conferido > max_notificar_dias_nao_conferido:
                max_notificar_dias_nao_conferido = rateio.notificar_dias_nao_conferido

        analise_lancamento = analise_prestacao_conta.analises_de_lancamentos.filter(despesa=despesa).first()

        if analise_lancamento and tipo_acerto and not tem_solicitacao_acerto_do_tipo(analise_lancamento, tipo_acerto):
            continue

        if com_ajustes and (not analise_lancamento or analise_lancamento.resultado != 'AJUSTE'):
            continue

        despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
        despesas_impostos = despesa.despesas_impostos.all()

        # Retorna a lista de uuid das despesas contidas na lista de transações
        # Utilizada para verificar se a despesa já está contida nessa lista para evitar repetição
        existe_em_lancamentos = [d['uuid'] for d in lancamentos]

        # Se despesa_geradora_do_imposto não estiver atribuido,
        # ou seja for None então ela é a despesa geradora do imposto
        if not despesa_geradora_do_imposto or str(despesa.uuid) not in existe_em_lancamentos:
            lancamento = {
                'periodo': f'{prestacao_conta.periodo.uuid}',
                'conta': f'{conta_associacao.uuid}',
                'data': despesa.data_documento if despesa.data_documento else '',
                'tipo_transacao': 'Gasto',
                'numero_documento': despesa.numero_documento,
                'descricao': despesa.nome_fornecedor,
                'valor_transacao_total': despesa.valor_total,
                'valor_transacao_na_conta':
                    despesa.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).aggregate(
                        Sum('valor_rateio'))[
                        'valor_rateio__sum'],
                'valores_por_conta': despesa.rateios.filter(status=STATUS_COMPLETO).values(
                    'conta_associacao__tipo_conta__nome').annotate(
                    Sum('valor_rateio')),
                'conferido': despesa.conferido,
                'documento_mestre': DespesaDocumentoMestreSerializer(despesa, many=False).data,
                'rateios': RateioDespesaConciliacaoSerializer(
                    despesa.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).order_by(
                        'id'),
                    many=True).data,
                'notificar_dias_nao_conferido': max_notificar_dias_nao_conferido,
                'analise_lancamento': {'resultado': analise_lancamento.resultado,
                                       'uuid': analise_lancamento.uuid} if analise_lancamento else None,

                'despesa_geradora_do_imposto': DespesaImpostoSerializer(despesa_geradora_do_imposto,
                                                                        many=False).data if despesa_geradora_do_imposto else None,
                'despesas_impostos': DespesaImpostoSerializer(despesas_impostos, many=True,
                                                              required=False).data if despesas_impostos else None,
                'uuid': str(despesa.uuid)
            }

            if com_ajustes:
                lancamento['analise_lancamento'] = AnaliseLancamentoPrestacaoContaRetrieveSerializer(analise_lancamento,
                                                                                                     many=False).data
            else:
                lancamento['analise_lancamento'] = {'resultado': analise_lancamento.resultado,
                                                    'uuid': analise_lancamento.uuid} if analise_lancamento else None

            lancamentos.append(lancamento)

        if despesas_impostos:
            for despesa_imposto in despesas_impostos:

                analise_lancamento = analise_prestacao_conta.analises_de_lancamentos.filter(
                    despesa=despesa_imposto).first()

                if analise_lancamento and tipo_acerto and not tem_solicitacao_acerto_do_tipo(analise_lancamento,
                                                                                             tipo_acerto):
                    continue

                if com_ajustes and (not analise_lancamento or analise_lancamento.resultado != 'AJUSTE'):
                    continue

                despesa_geradora_do_imposto = despesa_imposto.despesa_geradora_do_imposto.first()

                rateios = despesa_imposto.rateios.all()

                for rateio in rateios:
                    if rateio.conta_associacao == conta_associacao and str(
                        despesa_imposto.uuid) not in existe_em_lancamentos and despesa_imposto.cadastro_completo():

                        lancamento = {
                            'periodo': f'{prestacao_conta.periodo.uuid}',
                            'conta': f'{conta_associacao.uuid}',
                            'data': despesa_imposto.data_documento if despesa_imposto.data_documento else '',
                            'tipo_transacao': 'Gasto',
                            'numero_documento': despesa_imposto.numero_documento,
                            'descricao': despesa_imposto.nome_fornecedor,
                            'valor_transacao_total': despesa_imposto.valor_total,
                            'valor_transacao_na_conta':
                                despesa_imposto.rateios.filter(status=STATUS_COMPLETO).filter(
                                    conta_associacao=conta_associacao).aggregate(
                                    Sum('valor_rateio'))[
                                    'valor_rateio__sum'],
                            'valores_por_conta': despesa_imposto.rateios.filter(status=STATUS_COMPLETO).values(
                                'conta_associacao__tipo_conta__nome').annotate(
                                Sum('valor_rateio')),
                            'conferido': despesa_geradora_do_imposto.conferido,
                            'documento_mestre': DespesaDocumentoMestreSerializer(despesa_imposto, many=False).data,
                            'rateios': RateioDespesaConciliacaoSerializer(
                                despesa_imposto.rateios.filter(status=STATUS_COMPLETO).filter(
                                    conta_associacao=conta_associacao).order_by('id'),
                                many=True).data,
                            'notificar_dias_nao_conferido': max_notificar_dias_nao_conferido,
                            'analise_lancamento': {'resultado': analise_lancamento.resultado,
                                                   'uuid': analise_lancamento.uuid} if analise_lancamento else None,

                            'despesa_geradora_do_imposto': DespesaImpostoSerializer(despesa_imposto,
                                                                                    many=False).data if despesa_imposto else None,
                            'despesas_impostos': None,
                            'uuid': str(despesa_imposto.uuid)
                        }

                        if com_ajustes:
                            lancamento['analise_lancamento'] = AnaliseLancamentoPrestacaoContaRetrieveSerializer(
                                analise_lancamento,
                                many=False).data
                        else:
                            lancamento['analise_lancamento'] = {'resultado': analise_lancamento.resultado,
                                                                'uuid': analise_lancamento.uuid} if analise_lancamento else None

                        lancamentos.append(lancamento)

    return lancamentos


def lancamentos_da_prestacao(
    analise_prestacao_conta,
    conta_associacao,
    acao_associacao=None,
    tipo_transacao=None,
    tipo_acerto=None,
    com_ajustes=False,
    ordenar_por_imposto=None,
    numero_de_documento=None,
    tipo_de_documento=None,
    tipo_de_pagamento=None,
    filtrar_por_data_inicio=None,
    filtrar_por_data_fim=None,
    filtrar_por_nome_fornecedor=None,
    filtro_informacoes_list=None,
    filtro_conferencia_list=None,
    inclui_inativas=False,
    agrupa_solicitacoes=True
):
    from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaDocumentoMestreSerializer, \
        DespesaImpostoSerializer
    from sme_ptrf_apps.despesas.api.serializers.rateio_despesa_serializer import RateioDespesaConciliacaoSerializer
    from sme_ptrf_apps.receitas.api.serializers.receita_serializer import ReceitaConciliacaoSerializer
    from sme_ptrf_apps.core.api.serializers.analise_lancamento_prestacao_conta_serializer import \
        AnaliseLancamentoPrestacaoContaRetrieveSerializer, \
        AnaliseLancamentoPrestacaoContaSolicitacoesNaoAgrupadasRetrieveSerializer

    def documentos_de_despesa_por_conta_e_acao_no_periodo(
        conta_associacao,
        acao_associacao,
        periodo,
        numero_de_documento,
        tipo_de_documento,
        tipo_de_pagamento,
        filtrar_por_data_inicio,
        filtrar_por_data_fim,
        filtrar_por_nome_fornecedor=None,
        filtro_informacoes_list=None,
        filtro_conferencia_list=None,
        inclui_inativas=False,
    ):
        rateios = RateioDespesa.rateios_da_conta_associacao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo,
            incluir_inativas=True,
        )
        despesas_com_rateios = rateios.values_list('despesa__id', flat=True).distinct()

        if inclui_inativas:
            dataset = Despesa.objects.exclude(status=STATUS_INCOMPLETO).filter(id__in=despesas_com_rateios)
        else:
            dataset = Despesa.completas.filter(id__in=despesas_com_rateios)

        if filtrar_por_data_inicio and filtrar_por_data_fim:
            dataset = dataset.filter(data_transacao__range=[filtrar_por_data_inicio, filtrar_por_data_fim])

        elif filtrar_por_data_inicio and not filtrar_por_data_fim:
            dataset = dataset.filter(
                Q(data_transacao__gte=filtrar_por_data_inicio)
            )

        elif not filtrar_por_data_inicio and filtrar_por_data_fim:
            dataset = dataset.filter(
                Q(data_transacao__lte=filtrar_por_data_fim)
            )

        if numero_de_documento:
            dataset = dataset.filter(
                Q(numero_documento__unaccent__icontains=numero_de_documento) |
                Q(numero_documento__unaccent__istartswith=numero_de_documento) |
                Q(numero_documento__unaccent__iendswith=numero_de_documento)
            )

        if tipo_de_documento:
            dataset = dataset.filter(tipo_documento=tipo_de_documento)

        if tipo_de_pagamento:
            dataset = dataset.filter(tipo_transacao=tipo_de_pagamento)

        if filtrar_por_nome_fornecedor:
            dataset = dataset.filter(nome_fornecedor__unaccent__icontains=filtrar_por_nome_fornecedor)

        if filtro_informacoes_list:
            ids_para_excluir = []
            for despesa in dataset:
                excluir_despesa = True
                if Despesa.TAG_ANTECIPADO['id'] in filtro_informacoes_list and despesa.teve_pagamento_antecipado():
                    excluir_despesa = False
                if Despesa.TAG_ESTORNADO['id'] in filtro_informacoes_list and despesa.possui_estornos():
                    excluir_despesa = False
                if Despesa.TAG_IMPOSTO['id'] in filtro_informacoes_list and despesa.possui_retencao_de_impostos():
                    excluir_despesa = False
                if Despesa.TAG_IMPOSTO_PAGO['id'] in filtro_informacoes_list and despesa.e_despesa_de_imposto():
                    excluir_despesa = False
                if Despesa.TAG_PARCIAL['id'] in filtro_informacoes_list and despesa.tem_pagamento_com_recursos_proprios() or Despesa.TAG_PARCIAL['id'] in filtro_informacoes_list and despesa.tem_pagamentos_em_multiplas_contas():
                    excluir_despesa = False
                if Despesa.TAG_NAO_RECONHECIDA['id'] in filtro_informacoes_list and despesa.e_despesa_nao_reconhecida():
                    excluir_despesa = False
                if Despesa.TAG_SEM_COMPROVACAO_FISCAL['id'] in filtro_informacoes_list and despesa.e_despesa_sem_comprovacao_fiscal():
                    excluir_despesa = False
                if Despesa.TAG_CONCILIADA['id'] in filtro_informacoes_list and despesa.conferido:
                    excluir_despesa = False
                if Despesa.TAG_NAO_CONCILIADA['id'] in filtro_informacoes_list and not despesa.conferido:
                    excluir_despesa = False
                if Despesa.TAG_INATIVA['id'] in filtro_informacoes_list and despesa.e_despesa_inativa():
                    excluir_despesa = False

                if excluir_despesa:
                    ids_para_excluir.append(despesa.id)

            dataset = dataset.exclude(id__in=ids_para_excluir)

        if filtro_conferencia_list:
            ids_para_excluir = []
            for despesa in dataset:
                excluir_despesa = True
                analise_lancamento = analise_prestacao_conta.analises_de_lancamentos.filter(despesa=despesa).first()

                if 'AJUSTE' in filtro_conferencia_list and analise_lancamento and analise_lancamento.resultado == 'AJUSTE':
                    excluir_despesa = False

                if 'CORRETO' in filtro_conferencia_list and analise_lancamento and analise_lancamento.resultado == 'CORRETO' and analise_lancamento.houve_considerados_corretos_automaticamente == False:
                    excluir_despesa = False

                if 'CONFERENCIA_AUTOMATICA' in filtro_conferencia_list and analise_lancamento and analise_lancamento.houve_considerados_corretos_automaticamente == True:
                    excluir_despesa = False

                if 'NAO_CONFERIDO' in filtro_conferencia_list and not analise_lancamento:
                    excluir_despesa = False

                if excluir_despesa:
                    ids_para_excluir.append(despesa.id)

            dataset = dataset.exclude(id__in=ids_para_excluir)

        return dataset.all()

    receitas = []
    despesas = []

    prestacao_conta = analise_prestacao_conta.prestacao_conta

    tem_filtro_apenas_despesas = numero_de_documento or tipo_de_documento or tipo_de_pagamento or filtrar_por_nome_fornecedor
    if (not tipo_transacao or tipo_transacao == "CREDITOS") and not tem_filtro_apenas_despesas:
        receitas = Receita.receitas_da_conta_associacao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=prestacao_conta.periodo,
            filtrar_por_data_inicio=filtrar_por_data_inicio,
            filtrar_por_data_fim=filtrar_por_data_fim,
            filtro_informacoes_list=filtro_informacoes_list,
            filtro_conferencia_list=filtro_conferencia_list,
            analise_prestacao_conta=analise_prestacao_conta,
            inclui_inativas=True,
        )

        receitas = receitas.order_by("data")

    if not tipo_transacao or tipo_transacao == "GASTOS":
        despesas = documentos_de_despesa_por_conta_e_acao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=prestacao_conta.periodo,
            numero_de_documento=numero_de_documento,
            tipo_de_documento=tipo_de_documento,
            tipo_de_pagamento=tipo_de_pagamento,
            filtrar_por_data_inicio=filtrar_por_data_inicio,
            filtrar_por_data_fim=filtrar_por_data_fim,
            filtrar_por_nome_fornecedor=filtrar_por_nome_fornecedor,
            filtro_informacoes_list=filtro_informacoes_list,
            filtro_conferencia_list=filtro_conferencia_list,
            inclui_inativas=True,
        )

        despesas = despesas.order_by("data_documento")

    lancamentos = []

    if ordenar_por_imposto != 'true':
        # Iniciar a lista de lançamentos com a lista de despesas ordenada
        for despesa in despesas:

            max_notificar_dias_nao_conferido = 0
            despesas_filter = despesa.rateios.filter(status=STATUS_COMPLETO, conta_associacao=conta_associacao)

            if inclui_inativas:
                despesas_filter = despesa.rateios.exclude(status=STATUS_INCOMPLETO).filter(
                    conta_associacao=conta_associacao)
            for rateio in despesas_filter:
                if rateio.notificar_dias_nao_conferido > max_notificar_dias_nao_conferido:
                    max_notificar_dias_nao_conferido = rateio.notificar_dias_nao_conferido

            analise_lancamento = analise_prestacao_conta.analises_de_lancamentos.filter(despesa=despesa).first()

            if analise_lancamento and tipo_acerto and not tem_solicitacao_acerto_do_tipo(analise_lancamento,
                                                                                         tipo_acerto):
                continue

            if com_ajustes and (not analise_lancamento or analise_lancamento.resultado != 'AJUSTE'):
                continue

            despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
            despesas_impostos = despesa.despesas_impostos.all()

            lancamento = {
                'periodo': f'{prestacao_conta.periodo.uuid}',
                'conta': f'{conta_associacao.uuid}',
                'data': despesa.data_documento if despesa.data_documento else despesa.data_transacao if despesa.data_transacao else '',
                'tipo_transacao': 'Gasto',
                'numero_documento': despesa.numero_documento,
                'descricao': despesa.nome_fornecedor,
                'valor_transacao_total': despesa.valor_total,
                'valor_transacao_na_conta': despesas_filter.aggregate(Sum('valor_rateio'))['valor_rateio__sum'],
                'valores_por_conta': despesas_filter.values('conta_associacao__tipo_conta__nome').annotate(
                    Sum('valor_rateio')),
                'conferido': despesa.conferido,
                'documento_mestre': DespesaDocumentoMestreSerializer(despesa, many=False).data,
                'rateios': RateioDespesaConciliacaoSerializer(despesas_filter.order_by('id'), many=True).data,
                'notificar_dias_nao_conferido': max_notificar_dias_nao_conferido,
                'analise_lancamento': {'resultado': analise_lancamento.resultado,
                                       'uuid': analise_lancamento.uuid,
                                       'houve_considerados_corretos_automaticamente': analise_lancamento.houve_considerados_corretos_automaticamente,
                                       } if analise_lancamento else None,
                'despesa_geradora_do_imposto': DespesaImpostoSerializer(despesa_geradora_do_imposto,
                                                                        many=False).data if despesa_geradora_do_imposto else None,
                'despesas_impostos': DespesaImpostoSerializer(despesas_impostos, many=True,
                                                              required=False).data if despesas_impostos else None,
                'informacoes': despesa.tags_de_informacao,
                'informacoes_ordenamento': despesa.tags_de_informacao_concatenadas
            }

            if com_ajustes:
                if agrupa_solicitacoes:
                    lancamento['analise_lancamento'] = AnaliseLancamentoPrestacaoContaRetrieveSerializer(
                        analise_lancamento,
                        many=False).data
                else:
                    lancamento[
                        'analise_lancamento'] = AnaliseLancamentoPrestacaoContaSolicitacoesNaoAgrupadasRetrieveSerializer(
                        analise_lancamento,
                        many=False).data
            else:
                lancamento['analise_lancamento'] = {'resultado': analise_lancamento.resultado,
                                                    'uuid': analise_lancamento.uuid,
                                                    'houve_considerados_corretos_automaticamente': analise_lancamento.houve_considerados_corretos_automaticamente,
                                                    } if analise_lancamento else None

            lancamentos.append(lancamento)

    # Percorrer a lista de créditos ordenada e para cada credito, buscar na lista de lançamentos a posição correta
    for receita in receitas:

        analise_lancamento = analise_prestacao_conta.analises_de_lancamentos.filter(receita=receita).first()

        if analise_lancamento and tipo_acerto and not tem_solicitacao_acerto_do_tipo(analise_lancamento, tipo_acerto):
            continue

        if com_ajustes and (not analise_lancamento or analise_lancamento.resultado != 'AJUSTE'):
            continue

        novo_lancamento = {
            'periodo': f'{prestacao_conta.periodo.uuid}',
            'conta': f'{conta_associacao.uuid}',
            'data': receita.data,
            'tipo_transacao': 'Crédito',
            'numero_documento': '',
            'descricao': receita.tipo_receita.nome if receita.tipo_receita else '',
            'valor_transacao_total': receita.valor,
            'valor_transacao_na_conta': receita.valor,
            'valores_por_conta': [],
            'conferido': receita.conferido,
            'documento_mestre': ReceitaConciliacaoSerializer(receita, many=False).data,
            'rateios': [],
            'notificar_dias_nao_conferido': receita.notificar_dias_nao_conferido,
            'analise_lancamento': {'resultado': analise_lancamento.resultado,
                                   'uuid': analise_lancamento.uuid,
                                   'houve_considerados_corretos_automaticamente': analise_lancamento.houve_considerados_corretos_automaticamente,
                                   } if analise_lancamento else None,
            'informacoes': receita.tags_de_informacao,
            'informacoes_ordenamento': receita.tags_de_informacao_concatenadas
        }

        if com_ajustes:
            if agrupa_solicitacoes:
                novo_lancamento['analise_lancamento'] = AnaliseLancamentoPrestacaoContaRetrieveSerializer(
                    analise_lancamento,
                    many=False).data
            else:
                novo_lancamento[
                    'analise_lancamento'] = AnaliseLancamentoPrestacaoContaSolicitacoesNaoAgrupadasRetrieveSerializer(
                    analise_lancamento,
                    many=False).data

        else:
            novo_lancamento['analise_lancamento'] = {'resultado': analise_lancamento.resultado,
                                                     'uuid': analise_lancamento.uuid,
                                                     'houve_considerados_corretos_automaticamente': analise_lancamento.houve_considerados_corretos_automaticamente,
                                                     } if analise_lancamento else None

        lancamento_adicionado = False

        if lancamentos:
            for idx, lancamento in enumerate(lancamentos):
                if novo_lancamento['data'] <= lancamento['data']:
                    lancamentos.insert(idx, novo_lancamento)
                    lancamento_adicionado = True
                    break

        if not lancamento_adicionado:
            lancamentos.append(novo_lancamento)

    # A verificação de ordenar por imposto foi a última para trazer os impostos para os primeiros registros
    if ordenar_por_imposto == 'true':
        despesas = despesas.annotate(c=Count('despesas_impostos'), c2=Count('despesa_geradora'),
                                     c3=Max('data_transacao')).order_by('-c', 'c3', '-c2')
        lancamentos_ordenadas_por_imposto = retorna_lancamentos_despesas_ordenadas_por_imposto(despesas,
                                                                                               conta_associacao,
                                                                                               analise_prestacao_conta,
                                                                                               tipo_acerto, com_ajustes,
                                                                                               prestacao_conta,
                                                                                               DespesaDocumentoMestreSerializer,
                                                                                               RateioDespesaConciliacaoSerializer,
                                                                                               DespesaImpostoSerializer,
                                                                                               AnaliseLancamentoPrestacaoContaRetrieveSerializer)

        lancamentos = lancamentos_ordenadas_por_imposto + lancamentos

    return lancamentos


def marca_lancamentos_como_corretos(analise_prestacao, lancamentos_corretos):
    def marca_credito_correto(credito_uuid):
        if not analise_prestacao.analises_de_lancamentos.filter(receita__uuid=credito_uuid).exists():
            logging.info(
                f'Criando analise de lançamento do crédito {credito_uuid} na análise de PC {analise_prestacao.uuid}.')
            receita = Receita.by_uuid(credito_uuid)
            AnaliseLancamentoPrestacaoConta.objects.create(
                analise_prestacao_conta=analise_prestacao,
                tipo_lancamento="CREDITO",
                receita=receita
            )
        else:
            minha_analise_lancamento = analise_prestacao.analises_de_lancamentos.filter(
                receita__uuid=credito_uuid).first()

            minhas_solicitacoes = minha_analise_lancamento.solicitacoes_de_ajuste_da_analise.all()

            for solicitacao_acerto in minhas_solicitacoes:
                logging.info(f'Apagando solicitação de acerto {solicitacao_acerto.uuid}.')
                solicitacao_acerto.delete()

            minha_analise_lancamento.resultado = AnaliseLancamentoPrestacaoConta.RESULTADO_CORRETO
            minha_analise_lancamento.save()

    def marca_gasto_correto(gasto_uuid):
        if not analise_prestacao.analises_de_lancamentos.filter(despesa__uuid=gasto_uuid).exists():
            logging.info(
                f'Apagando analise de lançamento do gasto {gasto_uuid} na análise de PC {analise_prestacao.uuid}.')
            despesa = Despesa.by_uuid(gasto_uuid)
            AnaliseLancamentoPrestacaoConta.objects.create(
                analise_prestacao_conta=analise_prestacao,
                tipo_lancamento="GASTO",
                despesa=despesa
            )
        else:
            minha_analise_lancamento = analise_prestacao.analises_de_lancamentos.filter(
                despesa__uuid=gasto_uuid).first()

            minhas_solicitacoes = minha_analise_lancamento.solicitacoes_de_ajuste_da_analise.all()

            for solicitacao_acerto in minhas_solicitacoes:
                # TODO Remover o bloco comentado após conclusão da mudança em solicitações de dev.tesouro
                # if solicitacao_acerto.copiado:
                #     devolucao_ao_tesouro = solicitacao_acerto.devolucao_ao_tesouro
                #     if devolucao_ao_tesouro:
                #         logging.info(f'A solicitação de acerto {solicitacao_acerto.uuid} '
                #                      f'foi copiada de uma analise anterior, a devolucao ao tesouro '
                #                      f'{devolucao_ao_tesouro} NÃO será apagada.')
                # else:
                #     devolucao_ao_tesouro = solicitacao_acerto.devolucao_ao_tesouro
                #     if devolucao_ao_tesouro:
                #         logging.info(f'A solicitação de acerto {solicitacao_acerto.uuid} '
                #                      f'NÃO foi copiada de uma analise anterior, a devolucao ao tesouro '
                #                      f'{devolucao_ao_tesouro} SERÁ apagada.')
                #
                #         devolucao_ao_tesouro.delete()

                logging.info(f'Apagando solicitação de acerto {solicitacao_acerto.uuid}.')
                solicitacao_acerto.delete()

            minha_analise_lancamento.resultado = AnaliseLancamentoPrestacaoConta.RESULTADO_CORRETO
            minha_analise_lancamento.save()

    logging.info(f'Marcando lançamento como corretos na análise de PC {analise_prestacao.uuid}.')
    for lancamento in lancamentos_corretos:
        if lancamento["tipo_lancamento"] == 'CREDITO':
            marca_credito_correto(credito_uuid=lancamento["lancamento"])
        else:
            marca_gasto_correto(gasto_uuid=lancamento["lancamento"])


def marca_lancamentos_como_nao_conferidos(analise_prestacao, lancamentos_nao_conferidos):
    def marca_credito_nao_conferido(credito_uuid):
        logging.info(
            f'Apagando analise de lançamento do crédito {credito_uuid} na análise de PC {analise_prestacao.uuid}.')
        analise_prestacao.analises_de_lancamentos.filter(receita__uuid=credito_uuid).delete()

    def marca_gasto_nao_conferido(gasto_uuid):
        logging.info(f'Apagando analise de lançamento do gasto {gasto_uuid} na análise de PC {analise_prestacao.uuid}.')
        analise_prestacao.analises_de_lancamentos.filter(despesa__uuid=gasto_uuid).delete()

    logging.info(f'Marcando lançamento como não conferidos na análise de PC {analise_prestacao.uuid}.')
    for lancamento in lancamentos_nao_conferidos:
        if lancamento["tipo_lancamento"] == 'CREDITO':
            marca_credito_nao_conferido(credito_uuid=lancamento["lancamento"])
        else:
            marca_gasto_nao_conferido(gasto_uuid=lancamento["lancamento"])


def __altera_status_analise_lancamento(analise_prestacao, lancamento):
    if lancamento['tipo_lancamento'] == 'CREDITO':
        analise = AnaliseLancamentoPrestacaoConta.objects.filter(
            analise_prestacao_conta=analise_prestacao,
            receita__uuid=lancamento['lancamento_uuid']
        ).first()

        analise.resultado = AnaliseLancamentoPrestacaoConta.RESULTADO_CORRETO
        analise.save()
    else:
        analise = AnaliseLancamentoPrestacaoConta.objects.filter(
            analise_prestacao_conta=analise_prestacao,
            despesa__uuid=lancamento['lancamento_uuid']
        ).first()

        analise.resultado = AnaliseLancamentoPrestacaoConta.RESULTADO_CORRETO
        analise.save()


def __get_analise_lancamento(analise_prestacao, lancamento):
    if lancamento['tipo_lancamento'] == 'CREDITO':
        analise = AnaliseLancamentoPrestacaoConta.objects.filter(
            analise_prestacao_conta=analise_prestacao,
            receita__uuid=lancamento['lancamento_uuid']
        ).first()
    else:
        analise = AnaliseLancamentoPrestacaoConta.objects.filter(
            analise_prestacao_conta=analise_prestacao,
            despesa__uuid=lancamento['lancamento_uuid']
        ).first()

    return analise


def __cria_analise_lancamento_solicitacao_acerto(analise_prestacao, lancamento):
    if lancamento['tipo_lancamento'] == 'CREDITO':
        receita = Receita.by_uuid(lancamento['lancamento_uuid'])
        analise_lancamento = AnaliseLancamentoPrestacaoConta.objects.create(
            analise_prestacao_conta=analise_prestacao,
            tipo_lancamento="CREDITO",
            receita=receita,
            resultado=AnaliseLancamentoPrestacaoConta.RESULTADO_AJUSTE,
        )
    else:
        despesa = Despesa.by_uuid(lancamento['lancamento_uuid'])
        analise_lancamento = AnaliseLancamentoPrestacaoConta.objects.create(
            analise_prestacao_conta=analise_prestacao,
            tipo_lancamento="GASTO",
            despesa=despesa,
            resultado=AnaliseLancamentoPrestacaoConta.RESULTADO_AJUSTE,
        )

    return analise_lancamento


def __analisa_solicitacoes_acerto(solicitacoes_acerto, analise_lancamento, atualizacao_em_lote):
    logging.info(
        f'Verificando quais solicitações de ajustes existentes devem ser apagadas para a análise de lançamento {analise_lancamento.uuid}.')

    keep_solicitacoes = []
    for solicitacao_acerto in solicitacoes_acerto:
        if solicitacao_acerto['uuid']:
            solicitacao_encontrada = SolicitacaoAcertoLancamento.objects.get(uuid=solicitacao_acerto['uuid'])
            if solicitacao_encontrada:
                logging.info(f"Solicitação encontrada: {solicitacao_encontrada}")

                # Realizando update das solicitacoes encontradas
                solicitacao_encontrada.detalhamento = solicitacao_acerto['detalhamento']
                solicitacao_encontrada.save()

                # Realizando update na solicitação de devolucao ao tesouro da solicitação encontrada
                if hasattr(solicitacao_encontrada,
                           'solicitacao_devolucao_ao_tesouro') and solicitacao_encontrada.solicitacao_devolucao_ao_tesouro:
                    tipo_devolucao_ao_tesouro = TipoDevolucaoAoTesouro.objects.get(
                        uuid=solicitacao_acerto['devolucao_tesouro']['tipo'])
                    solicitacao_encontrada.solicitacao_devolucao_ao_tesouro.tipo = tipo_devolucao_ao_tesouro
                    solicitacao_encontrada.solicitacao_devolucao_ao_tesouro.devolucao_total = \
                    solicitacao_acerto['devolucao_tesouro']['devolucao_total']
                    solicitacao_encontrada.solicitacao_devolucao_ao_tesouro.valor = \
                    solicitacao_acerto['devolucao_tesouro']['valor']
                    solicitacao_encontrada.solicitacao_devolucao_ao_tesouro.motivo = solicitacao_acerto['detalhamento']

                    solicitacao_encontrada.solicitacao_devolucao_ao_tesouro.save()

                keep_solicitacoes.append(solicitacao_encontrada.uuid)
            else:
                continue
        else:
            logging.info(f"Não encontrada chave uuid da solicitação: {solicitacao_acerto['uuid']}. Será criado.")

            tipo_acerto = TipoAcertoLancamento.objects.get(uuid=solicitacao_acerto['tipo_acerto'])

            # TODO Remover o bloco comentado após conclusão da mudança em solicitações de dev.tesouro
            # devolucao_tesouro = None
            # if analise_lancamento.tipo_lancamento == 'GASTO' and solicitacao_acerto['devolucao_tesouro']:
            #     logging.info(f'Criando devolução ao tesouro para a análise de lançamento {analise_lancamento.uuid}.')
            #     devolucao_tesouro = DevolucaoAoTesouro.objects.create(
            #         prestacao_conta=analise_lancamento.analise_prestacao_conta.prestacao_conta,
            #         tipo=TipoDevolucaoAoTesouro.objects.get(uuid=solicitacao_acerto['devolucao_tesouro']['tipo']),
            #         data=solicitacao_acerto['devolucao_tesouro']['data'],
            #         despesa=analise_lancamento.despesa,
            #         devolucao_total=solicitacao_acerto['devolucao_tesouro']['devolucao_total'],
            #         valor=solicitacao_acerto['devolucao_tesouro']['valor'],
            #         motivo=solicitacao_acerto['detalhamento']
            #     )

            if not solicitacao_acerto['devolucao_tesouro'] or analise_lancamento.tipo_lancamento == 'GASTO':
                # Em atualizações em lote Apenas lançamentos do tipo gasto recebem ajustes de devolução ao tesouro
                logging.info(f'Criando solicitação de acerto para a análise de lançamento {analise_lancamento.uuid}.')

                solicitacao_criada = SolicitacaoAcertoLancamento.objects.create(
                    analise_lancamento=analise_lancamento,
                    tipo_acerto=tipo_acerto,
                    devolucao_ao_tesouro=None,  # devolucao_tesouro,
                    detalhamento=solicitacao_acerto['detalhamento'],
                    status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE
                )

                logging.info(f"Solicitação criada: {solicitacao_criada}.")

                keep_solicitacoes.append(solicitacao_criada.uuid)

            if analise_lancamento.tipo_lancamento == 'GASTO' and solicitacao_acerto['devolucao_tesouro']:
                logging.info(
                    f'Criando solicitação de devolução ao tesouro para a análise de lançamento {analise_lancamento.uuid}.')
                solicitacao_devolucao_ao_tesouro = SolicitacaoDevolucaoAoTesouro.objects.create(
                    solicitacao_acerto_lancamento=solicitacao_criada,
                    tipo=TipoDevolucaoAoTesouro.objects.get(uuid=solicitacao_acerto['devolucao_tesouro']['tipo']),
                    devolucao_total=solicitacao_acerto['devolucao_tesouro']['devolucao_total'],
                    valor=solicitacao_acerto['devolucao_tesouro']['valor'],
                    motivo=solicitacao_acerto['detalhamento']
                )
                logging.info(f"Solicitação de devolução ao tesouro criada: {solicitacao_devolucao_ao_tesouro}.")

    if not atualizacao_em_lote:
        for solicitacao_existente in analise_lancamento.solicitacoes_de_ajuste_da_analise.all():
            if solicitacao_existente.uuid not in keep_solicitacoes:
                logging.info(f"A solicitação: {solicitacao_existente} será apagada.")

                # TODO Remover o bloco comentado após conclusão da mudança em solicitações de dev.tesouro
                # devolucao_ao_tesouro = solicitacao_existente.devolucao_ao_tesouro
                # if devolucao_ao_tesouro:
                #     if solicitacao_existente.copiado:
                #         logging.info(f"A solicitação: {solicitacao_existente} foi copiada de uma analise anterior, "
                #                      f"a devolução NÃO será apagada")
                #     else:
                #         logging.info(f'Apagando devolução ao tesouro {devolucao_ao_tesouro.uuid}.')
                #         devolucao_ao_tesouro.delete()

                solicitacao_existente.delete()


def __atualiza_analise_lancamento_para_acerto(analise_lancamento):
    if analise_lancamento.resultado != AnaliseLancamentoPrestacaoConta.RESULTADO_AJUSTE:
        analise_lancamento.resultado = AnaliseLancamentoPrestacaoConta.RESULTADO_AJUSTE
        analise_lancamento.save()
    return analise_lancamento


def solicita_acertos_de_lancamentos(analise_prestacao, lancamentos, solicitacoes_acerto):
    atualizacao_em_lote = len(lancamentos) > 1
    logging.info(
        f'Criando solicitações de acerto na análise de PC {analise_prestacao.uuid}. em_lote={atualizacao_em_lote}')

    for lancamento in lancamentos:

        analise_lancamento = __get_analise_lancamento(analise_prestacao=analise_prestacao, lancamento=lancamento)

        if solicitacoes_acerto:
            if not analise_lancamento:
                analise_lancamento = __cria_analise_lancamento_solicitacao_acerto(
                    analise_prestacao=analise_prestacao,
                    lancamento=lancamento
                )
            else:
                __atualiza_analise_lancamento_para_acerto(analise_lancamento=analise_lancamento)

        __analisa_solicitacoes_acerto(
            solicitacoes_acerto=solicitacoes_acerto,
            analise_lancamento=analise_lancamento,
            atualizacao_em_lote=atualizacao_em_lote
        )

        if not atualizacao_em_lote and not solicitacoes_acerto:
            __altera_status_analise_lancamento(analise_prestacao=analise_prestacao, lancamento=lancamento)


def documentos_da_prestacao(analise_prestacao_conta):
    from ..models import TipoDocumentoPrestacaoConta

    associacao = analise_prestacao_conta.prestacao_conta.associacao

    def result_documento(_documento, _conta_associacao=None):
        analise_documento = analise_prestacao_conta.analises_de_documento.filter(
            tipo_documento_prestacao_conta=documento,
            conta_associacao=_conta_associacao
        ).first()
        return {
            'tipo_documento_prestacao_conta': {
                'uuid': f'{_documento.uuid}',
                'nome': f'{_documento.nome} {_conta_associacao.tipo_conta.nome}' if _conta_associacao else _documento.nome,
                'documento_por_conta': True if _conta_associacao else False,
                'conta_associacao': f'{_conta_associacao.uuid}' if _conta_associacao else None
            },
            'analise_documento': {
                'resultado': analise_documento.resultado,
                'uuid': analise_documento.uuid,
                'tipo_conta': analise_documento.conta_associacao.tipo_conta.nome if analise_documento.conta_associacao else None,
                'conta_associacao': f'{_conta_associacao.uuid}' if _conta_associacao else None
            } if analise_documento else None
        }

    documentos = []
    for documento in TipoDocumentoPrestacaoConta.objects.all():
        if documento.documento_por_conta:
            contas_com_movimento = analise_prestacao_conta.prestacao_conta.get_contas_com_movimento(
                add_sem_movimento_com_saldo=True)
            for conta in contas_com_movimento:
                if documento.e_relacao_bens and not analise_prestacao_conta.prestacao_conta.relacoes_de_bens_da_prestacao.filter(
                    conta_associacao=conta).exists():
                    continue
                documentos.append(result_documento(documento, conta))
        else:
            documentos.append(result_documento(documento))

    return documentos


def marca_documentos_como_corretos(analise_prestacao, documentos_corretos):
    def marca_documento_correto(tipo_documento_uuid, conta_associacao_uuid=None):
        if not analise_prestacao.analises_de_documento.filter(
            tipo_documento_prestacao_conta__uuid=tipo_documento_uuid,
            conta_associacao__uuid=conta_associacao_uuid
        ).exists():
            logging.info(
                f'Criando analise de documento {tipo_documento_uuid} conta {conta_associacao_uuid} na análise de PC {analise_prestacao.uuid}.')
            tipo_documento = TipoDocumentoPrestacaoConta.by_uuid(tipo_documento_uuid)
            conta = ContaAssociacao.by_uuid(conta_associacao_uuid) if conta_associacao_uuid else None
            AnaliseDocumentoPrestacaoConta.objects.create(
                analise_prestacao_conta=analise_prestacao,
                tipo_documento_prestacao_conta=tipo_documento,
                conta_associacao=conta,
                resultado=AnaliseDocumentoPrestacaoConta.RESULTADO_CORRETO
            )
        else:
            minha_analise_documento = analise_prestacao.analises_de_documento.filter(
                tipo_documento_prestacao_conta__uuid=tipo_documento_uuid,
                conta_associacao__uuid=conta_associacao_uuid
            ).first()

            minhas_solicitacoes = minha_analise_documento.solicitacoes_de_ajuste_da_analise.all()

            for solicitacao_acerto in minhas_solicitacoes:
                logging.info(f'Apagando solicitação de acerto {solicitacao_acerto.uuid}.')
                solicitacao_acerto.delete()

            minha_analise_documento.resultado = AnaliseDocumentoPrestacaoConta.RESULTADO_CORRETO
            minha_analise_documento.save()

    logging.info(f'Marcando documentos como corretos na análise de PC {analise_prestacao.uuid}.')
    for documento in documentos_corretos:
        marca_documento_correto(
            tipo_documento_uuid=documento['tipo_documento'],
            conta_associacao_uuid=documento['conta_associacao']
        )


def marca_documentos_como_nao_conferidos(analise_prestacao, documentos_nao_conferidos):
    def marca_documento_nao_conferido(tipo_documento_uuid, conta_associacao_uuid=None):
        logging.info(
            f'Apagando analise de documento {tipo_documento_uuid} conta {conta_associacao_uuid} na análise de PC {analise_prestacao.uuid}.')
        analise_prestacao.analises_de_documento.filter(
            tipo_documento_prestacao_conta__uuid=tipo_documento_uuid,
            conta_associacao__uuid=conta_associacao_uuid
        ).delete()

    logging.info(f'Marcando documentos como não conferidos na análise de PC {analise_prestacao.uuid}.')
    for documento in documentos_nao_conferidos:
        marca_documento_nao_conferido(
            tipo_documento_uuid=documento['tipo_documento'],
            conta_associacao_uuid=documento['conta_associacao']
        )


def solicita_acertos_de_documentos(analise_prestacao, documentos, solicitacoes_acerto):
    def analisa_solicitacoes_acerto_documento(_analise_documento, _solicitacoes_acerto):
        logging.info(
            f'Verificando quais solicitações de ajustes existentes devem ser apagadas para a análise de documento {_analise_documento.uuid}.')

        keep_solicitacoes = []
        for _solicitacao_acerto in _solicitacoes_acerto:
            if _solicitacao_acerto['uuid']:
                solicitacao_encontrada = SolicitacaoAcertoDocumento.objects.get(uuid=_solicitacao_acerto['uuid'])
                if solicitacao_encontrada:
                    logging.info(f"Solicitação encontrada: {solicitacao_encontrada}")

                    # Realizando update das solicitacoes encontradas
                    solicitacao_encontrada.detalhamento = _solicitacao_acerto['detalhamento']
                    solicitacao_encontrada.save()

                    keep_solicitacoes.append(solicitacao_encontrada.uuid)
                else:
                    continue
            else:
                logging.info(f"Não encontrada chave uuid da solicitação: {_solicitacao_acerto['uuid']}. Será criado.")
                tipo_acerto = TipoAcertoDocumento.objects.get(uuid=_solicitacao_acerto['tipo_acerto'])

                _solicitacao_criada = SolicitacaoAcertoDocumento.objects.create(
                    analise_documento=_analise_documento,
                    tipo_acerto=tipo_acerto,
                    detalhamento=_solicitacao_acerto['detalhamento'],
                    status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE
                )

                logging.info(f"Solicitação criada: {_solicitacao_criada}.")
                keep_solicitacoes.append(_solicitacao_criada.uuid)

        # apagando
        for _solicitacao_existente in _analise_documento.solicitacoes_de_ajuste_da_analise.all():
            if _solicitacao_existente.uuid not in keep_solicitacoes:
                logging.info(f"A solicitação: {_solicitacao_existente} será apagada.")

                _solicitacao_existente.delete()

    def altera_status_analise_documento(_analise_prestacao, _tipo_documento, _conta=None):
        _analise_encontrada = AnaliseDocumentoPrestacaoConta.objects.filter(
            analise_prestacao_conta=_analise_prestacao,
            tipo_documento_prestacao_conta=_tipo_documento,
            conta_associacao=_conta
        ).first()

        _analise_encontrada.resultado = AnaliseDocumentoPrestacaoConta.RESULTADO_CORRETO
        _analise_encontrada.save()

    logging.info(f'Criando solicitações de acerto de documentos na análise de PC {analise_prestacao.uuid}.')

    for documento in documentos:

        tipo_documento = TipoDocumentoPrestacaoConta.by_uuid(documento['tipo_documento'])
        conta = ContaAssociacao.by_uuid(documento['conta_associacao']) if documento['conta_associacao'] else None

        analise_documento = analise_prestacao.analises_de_documento.filter(
            tipo_documento_prestacao_conta=tipo_documento,
            conta_associacao=conta
        ).first()

        if solicitacoes_acerto:
            if not analise_documento:

                analise_documento = AnaliseDocumentoPrestacaoConta.objects.create(
                    analise_prestacao_conta=analise_prestacao,
                    tipo_documento_prestacao_conta=tipo_documento,
                    conta_associacao=conta,
                    resultado=AnaliseDocumentoPrestacaoConta.RESULTADO_AJUSTE
                )
            else:
                analise_documento.resultado = AnaliseDocumentoPrestacaoConta.RESULTADO_AJUSTE
                analise_documento.save()

        analisa_solicitacoes_acerto_documento(
            _analise_documento=analise_documento,
            _solicitacoes_acerto=solicitacoes_acerto
        )

        if not solicitacoes_acerto:
            altera_status_analise_documento(
                _analise_prestacao=analise_prestacao,
                _tipo_documento=tipo_documento,
                _conta=conta
            )


def previa_prestacao_conta(associacao, periodo):
    return {
        'associacao': AssociacaoCompletoSerializer(associacao, many=False).data,
        'periodo_uuid': periodo.uuid,
        'status': 'NAO_APRESENTADA',
        'uuid': None,
        'tecnico_responsavel': None,
        'data_recebimento': None,
        'data_recebimento_apos_acertos': None,
        'devolucoes_da_prestacao': [],
        'processo_sei': '',
        'data_ultima_analise': None,
        'devolucao_ao_tesouro': '',
        'analises_de_conta_da_prestacao': [],
        'permite_analise_valores_reprogramados': None,
        'motivos_aprovacao_ressalva': [],
        'outros_motivos_aprovacao_ressalva': '',
        'motivos_reprovacao': [],
        'outros_motivos_reprovacao': '',
        'recomendacoes': '',
        'devolucoes_ao_tesouro_da_prestacao': [],
        'arquivos_referencia': [],
        'analise_atual': None,
    }


def previa_informacoes_financeiras_para_atas(associacao, periodo):
    def totaliza_info_acoes(info_acoes):
        totalizador = {
            'saldo_reprogramado': 0,
            'saldo_reprogramado_capital': 0,
            'saldo_reprogramado_custeio': 0,
            'saldo_reprogramado_livre': 0,

            'receitas_no_periodo': 0,

            'receitas_devolucao_no_periodo': 0,
            'receitas_devolucao_no_periodo_custeio': 0,
            'receitas_devolucao_no_periodo_capital': 0,
            'receitas_devolucao_no_periodo_livre': 0,

            'repasses_no_periodo': 0,
            'repasses_no_periodo_capital': 0,
            'repasses_no_periodo_custeio': 0,
            'repasses_no_periodo_livre': 0,

            'outras_receitas_no_periodo': 0,
            'outras_receitas_no_periodo_capital': 0,
            'outras_receitas_no_periodo_custeio': 0,
            'outras_receitas_no_periodo_livre': 0,

            'despesas_no_periodo': 0,
            'despesas_no_periodo_capital': 0,
            'despesas_no_periodo_custeio': 0,

            'despesas_nao_conciliadas': 0,
            'despesas_nao_conciliadas_capital': 0,
            'despesas_nao_conciliadas_custeio': 0,

            'despesas_nao_conciliadas_anteriores': 0,
            'despesas_nao_conciliadas_anteriores_capital': 0,
            'despesas_nao_conciliadas_anteriores_custeio': 0,

            'despesas_conciliadas': 0,
            'despesas_conciliadas_capital': 0,
            'despesas_conciliadas_custeio': 0,

            'receitas_nao_conciliadas': 0,
            'receitas_nao_conciliadas_capital': 0,
            'receitas_nao_conciliadas_custeio': 0,
            'receitas_nao_conciliadas_livre': 0,

            'saldo_atual_custeio': 0,
            'saldo_atual_capital': 0,
            'saldo_atual_livre': 0,
            'saldo_atual_total': 0,

            'repasses_nao_realizados_capital': 0,
            'repasses_nao_realizados_custeio': 0,
            'repasses_nao_realizados_livre': 0,

            # Saldo Atual + Despesas Não demonstradas no período + Despesas não demonstradas períodos anteriores
            'saldo_bancario_custeio': 0,
            'saldo_bancario_capital': 0,
            'saldo_bancario_livre': 0,
            'saldo_bancario_total': 0,
        }
        for info_acao in info_acoes:
            for key in totalizador.keys():
                totalizador[key] += info_acao[key]

        return totalizador

    logger.info(
        f'Get prévia de info financeiras para ata. Associacao:{associacao.uuid} Período:{periodo}')

    info_contas = []
    for conta_associacao in associacao.contas.all():

        # Faz a verificação se a conta deve ser exibida em função da sua data de inicio
        if conta_associacao.conta_criada_no_periodo_ou_periodo_anteriores(periodo=periodo):

            logger.info(f'Get prévia info financeiras por conta para a ata. Associacao:{associacao.uuid} Conta:{conta_associacao}')
            info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=associacao.uuid,
                                                          periodo=periodo,
                                                          conta=conta_associacao,
                                                          apenas_transacoes_do_periodo=True,
                                                          )

            info_acoes = [info for info in info_acoes if
                          info['saldo_reprogramado'] or info['receitas_no_periodo'] or info['despesas_no_periodo']]

            info_contas.append(
                {
                    'conta_associacao': {
                        'uuid': f'{conta_associacao.uuid}',
                        'nome': f'{conta_associacao.tipo_conta.nome}',
                        'banco_nome': f'{conta_associacao.banco_nome}',
                        'agencia': f'{conta_associacao.agencia}',
                        'numero_conta': f'{conta_associacao.numero_conta}',
                    },
                    'acoes': info_acoes,
                    'totais': totaliza_info_acoes(info_acoes),
                }
            )

    info = {
        'uuid': None,
        'contas': info_contas,
    }

    return info


class MonitoraPC:

    def __init__(self, prestacao_de_contas, usuario, associacao, status=PrestacaoConta.STATUS_EM_PROCESSAMENTO):
        # Instancia do celery
        self.app = Celery("sme_ptrf_apps")
        self.app.config_from_object("django.conf:settings", namespace="CELERY")

        self.__prestacao_de_contas = prestacao_de_contas
        self.__uuid_pc = prestacao_de_contas.uuid
        self.__usuario = usuario
        self.__associacao = associacao
        self.__status = status
        self.dispara_mensagem_inicio_monitoramento()
        self.__tempo_aguardar_conclusao_pc = Parametros.get().tempo_aguardar_conclusao_pc

        # O segundo parâmetro de set_interval, define quanto tempo (em segundos) aguardamos
        # para verificar se a PC ainda está EM_PROCESSAMENTO que vem de core/Parametro
        self.set_interval(self.verifica_status_pc, self.tempo_aguardar_conclusao_pc)

        self.t = None

    @property
    def prestacao_de_contas(self):
        return self.__prestacao_de_contas

    @property
    def uuid_prestacao_de_contas(self):
        return self.__uuid_pc

    @property
    def usuario(self):
        return self.__usuario

    @property
    def status(self):
        return self.__status

    @property
    def associacao(self):
        return self.__associacao

    @property
    def tempo_aguardar_conclusao_pc(self):
        tempo = self.__tempo_aguardar_conclusao_pc if self.__tempo_aguardar_conclusao_pc > 0 else 60
        return tempo

    def dispara_mensagem_inicio_monitoramento(self):
        logger.info(f"Monitoramento de PC: Iniciando o processo de monitoramento da PC: {self.prestacao_de_contas}")

    def verifica_status_pc(self):
        from ..services import FalhaGeracaoPcService
        pc = PrestacaoConta.objects.filter(uuid=self.uuid_prestacao_de_contas).first()

        if pc:
            periodo = pc.periodo

            if periodo:

                if pc.status == self.status:

                    try:

                        self.revoke_tasks_by_id(
                            prestacao_conta=pc
                        )

                        # Registrando falha de geracao de pc
                        registra_falha = FalhaGeracaoPcService(periodo=periodo, usuario=self.usuario, associacao=self.associacao, prestacao_de_contas=pc)
                        registra_falha.registra_falha_geracao_pc()

                        ultima_analise = pc.analises_da_prestacao.last()

                        if ultima_analise:
                            pc.status = PrestacaoConta.STATUS_DEVOLVIDA
                            pc.save()
                            logger.info(
                                f"Monitoramento de PC: Prestação de contas passada para status DEVOLVIDA com sucesso.")
                        else:
                            reaberta = reabrir_prestacao_de_contas(self.uuid_prestacao_de_contas)

                            if reaberta:
                                logger.info(
                                    f"Monitoramento de PC: Prestação de contas reaberta com sucesso. Todos os seus "
                                    f"registros foram apagados.")
                            else:
                                logger.info(
                                    f"Monitoramento de PC: Houve algum erro ao tentar reabrir a prestação de contas.")

                    except Exception as e:
                        logger.info(f"Monitoramento de PC: Houve algum erro ao no processo de monitoramento de PC. {e}")

        if self.t:
            self.t.cancel()

    def set_interval(self, func, sec):
        pc = PrestacaoConta.objects.filter(uuid=self.uuid_prestacao_de_contas).first()

        if pc:
            periodo = pc.periodo

            if periodo:
                import threading

                self.t = threading.Timer(sec, func)
                self.t.start()

    def revoke_tasks_by_id(self, prestacao_conta):
        """
        Revoke one task by the id of the celery task
        :param prestacao_conta: PC of the celery task
        :return: None
        Examples:
            revoke_tasks_by_id(
                prestacao_conta=Object
            )
        """

        tasks_ativas_dessa_pc = prestacao_conta.tasks_celery_da_prestacao_conta.filter(
            nome_task='concluir_prestacao_de_contas_async').filter(finalizada=False).all()
        for task in tasks_ativas_dessa_pc:
            logger.info(f'Revoking: {task}')
            self.app.control.revoke(task_id=task.id_task_assincrona, terminate=True)
            task.registra_data_hora_finalizacao_forcada(log="Finalização forçada pela falha de PC.")
