import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from django.db import transaction, models
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
from sme_ptrf_apps.paa.services import ResumoPrioridadesService, ValidacaoSaldoIndisponivel
from sme_ptrf_apps.paa.models import (
    ReceitaPrevistaPaa,
    ReceitaPrevistaOutroRecursoPeriodo,
    ReceitaPrevistaPdde,
    RecursoProprioPaa,
)

logger = logging.getLogger(__name__)


class ConfirmarExlusaoPrioridadesPaaRecursoProprioService(Exception):
    pass


class PrioridadesPaaImpactadasBaseService(ABC):
    """
    Service para sincronizar prioridades do PAA quando Receitas Previstas PTRF, PDDE, Outros Recursos.

    Regras:
    - PAA deve estar em elaboração (status = EM_ELABORACAO)
    - Prioridades devem usar a mesma Ação(PTRF, PDDE, Outros Recursos)
    """

    def __init__(self, receita_prevista: dict, instance_receita_prevista=None):
        """
        Inicializa o serviço de prioridades do PAA com base em uma receita prevista.

        :param receita_prevista: Dados da receita prevista a ser utilizada (Dicionário recebido no serializer)
                                Necessário a sobrescrita de acordo com a instancia de Receitas previstas utilizada
                                - `self.acao_receita`
                                    Ex:
                                        - Receitas Previstas PTRF utiliza `acao_associacao`
                                        - Receitas Previstas PDDE utiliza `acao_pdde`
                                        - Receitas Previstas Outros Recursos utiliza `outro_recurso_periodo`
                                - `self.recurso`
                                    Ex:
                                        - RecursoOpcoesEnum.PTRF.name
                                        - RecursoOpcoesEnum.PDDE.name
                                        - RecursoOpcoesEnum.RECURSO_PROPRIO.name
                                        - RecursoOpcoesEnum.OUTRO_RECURSO.name

        :param instance_receita_prevista: Opcional, quando a receita prevista for um objeto existente (edição)
        """
        self.instance_receita_prevista = instance_receita_prevista  # Quando é um objeto existente (edição)
        self.receita_prevista = receita_prevista
        self.acao_receita = self.get_acao_receita()
        self.recurso = self.get_recurso()

    @abstractmethod
    def get_acao_receita(self):
        """ Necessário a sobrescrita de acordo com a instancia de Receitas previstas utilizada
            Ex:
                - Receitas Previstas PTRF utiliza `acao_associacao`
                - Receitas Previstas PDDE utiliza `acao_pdde`
                - Receitas Previstas OUTRO_RECURSO utiliza `outro_recurso_periodo`"""
        raise NotImplementedError

    @abstractmethod
    def get_recurso(self):
        """ Necessário a sobrescrita de acordo com a instancia de Receitas previstas utilizada (RecursoOpcoesEnum) """
        raise NotImplementedError

    def _get_acao_uuid_resumo_prioridade(self):
        """ Identificador utilizado no Node do resumo de prioridades """
        if isinstance(self.instance_receita_prevista, ReceitaPrevistaOutroRecursoPeriodo):
            return self.instance_receita_prevista.outro_recurso_periodo.outro_recurso.uuid

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPdde):
            return self.instance_receita_prevista.acao_pdde.uuid

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPaa):
            return self.instance_receita_prevista.acao_associacao.uuid

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return self.instance_receita_prevista.associacao.uuid

        raise NotImplementedError

    def _get_valor_custeio_edicao(self):
        """ Considera o valor de custeio acordo com a instancia de Receitas previstas utilizada """
        if isinstance(self.instance_receita_prevista, ReceitaPrevistaOutroRecursoPeriodo):
            return (
                Decimal(self.receita_prevista.get('previsao_valor_custeio')) +
                Decimal(self.receita_prevista.get('saldo_custeio'))
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPdde):
            return (
                Decimal(self.receita_prevista.get('previsao_valor_custeio')) +
                Decimal(self.receita_prevista.get('saldo_custeio'))
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPaa):
            return Decimal(self.receita_prevista.get('previsao_valor_custeio'))

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return 0

        raise NotImplementedError

    def _get_valor_custeio_atual(self):
        """ Considera o valor de custeio de acordo com a instancia de Receitas previstas utilizada """
        if isinstance(self.instance_receita_prevista, ReceitaPrevistaOutroRecursoPeriodo):
            return (
                self.instance_receita_prevista.previsao_valor_custeio +
                self.instance_receita_prevista.saldo_custeio
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPdde):
            return (
                self.instance_receita_prevista.previsao_valor_custeio +
                self.instance_receita_prevista.saldo_custeio
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPaa):
            return self.instance_receita_prevista.previsao_valor_custeio

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return 0

        raise NotImplementedError

    def _get_valor_capital_edicao(self):
        """ Considera o valor de capital de acordo com a instancia de Receitas previstas utilizada """
        if isinstance(self.instance_receita_prevista, ReceitaPrevistaOutroRecursoPeriodo):
            return (
                Decimal(self.receita_prevista.get('previsao_valor_capital')) +
                Decimal(self.receita_prevista.get('saldo_capital'))
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPdde):
            return (
                Decimal(self.receita_prevista.get('previsao_valor_capital')) +
                Decimal(self.receita_prevista.get('saldo_capital'))
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPaa):
            return Decimal(self.receita_prevista.get('previsao_valor_capital'))

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return 0

        raise NotImplementedError

    def _get_valor_capital_atual(self):
        """ Considera o valor de capital de acordo com a instancia de Receitas previstas utilizada """
        if isinstance(self.instance_receita_prevista, ReceitaPrevistaOutroRecursoPeriodo):
            return (
                self.instance_receita_prevista.previsao_valor_capital +
                self.instance_receita_prevista.saldo_capital
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPdde):
            return (
                self.instance_receita_prevista.previsao_valor_capital +
                self.instance_receita_prevista.saldo_capital
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPaa):
            return self.instance_receita_prevista.previsao_valor_capital

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return 0

        raise NotImplementedError

    def _get_valor_livre_edicao(self):
        """ Considera o valor de livre de acordo com a instancia de Receitas previstas utilizada """
        if isinstance(self.instance_receita_prevista, ReceitaPrevistaOutroRecursoPeriodo):
            return (
                Decimal(self.receita_prevista.get('previsao_valor_livre')) +
                Decimal(self.receita_prevista.get('saldo_livre'))
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPdde):
            return (
                Decimal(self.receita_prevista.get('previsao_valor_livre')) +
                Decimal(self.receita_prevista.get('saldo_livre'))
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPaa):
            return Decimal(self.receita_prevista.get('previsao_valor_livre'))

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return Decimal(self.receita_prevista.get('valor'))

        raise NotImplementedError

    def _get_valor_livre_atual(self):
        """ Considera o valor de livre de acordo com a instancia de Receitas previstas utilizada """
        if isinstance(self.instance_receita_prevista, ReceitaPrevistaOutroRecursoPeriodo):
            return (
                self.instance_receita_prevista.previsao_valor_livre +
                self.instance_receita_prevista.saldo_livre
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPdde):
            return (
                self.instance_receita_prevista.previsao_valor_livre +
                self.instance_receita_prevista.saldo_livre
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPaa):
            return self.instance_receita_prevista.previsao_valor_livre

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return self.instance_receita_prevista.valor

        raise NotImplementedError

    def verificar_prioridades_impactadas(self) -> list:
        """
        Verifica e retorna as prioridades que serão impactadas.
        Usado para confirmação prévia do usuário.
        """
        if not self._validar_pre_condicoes():
            logger.error("Pré condições não validadas!")
            return []

        prioridades = self._buscar_prioridades_impactadas()
        return list(prioridades.values('uuid', 'valor_total', 'tipo_aplicacao'))

    @transaction.atomic
    def limpar_valor_prioridades_impactadas(self):
        """
        Define como NULL o valor_total das prioridades impactadas
        """
        if not self._validar_pre_condicoes():
            return []

        prioridades_impactadas = self._buscar_prioridades_impactadas()

        if prioridades_impactadas.exists():
            logger.info(
                f"Limpando valor_total de {prioridades_impactadas.count()} prioridades "
                f"para acao {str(self.acao_receita)}"
            )
            logger.info('#### LIMPAR PRIORIDADES ####')
            prioridades_impactadas.update(valor_total=None)

        return list(prioridades_impactadas.values_list('uuid', flat=True))

    def _validar_pre_condicoes(self) -> bool:
        """Valida se as pré-condições estão satisfeitas."""
        if not self.instance_receita_prevista:
            logger.error(f"Receita sem instância(Não há objeto de edição): {self.instance_receita_prevista}")
            return False
        if not self.acao_receita:
            logger.error(f"Receita prevista sem acao definida: {self.acao_receita}")
            return False

        if not self.recurso:
            logger.error("Recurso no definido!")
            return False

        return True

    def _query_base(self) -> models.QuerySet:
        """
        Retorna um queryset com as prioridades que atendem as pré-condições
        para limpar o valor_total.

        As pré-condições são:
        - PAA em elaboração
        - Valor total diferente de NULL (prioridades já limpas)
        - Tipo de aplicação igual ao da receita prevista (caso tenha)

        Esta função pode ser sobrescrita para customização para diversos tipos de Receita (PTRF, PDDE, Outros Recursos)
        """
        from sme_ptrf_apps.paa.models import Paa
        paas_em_elaboracao = Paa.objects.filter(
            pk=models.OuterRef('paa_id')).paas_em_elaboracao()

        qs = PrioridadePaa.objects.filter(
            models.Exists(paas_em_elaboracao),
            valor_total__isnull=False,
        )

        return qs

    def _verifica_saldo(self, prioridade, valor_total):
        # Validar no service de Resumo de Prioridades
        resumo = ResumoPrioridadesService(prioridade.paa)
        # # considera apenas a diferença entre o valor atual da receita e o novo valor
        # valor_total = valor_custeio_atual - valor_custeio_edicao
        SIMULA_PRIORIDADE_SEM_VALOR = 0
        # Retorna Exceção em caso de saldo insuficiente
        resumo.validar_valor_prioridade(
            valor_total=valor_total,
            acao_uuid=self._get_acao_uuid_resumo_prioridade(),
            tipo_aplicacao=prioridade.tipo_aplicacao,
            recurso=self.recurso,
            prioridade_uuid=prioridade.uuid,
            # Considera 0 apenas para simular uma validação de saldo(simula uma prioridade sem valor para checar o saldo)  # noqa
            valor_atual_prioridade=SIMULA_PRIORIDADE_SEM_VALOR
        )

    def _buscar_prioridades_impactadas(self):
        qs = self._query_base()

        if qs.exists():
            prioridades_com_saldo_afetados = []
            if self.instance_receita_prevista:
                logger.error(f"Checando edição de receita prevista: {self.instance_receita_prevista}")
                # Se for edição
                valor_custeio_edicao = Decimal(self._get_valor_custeio_edicao())
                valor_capital_edicao = Decimal(self._get_valor_capital_edicao())
                valor_livre_edicao = Decimal(self._get_valor_livre_edicao())
                logger.info(f"Valores da edição: {valor_custeio_edicao}, {valor_capital_edicao}, {valor_livre_edicao}")

                valor_custeio_atual = self._get_valor_custeio_atual()
                valor_capital_atual = self._get_valor_capital_atual()
                valor_livre_atual = self._get_valor_livre_atual()
                logger.info(f"Valores atuais: {valor_custeio_atual}, {valor_capital_atual}, {valor_livre_atual}")

                # verifica se custeio foi reduzido
                valor_custeio_foi_reduzido = valor_custeio_edicao < valor_custeio_atual

                # verifica se capital foi reduzido
                valor_capital_foi_reduzido = valor_capital_edicao < valor_capital_atual

                # verifica se livre foi reduzido
                valor_livre_foi_reduzido = valor_livre_edicao < valor_livre_atual

                valor_total = 0
                valor_total += valor_custeio_atual - valor_custeio_edicao
                valor_total += valor_capital_atual - valor_capital_edicao
                valor_total += valor_livre_atual - valor_livre_edicao

                if valor_custeio_foi_reduzido:
                    # verificar somente as prioridades de custeio para validação de saldo
                    prioridades_a_verificar = qs.filter(tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name)
                    logger.error((
                        "Validando a redução de valor de custeio em edição da receita prevista "
                        f"de {valor_custeio_atual} para {valor_custeio_edicao}. Valor dif. {valor_total}"))

                    for prioridade in prioridades_a_verificar:
                        # Validar no service de Resumo de Prioridades
                        try:
                            self._verifica_saldo(prioridade, valor_total)
                        except ValidacaoSaldoIndisponivel:
                            logger.error(f"Saldo insuficiente para a prioridade de custeio {prioridade.uuid}")
                            # adiciona às prioridades que afetaram o saldo
                            prioridades_com_saldo_afetados.append(str(prioridade.uuid))
                        except Exception as e:
                            logger.error(f"Erro ao validar saldo para a prioridade de custeio {prioridade.uuid}: {e}")

                if valor_capital_foi_reduzido:
                    # verificar somente as prioridades de capital para validação de saldo
                    prioridades_a_verificar = qs.filter(tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name)
                    logger.error((
                        "Validando a redução de valor de capital em edição da receita prevista "
                        f"de {valor_capital_atual} para {valor_capital_edicao}. Valor dif. {valor_total}"))
                    for prioridade in prioridades_a_verificar:
                        # Validar no service de Resumo de Prioridades
                        try:
                            self._verifica_saldo(prioridade, valor_total)
                        except ValidacaoSaldoIndisponivel:
                            logger.error(f"Saldo insuficiente para a prioridade de capital {prioridade.uuid}")
                            # adiciona às prioridades que afetaram o saldo
                            prioridades_com_saldo_afetados.append(str(prioridade.uuid))
                        except Exception as e:
                            logger.error(f"Erro ao validar saldo para a prioridade de capital {prioridade.uuid}: {e}")

                if valor_livre_foi_reduzido:
                    # verificar prioridades de custeio e capital para validação de saldo quando valor_livre é reduzido
                    # Pois, ambos os tipos de aplicação utilizam do mesmo saldo quando, em custeio/capital não há saldo
                    # OBS: Nesse caso, a validação de saldo é realizada considerando apenas os valores de
                    # livre aplicação de (valor_livre_atual - valor_livre_edicao).
                    valor_total = valor_livre_atual - valor_livre_edicao

                    prioridades_a_verificar = qs.filter(
                        tipo_aplicacao__in=[
                            TipoAplicacaoOpcoesEnum.CUSTEIO.name,
                            TipoAplicacaoOpcoesEnum.CAPITAL.name
                        ])
                    logger.error((
                        "Validando a redução de valor de livre aplicacao em edição da receita prevista "
                        f"de {valor_livre_atual} para {valor_livre_edicao}"))
                    for prioridade in prioridades_a_verificar:
                        # Validar no service de Resumo de Prioridades
                        try:
                            self._verifica_saldo(prioridade, valor_total)
                        except ValidacaoSaldoIndisponivel:
                            logger.error(f"Saldo insuficiente para a prioridade de livre {prioridade.uuid}")
                            # adiciona às prioridades que afetaram o saldo
                            prioridades_com_saldo_afetados.append(str(prioridade.uuid))
                        except Exception as e:
                            logger.error(f"Erro ao validar saldo para a prioridade de livre {prioridade.uuid}: {e}")

            # retornar somente prioridades com saldos afetados
            qs = qs.filter(uuid__in=prioridades_com_saldo_afetados)

        logger.info(f"Encontradas {qs.count()} prioridades impactadas.")
        return qs


class PrioridadesPaaImpactadasReceitasPrevistasPTRFService(PrioridadesPaaImpactadasBaseService):
    def __init__(self, receita_prevista: dict, instance_receita_prevista: ReceitaPrevistaPaa = None):
        super().__init__(receita_prevista, instance_receita_prevista)

    def get_acao_receita(self):
        return self.instance_receita_prevista.acao_associacao if self.instance_receita_prevista else None

    def get_recurso(self):
        return RecursoOpcoesEnum.PTRF.name

    def _query_base(self):
        qs = super()._query_base()
        qs = qs.filter(
            paa__associacao=self.acao_receita.associacao,
            acao_associacao=self.acao_receita,
            recurso=self.recurso,
        )
        return qs


class PrioridadesPaaImpactadasReceitasPrevistasPDDEService(PrioridadesPaaImpactadasBaseService):
    def __init__(self, receita_prevista: dict, instance_receita_prevista: ReceitaPrevistaPdde = None):
        super().__init__(receita_prevista, instance_receita_prevista)

    def get_recurso(self):
        return RecursoOpcoesEnum.PDDE.name

    def get_acao_receita(self):
        logger.info(f"get_acao_receita: {self.instance_receita_prevista}")
        return self.instance_receita_prevista.acao_pdde if self.instance_receita_prevista else None

    def _query_base(self) -> models.QuerySet:
        qs = super()._query_base()
        paa = self.instance_receita_prevista.paa
        logger.info(f"paa: {paa}")
        qs = qs.filter(
            paa__associacao=paa.associacao,
            acao_pdde=self.acao_receita,
            programa_pdde=self.acao_receita.programa,
            recurso=self.recurso,
        )
        logger.info(f"query_base: {qs.values('uuid', 'valor_total', 'tipo_aplicacao')}")
        return qs


class PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(PrioridadesPaaImpactadasBaseService):
    def __init__(self, receita_prevista: dict, instance_receita_prevista: ReceitaPrevistaOutroRecursoPeriodo = None):
        super().__init__(receita_prevista, instance_receita_prevista)

    def get_recurso(self):
        return RecursoOpcoesEnum.OUTRO_RECURSO.name

    def get_acao_receita(self):
        logger.info(f"get_acao_receita: {self.instance_receita_prevista}")
        return self.instance_receita_prevista.outro_recurso_periodo if self.instance_receita_prevista else None

    def _query_base(self) -> models.QuerySet:
        qs = super()._query_base()
        paa = self.instance_receita_prevista.paa
        logger.info(f"paa: {paa}")
        qs = qs.filter(
            paa__associacao=paa.associacao,
            outro_recurso=self.acao_receita.outro_recurso,
            recurso=self.recurso,
        )
        logger.info(f"query_base: {qs.values('uuid', 'valor_total', 'tipo_aplicacao')}")
        return qs


class PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(PrioridadesPaaImpactadasBaseService):
    def __init__(self, receita_prevista: dict, instance_receita_prevista: RecursoProprioPaa = None):
        super().__init__(receita_prevista, instance_receita_prevista)

    def get_recurso(self):
        return RecursoOpcoesEnum.RECURSO_PROPRIO.name

    def get_acao_receita(self):
        # RECURSO_PROPRIO utiliza o proprio Enum para o Node de saldo em Resumo de Recurso
        return self.get_recurso()

    def _query_base(self) -> models.QuerySet:
        qs = super()._query_base()
        paa = self.instance_receita_prevista.paa
        logger.info(f"paa: {paa}")
        qs = qs.filter(
            paa__associacao=paa.associacao,
            recurso=self.recurso,
        )
        logger.info(f"query_base: {qs.values('uuid', 'valor_total', 'tipo_aplicacao')}")
        return qs

    @transaction.atomic
    def limpar_valor_prioridades_impactadas_ao_excluir_instancia(self, confirmar=False):
        """
        Define como NULL o valor_total das prioridades impactadas pela exclusão do Recurso Próprio
        """
        qs = self._query_base()
        if not self._validar_pre_condicoes():
            return []

        prioridades_impactadas = qs.filter(
            tipo_aplicacao__in=[
                TipoAplicacaoOpcoesEnum.CUSTEIO.name,
                TipoAplicacaoOpcoesEnum.CAPITAL.name
            ])

        if prioridades_impactadas.exists():
            logger.info(
                f"Limpando valor_total de {prioridades_impactadas.count()} prioridades "
                f"para acao {str(self.acao_receita)} impactadas pela exclusão de Recurso Próprio"
            )
            logger.info('#### LIMPAR PRIORIDADES ####')
            if not confirmar:
                raise ConfirmarExlusaoPrioridadesPaaRecursoProprioService((
                    "Existem prioridades cadastradas que utilizam o valor da receita prevista. "
                    "Será necessário revisar as prioridades para atualizar o valor total.")
                )
            prioridades_impactadas.update(valor_total=None)

        return list(prioridades_impactadas.values_list('uuid', flat=True))
