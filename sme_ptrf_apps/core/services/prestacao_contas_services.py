import logging

from django.db import transaction
from django.db.models import Q, Sum

from .demonstrativo_financeiro_xlsx_service import (gerar_arquivo_demonstrativo_financeiro_xlsx,
                                                    apagar_previas_demonstrativo_financeiro)
from ..models import (
    PrestacaoConta,
    FechamentoPeriodo,
    Associacao,
    DemonstrativoFinanceiro,
    ObservacaoConciliacao,
    AnaliseLancamentoPrestacaoConta,
    SolicitacaoAcertoLancamento,
    TipoAcertoLancamento,
    DevolucaoAoTesouro,
    TipoDevolucaoAoTesouro,
    TipoDocumentoPrestacaoConta,
    AnaliseDocumentoPrestacaoConta,
    ContaAssociacao,
    TipoAcertoDocumento,
    SolicitacaoAcertoDocumento
)
from ..services import info_acoes_associacao_no_periodo
from ..services.relacao_bens import gerar_arquivo_relacao_de_bens, apagar_previas_relacao_de_bens
from ..services.processos_services import get_processo_sei_da_prestacao
from ...despesas.models import RateioDespesa, Despesa
from ...receitas.models import Receita
from ..tasks import concluir_prestacao_de_contas_async, gerar_previa_demonstrativo_financeiro_async

from ..services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro
from .demonstrativo_financeiro_pdf_service import gerar_arquivo_demonstrativo_financeiro_pdf

from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO

logger = logging.getLogger(__name__)


@transaction.atomic
def concluir_prestacao_de_contas(periodo, associacao, usuario=""):
    prestacao = PrestacaoConta.abrir(periodo=periodo, associacao=associacao)
    logger.info(f'Aberta a prestação de contas {prestacao}.')

    e_retorno_devolucao = prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA

    prestacao.em_processamento()
    logger.info(f'Prestação de contas em processamento {prestacao}.')
    concluir_prestacao_de_contas_async.delay(
        periodo.uuid,
        associacao.uuid,
        usuario=usuario,
        e_retorno_devolucao=e_retorno_devolucao
    )

    return prestacao


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
            'repasses_nao_realizados_livre': 0
        }
        for info_acao in info_acoes:
            for key in totalizador.keys():
                totalizador[key] += info_acao[key]

        return totalizador

    logger.info(
        f'Get info financeiras para ata. Associacao:{prestacao_contas.associacao.uuid} Período:{prestacao_contas.periodo}')

    info_contas = []
    for conta_associacao in prestacao_contas.associacao.contas.all():
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
    associacoes_da_dre = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').order_by(
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

        info_prestacao = {
            'periodo_uuid': f'{periodo.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': None,
            'processo_sei': get_processo_sei_da_prestacao(prestacao_contas=prestacao_conta) if prestacao_conta else '',
            'status': prestacao_conta.status if prestacao_conta else PrestacaoConta.STATUS_NAO_APRESENTADA,
            'tecnico_responsavel': '',
            'unidade_eol': associacao.unidade.codigo_eol,
            'unidade_nome': associacao.unidade.nome,
            'unidade_tipo_unidade': associacao.unidade.tipo_unidade,
            'uuid': f'{prestacao_conta.uuid}' if prestacao_conta else '',
            'associacao_uuid': f'{associacao.uuid}',
            'devolucao_ao_tesouro': '0,00'
        }

        prestacoes.append(info_prestacao)

    return prestacoes


def lista_prestacoes_de_conta_todos_os_status(
    dre,
    periodo,
    filtro_nome=None,
    filtro_tipo_unidade=None,
    filtro_por_status=[]
):
    associacoes_da_dre = Associacao.objects.filter(unidade__dre=dre).exclude(cnpj__exact='').order_by(
        'unidade__tipo_unidade', 'unidade__nome')

    if filtro_nome is not None:
        associacoes_da_dre = associacoes_da_dre.filter(Q(nome__unaccent__icontains=filtro_nome) | Q(
            unidade__nome__unaccent__icontains=filtro_nome))

    if filtro_tipo_unidade is not None:
        associacoes_da_dre = associacoes_da_dre.filter(unidade__tipo_unidade=filtro_tipo_unidade)

    prestacoes = []
    for associacao in associacoes_da_dre:
        prestacao_conta = PrestacaoConta.objects.filter(associacao=associacao, periodo=periodo).first()

        if filtro_por_status and not prestacao_conta and PrestacaoConta.STATUS_NAO_APRESENTADA not in filtro_por_status:
            # Pula PCs não apresentadas se existir um filtro por status e não contiver o status não apresentada
            continue

        if filtro_por_status and prestacao_conta and prestacao_conta.status not in filtro_por_status:
            # Pula PCs apresentadas se existir um filtro por status e não contiver o status da PC
            continue

        info_prestacao = {
            'periodo_uuid': f'{periodo.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': None,
            'processo_sei': get_processo_sei_da_prestacao(prestacao_contas=prestacao_conta) if prestacao_conta else '',
            'status': prestacao_conta.status if prestacao_conta else PrestacaoConta.STATUS_NAO_APRESENTADA,
            'tecnico_responsavel': '',
            'unidade_eol': associacao.unidade.codigo_eol,
            'unidade_nome': associacao.unidade.nome,
            'unidade_tipo_unidade': associacao.unidade.tipo_unidade,
            'uuid': f'{prestacao_conta.uuid}' if prestacao_conta else '',
            'associacao_uuid': f'{associacao.uuid}',
            'devolucao_ao_tesouro': '0,00'
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

    logger.info(f'Gerando demonstrativo financeiro em XLSX da conta {conta_associacao}.')

    try:
        observacao_conciliacao = ObservacaoConciliacao.objects.get(periodo__uuid=periodo.uuid, conta_associacao__uuid=conta_associacao.uuid)
    except Exception:
        observacao_conciliacao = None

    if criar_arquivos:
        demonstrativo = gerar_arquivo_demonstrativo_financeiro_xlsx(acoes=acoes, periodo=periodo,
                                                                    conta_associacao=conta_associacao,
                                                                    prestacao=prestacao,
                                                                    previa=previa,
                                                                    demonstrativo_financeiro=demonstrativo,
                                                                    observacao_conciliacao=observacao_conciliacao,
                                                                    )

    logger.info(f'Gerando demonstrativo financeiro em PDF da conta {conta_associacao}.')
    dados_demonstrativo = gerar_dados_demonstrativo_financeiro(usuario, acoes, periodo, conta_associacao,
                                                               prestacao, observacao_conciliacao=observacao_conciliacao,
                                                               previa=previa)

    if criar_arquivos:
        gerar_arquivo_demonstrativo_financeiro_pdf(dados_demonstrativo, demonstrativo)

    demonstrativo.arquivo_concluido()

    return demonstrativo


def tem_solicitacao_acerto_do_tipo(analise_lancamento, tipo_acerto):
    return analise_lancamento.solicitacoes_de_ajuste_da_analise.filter(tipo_acerto=tipo_acerto).exists()


def lancamentos_da_prestacao(
    analise_prestacao_conta,
    conta_associacao,
    acao_associacao=None,
    tipo_transacao=None,
    tipo_acerto=None,
    com_ajustes=False,
):
    from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaDocumentoMestreSerializer
    from sme_ptrf_apps.despesas.api.serializers.rateio_despesa_serializer import RateioDespesaConciliacaoSerializer
    from sme_ptrf_apps.receitas.api.serializers.receita_serializer import ReceitaConciliacaoSerializer
    from sme_ptrf_apps.core.api.serializers.analise_lancamento_prestacao_conta_serializer import AnaliseLancamentoPrestacaoContaRetrieveSerializer

    def documentos_de_despesa_por_conta_e_acao_no_periodo(conta_associacao, acao_associacao, periodo):
        rateios = RateioDespesa.rateios_da_conta_associacao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=periodo
        )
        despesas_com_rateios = rateios.values_list('despesa__id', flat=True).distinct()

        dataset = Despesa.completas.filter(id__in=despesas_com_rateios)

        return dataset.all()

    receitas = []
    despesas = []

    prestacao_conta = analise_prestacao_conta.prestacao_conta

    if not tipo_transacao or tipo_transacao == "CREDITOS":
        receitas = Receita.receitas_da_conta_associacao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=prestacao_conta.periodo
        )

        receitas = receitas.order_by("data")

    if not tipo_transacao or tipo_transacao == "GASTOS":
        despesas = documentos_de_despesa_por_conta_e_acao_no_periodo(
            conta_associacao=conta_associacao,
            acao_associacao=acao_associacao,
            periodo=prestacao_conta.periodo
        )

        despesas = despesas.order_by("data_transacao")

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

        lancamento = {
            'periodo': f'{prestacao_conta.periodo.uuid}',
            'conta': f'{conta_associacao.uuid}',
            'data': despesa.data_transacao,
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
                despesa.rateios.filter(status=STATUS_COMPLETO).filter(conta_associacao=conta_associacao).order_by('id'),
                many=True).data,
            'notificar_dias_nao_conferido': max_notificar_dias_nao_conferido,
            'analise_lancamento': {'resultado': analise_lancamento.resultado,
                                   'uuid': analise_lancamento.uuid} if analise_lancamento else None
        }

        if com_ajustes:
            lancamento['analise_lancamento'] = AnaliseLancamentoPrestacaoContaRetrieveSerializer(analise_lancamento,
                                                                                                 many=False).data
        else:
            lancamento['analise_lancamento'] = {'resultado': analise_lancamento.resultado,
                                                'uuid': analise_lancamento.uuid} if analise_lancamento else None

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
                                   'uuid': analise_lancamento.uuid} if analise_lancamento else None
        }

        if com_ajustes:
            novo_lancamento['analise_lancamento'] = AnaliseLancamentoPrestacaoContaRetrieveSerializer(
                analise_lancamento,
                many=False).data
        else:
            novo_lancamento['analise_lancamento'] = {'resultado': analise_lancamento.resultado,
                                                     'uuid': analise_lancamento.uuid} if analise_lancamento else None

        lancamento_adicionado = False

        if lancamentos:
            for idx, lancamento in enumerate(lancamentos):
                if novo_lancamento['data'] <= lancamento['data']:
                    lancamentos.insert(idx, novo_lancamento)
                    lancamento_adicionado = True
                    break

        if not lancamento_adicionado:
            lancamentos.append(novo_lancamento)

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

    logging.info(f'Marcando lançamento como corretos na análise de PC {analise_prestacao.uuid}.')
    for lancamento in lancamentos_corretos:
        if lancamento["tipo_lancamento"] == 'CREDITO':
            marca_credito_correto(credito_uuid=lancamento["lancamento"])
        else:
            marca_gasto_correto(gasto_uuid=lancamento["lancamento"])


def marca_lancamentos_como_nao_conferidos(analise_prestacao, lancamentos_nao_conferidos):
    def marca_credito_nao_conferido(credito_uuid):
        logging.info(f'Apagando analise de lançamento do crédito {credito_uuid} na análise de PC {analise_prestacao.uuid}.')
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


def __apaga_analise_lancamento(analise_prestacao, lancamento):
    if lancamento['tipo_lancamento'] == 'CREDITO':
        AnaliseLancamentoPrestacaoConta.objects.filter(
            analise_prestacao_conta=analise_prestacao,
            receita__uuid=lancamento['lancamento_uuid']
        ).delete()
    else:
        AnaliseLancamentoPrestacaoConta.objects.filter(
            analise_prestacao_conta=analise_prestacao,
            despesa__uuid=lancamento['lancamento_uuid']
        ).delete()


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


def __cria_solicitacao_acerto(analise_lancamento, solicitacao_acerto):
    tipo_acerto = TipoAcertoLancamento.objects.get(uuid=solicitacao_acerto['tipo_acerto'])

    devolucao_tesouro = None
    if analise_lancamento.tipo_lancamento == 'GASTO' and solicitacao_acerto['devolucao_tesouro']:
        logging.info(f'Criando devolução ao tesouro para a análise de lançamento {analise_lancamento.uuid}.')
        devolucao_tesouro = DevolucaoAoTesouro.objects.create(
            prestacao_conta=analise_lancamento.analise_prestacao_conta.prestacao_conta,
            tipo=TipoDevolucaoAoTesouro.objects.get(uuid=solicitacao_acerto['devolucao_tesouro']['tipo']),
            data=solicitacao_acerto['devolucao_tesouro']['data'],
            despesa=analise_lancamento.despesa,
            devolucao_total=solicitacao_acerto['devolucao_tesouro']['devolucao_total'],
            valor=solicitacao_acerto['devolucao_tesouro']['valor'],
            motivo=solicitacao_acerto['detalhamento']
        )

    if not solicitacao_acerto['devolucao_tesouro'] or analise_lancamento.tipo_lancamento == 'GASTO':
        # Apenas lançamentos do tipo gasto recebem ajustes de devolução ao tesouro
        logging.info(f'Criando solicitação de acerto para a análise de lançamento {analise_lancamento.uuid}.')
        SolicitacaoAcertoLancamento.objects.create(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto,
            devolucao_ao_tesouro=devolucao_tesouro,
            detalhamento=solicitacao_acerto['detalhamento']
        )


def __apaga_solicitacoes_acerto_lancamento(analise_lancamento):
    logging.info(f'Apagando solicitações de ajustes existentes para a análise de lançamento {analise_lancamento.uuid}.')
    for solicitacao_acerto in analise_lancamento.solicitacoes_de_ajuste_da_analise.all():
        devolucao_ao_tesouro = solicitacao_acerto.devolucao_ao_tesouro

        logging.info(f'Apagando solicitação de acerto {solicitacao_acerto.uuid}.')
        solicitacao_acerto.delete()

        if devolucao_ao_tesouro:
            logging.info(f'Apagando devolução ao tesouro {devolucao_ao_tesouro.uuid}.')
            devolucao_ao_tesouro.delete()


def __atualiza_analise_lancamento_para_acerto(analise_lancamento):
    if analise_lancamento.resultado != AnaliseLancamentoPrestacaoConta.RESULTADO_AJUSTE:
        analise_lancamento.resultado = AnaliseLancamentoPrestacaoConta.RESULTADO_AJUSTE
        analise_lancamento.save()
    return analise_lancamento


def solicita_acertos_de_lancamentos(analise_prestacao, lancamentos, solicitacoes_acerto):
    atualizacao_em_lote = len(lancamentos) > 1
    logging.info(f'Criando solicitações de acerto na análise de PC {analise_prestacao.uuid}. em_lote={atualizacao_em_lote}')

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

        if not atualizacao_em_lote:
            __apaga_solicitacoes_acerto_lancamento(analise_lancamento=analise_lancamento)

        for solicitacao in solicitacoes_acerto:
            __cria_solicitacao_acerto(analise_lancamento=analise_lancamento, solicitacao_acerto=solicitacao)

        if not atualizacao_em_lote and not solicitacoes_acerto:
            __apaga_analise_lancamento(analise_prestacao=analise_prestacao, lancamento=lancamento)


def documentos_da_prestacao(analise_prestacao_conta):
    from ..models import TipoDocumentoPrestacaoConta, ContaAssociacao

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
            for conta in associacao.contas.all().order_by('id'):
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

    logging.info(f'Marcando documentos como corretos na análise de PC {analise_prestacao.uuid}.')
    for documento in documentos_corretos:
        marca_documento_correto(
            tipo_documento_uuid=documento['tipo_documento'],
            conta_associacao_uuid=documento['conta_associacao']
        )


def marca_documentos_como_nao_conferidos(analise_prestacao, documentos_nao_conferidos):
    def marca_documento_nao_conferido(tipo_documento_uuid, conta_associacao_uuid=None):
        logging.info(f'Apagando analise de documento {tipo_documento_uuid} conta {conta_associacao_uuid} na análise de PC {analise_prestacao.uuid}.')
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

    def apaga_solicitacoes_acerto_documento(_analise_documento):
        logging.info(
            f'Apagando solicitações de ajustes existentes para a análise de documento {analise_documento.uuid}.')
        for solicitacao_acerto in _analise_documento.solicitacoes_de_ajuste_da_analise.all():
            logging.info(f'Apagando solicitação de acerto de dodcumento {solicitacao_acerto.uuid}.')
            solicitacao_acerto.delete()

    def cria_solicitacoes_acerto_documento(_analise_documento, _solicitacoes_acerto):
        for _solicitacao_acerto in _solicitacoes_acerto:
            logging.info(f'Criando solicitação de acerto para a análise de documento {_analise_documento.uuid}.')
            tipo_acerto = TipoAcertoDocumento.objects.get(uuid=_solicitacao_acerto['tipo_acerto'])
            SolicitacaoAcertoDocumento.objects.create(
                analise_documento=_analise_documento,
                tipo_acerto=tipo_acerto,
                detalhamento=_solicitacao_acerto['detalhamento']
            )

    def apaga_analise_documento(_analise_prestacao, _tipo_documento, _conta=None):
        AnaliseDocumentoPrestacaoConta.objects.filter(
            analise_prestacao_conta=_analise_prestacao,
            tipo_documento_prestacao_conta=_tipo_documento,
            conta_associacao=_conta
        ).delete()

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

        apaga_solicitacoes_acerto_documento(_analise_documento=analise_documento)

        cria_solicitacoes_acerto_documento(
            _analise_documento=analise_documento,
            _solicitacoes_acerto=solicitacoes_acerto
        )

        if not solicitacoes_acerto:
            apaga_analise_documento(_analise_prestacao=analise_prestacao, _tipo_documento=tipo_documento, _conta=conta)
