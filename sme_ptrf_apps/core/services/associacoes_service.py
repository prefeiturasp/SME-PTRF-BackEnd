import logging
from rest_framework import status
from .periodo_services import status_prestacao_conta_associacao
from django.db.models import Q
from django.core.exceptions import ValidationError
from sme_ptrf_apps.core.choices import MembroEnum
from sme_ptrf_apps.receitas.models.repasse import Repasse, StatusRepasse
from ..models import PrestacaoConta, Associacao, SolicitacaoAcertoDocumento, FechamentoPeriodo
from ...despesas.models import Despesa
import datetime

from ...receitas.models import Receita

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
        d = datetime.datetime.strptime(str(data), '%Y-%m-%d')
        data_formatada = d.strftime("%d/%m/%Y")

    return f'{data_formatada}'


class AssociacaoService:

    def __init__(self, associacao):
        self.__associacao = associacao


    @property
    def associacao(self):
        return self.__associacao



class ValidaDataDeEncerramento(AssociacaoService):
    def __init__(self, associacao, data_de_encerramento, periodo_inicial=None):
        super().__init__(associacao)
        self.__data_de_encerramento = data_de_encerramento
        self.__periodo_inicial = periodo_inicial
        self.despesas = None
        self.receitas = None
        self.prestacoes = None
        self.fechamentos = None
        self.data_inicio_realizacao_despesas = None
        self.data_fim_realizacao_despesas = None
        self.__set_response()


    @property
    def data_de_encerramento(self):
        return self.__data_de_encerramento

    @property
    def periodo_inicial(self):
        return self.__periodo_inicial

    def retorna_se_tem_despesa(self):
        return Despesa.objects.filter(
                Q(status="COMPLETO") &
                Q(data_e_hora_de_inativacao__isnull=True) &
                Q(associacao=self.associacao) &
                Q(data_transacao__gte=self.data_inicio_realizacao_despesas)
            ).exists()

    def retorna_se_tem_receita(self):
        return Receita.objects.filter(
                Q(status="COMPLETO") &
                Q(associacao=self.associacao) &
                Q(data__gte=self.data_inicio_realizacao_despesas)
            ).exists()

    def retorna_se_tem_pc(self):
        return PrestacaoConta.objects.filter(
                associacao=self.associacao,
                periodo__data_inicio_realizacao_despesas__gte=self.data_inicio_realizacao_despesas,
                status__in=[PrestacaoConta.STATUS_APROVADA,
                            PrestacaoConta.STATUS_APROVADA_RESSALVA,
                            PrestacaoConta.STATUS_REPROVADA]
            ).exists()

    def retorna_se_tem_fechamento(self):
        return FechamentoPeriodo.objects.filter(
                associacao=self.associacao,
                periodo__data_inicio_realizacao_despesas__gte=self.data_inicio_realizacao_despesas,
            ).exists()


    def __set_response(self):
        self.response = {
            'erro': 'data_valida',
            'mensagem': 'Data de encerramento válida',
            "status": status.HTTP_200_OK,
        }

        if self.periodo_inicial:
            self.data_inicio_realizacao_despesas = self.periodo_inicial.data_inicio_realizacao_despesas if self.periodo_inicial.data_inicio_realizacao_despesas else None
            self.data_fim_realizacao_despesas = self.periodo_inicial.data_fim_realizacao_despesas if self.periodo_inicial.data_fim_realizacao_despesas else None
        else:
            self.data_inicio_realizacao_despesas = self.associacao.periodo_inicial.data_inicio_realizacao_despesas if self.associacao.periodo_inicial and self.associacao.periodo_inicial.data_inicio_realizacao_despesas else None
            self.data_fim_realizacao_despesas = self.associacao.periodo_inicial.data_fim_realizacao_despesas if self.associacao.periodo_inicial and self.associacao.periodo_inicial.data_fim_realizacao_despesas else None

        if self.data_de_encerramento and self.data_de_encerramento > datetime.date.today():
            self.response = {
                'erro': 'data_invalida',
                'mensagem': 'Data de encerramento não pode ser maior que a data de Hoje',
                "status": status.HTTP_400_BAD_REQUEST,
            }
            return

        if self.data_fim_realizacao_despesas and self.data_de_encerramento and self.data_de_encerramento < self.data_fim_realizacao_despesas:
            self.response = {
                'erro': 'data_invalida',
                'mensagem': 'Data de encerramento não pode ser menor que data_fim_realizacao_despesas do período inicial',
                "status": status.HTTP_400_BAD_REQUEST,
            }
            return

        if self.data_inicio_realizacao_despesas:
            self.despesas = self.retorna_se_tem_despesa()

            self.receitas = self.retorna_se_tem_receita()

            self.prestacoes = self.retorna_se_tem_pc()

            self.fechamentos = self.retorna_se_tem_fechamento()

        if self.despesas or self.receitas:
            self.response = {
                'erro': 'data_invalida',
                'mensagem': 'Existem movimentações cadastradas após a data informada. Favor alterar a data das movimentações ou a data do encerramento.',
                "status": status.HTTP_400_BAD_REQUEST,
            }
            return


class ValidaSePodeEditarPeriodoInicial(AssociacaoService):
    def __init__(self, associacao):
        super().__init__(associacao)
        self.despesas = None
        self.receitas = None
        self.prestacoes = None
        self.__set_response()

    def retorna_se_tem_despesa(self):
        return Despesa.objects.filter(
                Q(status="COMPLETO") &
                Q(data_e_hora_de_inativacao__isnull=True) &
                Q(associacao=self.associacao) &
                Q(data_transacao__gte=self.data_inicio_realizacao_despesas)
            ).exists()

    def retorna_se_tem_receita(self):
        return Receita.objects.filter(
                Q(status="COMPLETO") &
                Q(associacao=self.associacao) &
                Q(data__gte=self.data_inicio_realizacao_despesas)
            ).exists()

    def retorna_se_tem_pc(self):
        return PrestacaoConta.objects.filter(
                associacao=self.associacao,
                periodo__data_inicio_realizacao_despesas__gte=self.data_inicio_realizacao_despesas,
                status__in=[PrestacaoConta.STATUS_APROVADA,
                            PrestacaoConta.STATUS_APROVADA_RESSALVA,
                            PrestacaoConta.STATUS_REPROVADA]
            ).exists()


    def __set_response(self):
        self.response = {
            "pode_editar_periodo_inicial": True,
            "mensagem_pode_editar_periodo_inicial": "",
            "help_text": "O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado.",
        }

        self.data_inicio_realizacao_despesas = self.associacao.periodo_inicial.data_inicio_realizacao_despesas if self.associacao.periodo_inicial and self.associacao.periodo_inicial.data_inicio_realizacao_despesas else None

        # TODO Removida a verificação de despesas e receitas a pedido da PO História 91682
        # if self.data_inicio_realizacao_despesas:
        #     self.despesas = self.retorna_se_tem_despesa()
        #
        #     self.receitas = self.retorna_se_tem_receita()


        if self.data_inicio_realizacao_despesas and self.retorna_se_tem_pc():
            self.response = {
                "pode_editar_periodo_inicial": False,
                "mensagem_pode_editar_periodo_inicial": "Não é permitido alterar o período inicial da Associação, pois há prestação de contas concluída após o início de uso do sistema.",
                "help_text": "O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado.",
            }
            return

        if self.associacao.status_valores_reprogramados == self.associacao.STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS:
            self.response = {
                "pode_editar_periodo_inicial": False,
                "mensagem_pode_editar_periodo_inicial": "Não é permitido alterar o período inicial da Associação, pois há valores reprogramados cadastrados conferidos como corretos no início de uso do sistema.",
                "help_text": "O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado.",
            }
            return

        # TODO Removida a verificação de despesas e receitas a pedido da PO História 91682
        # if self.despesas or self.receitas:
        #     self.response = {
        #         "pode_editar_periodo_inicial": False,
        #         "mensagem_pode_editar_periodo_inicial": "Não é permitido alterar o período inicial pois já houve movimentação após o início de uso do sistema.",
        #         "help_text": "O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado."
        #     }
        #     return

