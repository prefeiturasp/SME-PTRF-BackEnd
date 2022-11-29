import logging

from .periodo_services import status_prestacao_conta_associacao
from django.db.models import Q
from django.core.exceptions import ValidationError
from sme_ptrf_apps.core.choices import MembroEnum
from sme_ptrf_apps.receitas.models.repasse import Repasse, StatusRepasse
from ..models import PrestacaoConta, Associacao, SolicitacaoAcertoDocumento
from ...despesas.models import Despesa
from datetime import datetime

logger = logging.getLogger(__name__)


def retorna_despesas_com_pagamento_antecipado_por_periodo(associacao, periodo):
    data_inicio_realizacao_despesas = periodo.data_inicio_realizacao_despesas
    data_fim_realizacao_despesas = periodo.data_fim_realizacao_despesas

    if data_fim_realizacao_despesas:
        despesas = Despesa.objects.filter(
            Q(associacao=associacao) &
            Q(data_documento__gte=data_inicio_realizacao_despesas) &
            Q(data_documento__lte=data_fim_realizacao_despesas) &
            Q(data_transacao__gte=data_inicio_realizacao_despesas) &
            Q(data_transacao__lte=data_fim_realizacao_despesas)
        )
    else:
        despesas = Despesa.objects.filter(
            Q(associacao=associacao) &
            Q(data_documento__gte=data_inicio_realizacao_despesas) &
            Q(data_transacao__gte=data_inicio_realizacao_despesas)
        )

    despesas_com_pagamento_antecipado = []
    for despesa in despesas:

        if despesa.data_transacao < despesa.data_documento and not despesa.despesa_geradora_do_imposto.first():

            motivos = [{"motivo": motivo.motivo} for motivo in despesa.motivos_pagamento_antecipado.all()]

            despesas_com_pagamento_antecipado.append(
                {
                    "nome_fornecedor": despesa.nome_fornecedor,
                    "cpf_cnpj_fornecedor": despesa.cpf_cnpj_fornecedor,
                    "tipo_documento": despesa.tipo_documento.nome if despesa and despesa.tipo_documento and despesa.tipo_documento.nome else "",
                    "numero_documento": despesa.numero_documento,
                    "data_documento": formata_data(despesa.data_documento),
                    "tipo_transacao": despesa.tipo_transacao.nome if despesa and despesa.tipo_transacao and despesa.tipo_transacao.nome else "",
                    "data_transacao": formata_data(despesa.data_transacao),
                    "valor_total": despesa.valor_total,
                    "motivos_pagamento_antecipado": motivos,
                    "outros_motivos_pagamento_antecipado": despesa.outros_motivos_pagamento_antecipado,
                })

    return despesas_com_pagamento_antecipado


def retorna_repasses_pendentes_periodos_ate_agora(associacao, periodo):
    repasses = Repasse.objects.filter(
        associacao=associacao,
        periodo__referencia__lte=periodo.referencia,
        status=StatusRepasse.PENDENTE.name
    )

    resultado = []
    for repasse in repasses:
        resultado.append(
            {
                'repasse_periodo': repasse.periodo.referencia,
                'repasse_acao': repasse.acao_associacao.acao.nome,
                'repasse_total': repasse.valor_capital + repasse.valor_custeio + repasse.valor_livre,
            }
        )

    return resultado


def tem_repasses_pendentes_periodos_ate_agora(associacao, periodo):
    repasses_pendentes = Repasse.objects.filter(
        associacao=associacao,
        periodo__referencia__lte=periodo.referencia,
        status=StatusRepasse.PENDENTE.name
    )
    return repasses_pendentes.exists()


def retorna_se_pode_habilitar_botao_ver_acertos_em_analise_da_dre(periodo, associacao_uuid):
    associacao = Associacao.by_uuid(associacao_uuid)

    tem_solicitacoes_de_ajustes_extratos_bancarios = PrestacaoConta.objects.filter(
        periodo=periodo,
        associacao=associacao,
        analises_da_prestacao__analises_de_extratos__isnull=False
    ).count()

    tem_solicitacoes_de_ajustes_lancamentos = PrestacaoConta.objects.filter(
        periodo=periodo,
        associacao=associacao,
        analises_da_prestacao__analises_de_lancamentos__solicitacoes_de_ajuste_da_analise__isnull=False
    ).count()

    tem_solicitacoes_de_ajustes_documentos = PrestacaoConta.objects.filter(
        periodo=periodo,
        associacao=associacao,
        analises_da_prestacao__analises_de_documento__solicitacoes_de_ajuste_da_analise__isnull=False
    ).count()

    total_ajustes = tem_solicitacoes_de_ajustes_lancamentos + tem_solicitacoes_de_ajustes_documentos + \
        tem_solicitacoes_de_ajustes_extratos_bancarios

    return total_ajustes > 0


def retorna_status_prestacoes(periodos=None, status_pc=None, uuid=None):
    lista_de_periodos = []
    if periodos:
        for periodo in periodos:
            prestacao_conta_status = status_prestacao_conta_associacao(periodo_uuid=periodo.uuid, associacao_uuid=uuid)

            obj_periodo = {
                'referencia': periodo.referencia,
                'data_inicio_realizacao_despesas': periodo.data_inicio_realizacao_despesas,
                'data_fim_realizacao_despesas': periodo.data_fim_realizacao_despesas,
                'status_pc': prestacao_conta_status['status_prestacao'],
                'texto_status': prestacao_conta_status['texto_status'],
                'legenda_cor': prestacao_conta_status['legenda_cor'],
                'prestacao_de_contas_uuid': prestacao_conta_status['prestacao_de_contas_uuid'],
                'pode_habilitar_botao_ver_acertos_em_analise_da_dre': retorna_se_pode_habilitar_botao_ver_acertos_em_analise_da_dre(periodo=periodo, associacao_uuid=uuid),
            }

            lista_de_periodos.append(obj_periodo)

        if status_pc:
            lista_de_periodos = list(filter(lambda d: d['status_pc'] == status_pc, lista_de_periodos))

        return lista_de_periodos


def get_status_presidente(associacao):
    status_presidente = associacao.status_presidente if associacao else ""
    cargo_substituto_presidente_ausente = associacao.cargo_substituto_presidente_ausente if associacao else ""
    cargo_substituto_presidente_ausente_value = ""
    if associacao and associacao.cargo_substituto_presidente_ausente:
        cargo_substituto_presidente_ausente_value = MembroEnum[associacao.cargo_substituto_presidente_ausente].value

    logger.info(
        f'Status presidente: {status_presidente} Cargo substituto: {cargo_substituto_presidente_ausente}, {cargo_substituto_presidente_ausente_value}')

    result = {
        'status_presidente': status_presidente,
        'cargo_substituto_presidente_ausente': cargo_substituto_presidente_ausente,
        'cargo_substituto_presidente_ausente_value': cargo_substituto_presidente_ausente_value
    }

    return result


def update_status_presidente(associacao, status_presidente, cargo_substituto_presidente_ausente):
    if not status_presidente or status_presidente not in ['PRESENTE', 'AUSENTE']:
        result_error = {
            'erro': 'campo_requerido',
            'mensagem': 'É necessário enviar no payload um staus_presidente válido [PRESENTE|AUSENTE]. '
        }
        raise ValidationError(result_error)

    if status_presidente == 'AUSENTE' and not cargo_diretoria_executiva_valido(cargo_substituto_presidente_ausente):
        result_error = {
            'erro': 'campo_requerido',
            'mensagem': 'É necessário enviar no payload um cargo_substituto_presidente_ausente válido.'
        }
        raise ValidationError(result_error)

    associacao.status_presidente = status_presidente
    associacao.cargo_substituto_presidente_ausente = cargo_substituto_presidente_ausente
    associacao.save()

    result = {
        'status_presidente': associacao.status_presidente,
        'cargo_substituto_presidente_ausente': associacao.cargo_substituto_presidente_ausente,
    }

    return result


def cargo_diretoria_executiva_valido(cargo):
    from sme_ptrf_apps.core.choices.membro_associacao import MembroEnum
    cargos_diretoria_executiva = [key[0] for key in MembroEnum.diretoria_executiva_choices()]
    return cargo in cargos_diretoria_executiva


def associacao_pode_implantar_saldo(associacao):
    result = None

    periodo_primeira_pc = associacao.periodo_inicial.proximo_periodo if associacao.periodo_inicial else None

    if not associacao.periodo_inicial:
        result = {
            'permite_implantacao': False,
            'erro': 'periodo_inicial_nao_definido',
            'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.'
        }

    if associacao.prestacoes_de_conta_da_associacao.exists():
        if not associacao.prestacoes_de_conta_da_associacao.filter(
            Q(periodo=periodo_primeira_pc) & Q(status='DEVOLVIDA')
        ).exists():
            result = {
                'permite_implantacao': False,
                'erro': 'prestacao_de_contas_nao-encontrada',
                'mensagem': 'Os saldos não podem ser implantados, não existe uma prestação de contas do periodo inicial'
                            ' e devolivida.'
            }

    if not result:
        result = {
            'permite_implantacao': True,
            'erro': '',
            'mensagem': 'Os saldos podem ser implantados normalmente.'
        }

    return result


def get_implantacao_de_saldos_da_associacao(associacao):
    from rest_framework import status
    from .implantacao_saldos_services import implantacoes_de_saldo_da_associacao
    from ..api.serializers import (AcaoAssociacaoLookUpSerializer,
                                   ContaAssociacaoLookUpSerializer,
                                   PeriodoLookUpSerializer)

    periodo_primeira_pc = associacao.periodo_inicial.proximo_periodo if associacao.periodo_inicial else None

    if not associacao.periodo_inicial:
        erro = {
            'erro': 'periodo_inicial_nao_definido',
            'mensagem': 'Período inicial não foi definido para essa associação. Verifique com o administrador.'
        }
        return {
            'conteudo': erro,
            'status_code': status.HTTP_400_BAD_REQUEST
        }

    if associacao.prestacoes_de_conta_da_associacao.exists():
        if not associacao.prestacoes_de_conta_da_associacao.filter(
            Q(periodo=periodo_primeira_pc) & Q(status='DEVOLVIDA')
        ).exists():
            erro = {
                'erro': 'prestacao_de_contas_nao-encontrada',
                'mensagem': 'Os saldos não podem ser implantados, não existe uma prestação de contas do periodo inicial'
                            ' e devolivida.'
            }
            return {
                'conteudo': erro,
                'status_code': status.HTTP_400_BAD_REQUEST
            }

    saldos = []
    implantacoes = implantacoes_de_saldo_da_associacao(associacao=associacao)
    for implantacao in implantacoes:
        saldo = {
            'acao_associacao': AcaoAssociacaoLookUpSerializer(implantacao['acao_associacao']).data,
            'conta_associacao': ContaAssociacaoLookUpSerializer(implantacao['conta_associacao']).data,
            'aplicacao': implantacao['aplicacao'],
            'saldo': implantacao['saldo'],
            "status": associacao.status_valores_reprogramados
        }
        saldos.append(saldo)

    result = {
        'associacao': f'{associacao.uuid}',
        'periodo': PeriodoLookUpSerializer(associacao.periodo_inicial).data,
        'saldos': saldos,
    }

    return {
        'conteudo': result,
        'status_code': status.HTTP_200_OK
    }


def formata_data(data):
    data_formatada = " - "
    if data:
        d = datetime.strptime(str(data), '%Y-%m-%d')
        data_formatada = d.strftime("%d/%m/%Y")

    return f'{data_formatada}'
