import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from django.db import transaction, models
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
from sme_ptrf_apps.paa.services import ResumoPrioridadesService, ValidacaoSaldoIndisponivel
from sme_ptrf_apps.paa.models import (
    ReceitaPrevistaPaa,
    AcaoPdde,
    OutroRecursoPeriodoPaa,
    ReceitaPrevistaOutroRecursoPeriodo,
    ReceitaPrevistaPdde,
    RecursoProprioPaa,
)
from sme_ptrf_apps.core.models.acao_associacao import AcaoAssociacao
logger = logging.getLogger(__name__)

ReceitaPrevistaInstancia = ReceitaPrevistaPaa | ReceitaPrevistaPdde | ReceitaPrevistaOutroRecursoPeriodo | RecursoProprioPaa  # noqa


class ConfirmarExlusaoPrioridadesPaaRecursoProprioService(Exception):
    """Sinaliza que a exclusão de um Recurso Próprio precisa de confirmação do usuário.

    Levantada quando há prioridades cadastradas que utilizam o valor da
    receita prevista de Recurso Próprio a ser excluída.
    """


class PrioridadesPaaImpactadasBaseService(ABC):
    """
    Service para sincronizar prioridades do PAA quando Receitas Previstas PTRF, PDDE, Outros Recursos.

    Regras:
    - PAA deve estar em elaboração (status = EM_ELABORACAO ou EM_RETIFICACAO)
    - Prioridades devem usar a mesma Ação(PTRF, PDDE, Outros Recursos)
    """

    def __init__(self, receita_prevista: dict, instance_receita_prevista: ReceitaPrevistaInstancia | None = None):
        """Inicializa o serviço de prioridades do PAA com base em uma receita prevista.

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
        # Cache de ResumoPrioridadesService por paa_id: evita recriar o service (e recalcular o resumo
        # completo do PAA, custoso) a cada prioridade verificada em `_verifica_saldo`, já que todas as
        # prioridades avaliadas num mesmo loop pertencem ao mesmo PAA.
        self._resumo_service_cache = {}

    @abstractmethod
    def get_acao_receita(self):
        """ Necessário a sobrescrita de acordo com a instancia de Receitas previstas utilizada
            Ex:
                - Receitas Previstas PTRF utiliza `acao_associacao`
                - Receitas Previstas PDDE utiliza `acao_pdde`
                - Receitas Previstas OUTRO_RECURSO utiliza `outro_recurso_periodo`"""
        raise NotImplementedError

    @abstractmethod
    def get_recurso(self) -> str:
        """Retorna o nome do recurso associado à receita prevista (RecursoOpcoesEnum).

        Deve ser sobrescrito de acordo com a instância de receita
        prevista utilizada.

        Raises:
            NotImplementedError: Sempre, quando não sobrescrito pela
                subclasse.
        """
        raise NotImplementedError

    def _get_acao_uuid_resumo_prioridade(self) -> str:
        """Identificador utilizado no Node do resumo de prioridades.

        Returns:
            UUID da ação/recurso associado à instância de
            receita prevista em edição.

        Raises:
            NotImplementedError: Caso a instância de receita prevista não
                seja de um tipo reconhecido.
        """
        if isinstance(self.instance_receita_prevista, ReceitaPrevistaOutroRecursoPeriodo):
            return self.instance_receita_prevista.outro_recurso_periodo.outro_recurso.uuid

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPdde):
            return self.instance_receita_prevista.acao_pdde.uuid

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPaa):
            return self.instance_receita_prevista.acao_associacao.uuid

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return self.instance_receita_prevista.associacao.uuid

        raise NotImplementedError

    def _get_valor_custeio_edicao(self) -> Decimal | int:
        """Calcula o valor de custeio considerado na edição da receita prevista.

        Considera os dados enviados em `receita_prevista` de acordo com o
        tipo de instância de receita prevista utilizada.

        Returns:
            Valor de custeio (previsão mais saldo, quando aplicável) da
            edição, ou 0 quando o recurso não possui custeio (Recurso
            Próprio).

        Raises:
            NotImplementedError: Caso a instância de receita prevista não
                seja de um tipo reconhecido.
        """
        if isinstance(self.instance_receita_prevista, ReceitaPrevistaOutroRecursoPeriodo):
            return (
                Decimal(self.receita_prevista.get('previsao_valor_custeio') or 0) +
                Decimal(self.receita_prevista.get('saldo_custeio') or 0)
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPdde):
            return (
                Decimal(self.receita_prevista.get('previsao_valor_custeio')) +
                Decimal(self.receita_prevista.get('saldo_custeio'))
            )

        if isinstance(self.instance_receita_prevista, ReceitaPrevistaPaa):
            return Decimal(self.receita_prevista.get('previsao_valor_custeio', 0))

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return 0

        raise NotImplementedError

    def _get_valor_custeio_atual(self) -> Decimal | int:
        """Retorna o valor de custeio atual (antes da edição) da receita prevista.

        Returns:
            Valor de custeio atual (previsão mais saldo, quando
            aplicável), ou 0 quando o recurso não possui custeio (Recurso
            Próprio).

        Raises:
            NotImplementedError: Caso a instância de receita prevista não
                seja de um tipo reconhecido.
        """
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

    def _get_valor_capital_edicao(self) -> Decimal | int:
        """Calcula o valor de capital considerado na edição da receita prevista.

        Returns:
            Valor de capital (previsão mais saldo, quando aplicável) da
            edição, ou 0 quando o recurso não possui capital (Recurso
            Próprio).

        Raises:
            NotImplementedError: Caso a instância de receita prevista não
                seja de um tipo reconhecido.
        """
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
            return Decimal(self.receita_prevista.get('previsao_valor_capital', 0))

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return 0

        raise NotImplementedError

    def _get_valor_capital_atual(self) -> Decimal | int:
        """Retorna o valor de capital atual (antes da edição) da receita prevista.

        Returns:
            Valor de capital atual (previsão mais saldo, quando
            aplicável), ou 0 quando o recurso não possui capital (Recurso
            Próprio).

        Raises:
            NotImplementedError: Caso a instância de receita prevista não
                seja de um tipo reconhecido.
        """
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

    def _get_valor_livre_edicao(self) -> Decimal:
        """Calcula o valor de livre aplicação considerado na edição da receita prevista.

        Returns:
            Valor de livre aplicação (previsão mais saldo, quando
            aplicável) da edição.

        Raises:
            NotImplementedError: Caso a instância de receita prevista não
                seja de um tipo reconhecido.
        """
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
            return Decimal(self.receita_prevista.get('previsao_valor_livre', 0))

        if isinstance(self.instance_receita_prevista, RecursoProprioPaa):
            return Decimal(self.receita_prevista.get('valor'))

        raise NotImplementedError

    def _get_valor_livre_atual(self) -> Decimal:
        """Retorna o valor de livre aplicação atual (antes da edição) da receita prevista.

        Returns:
            Valor de livre aplicação atual (previsão mais saldo, quando
            aplicável).

        Raises:
            NotImplementedError: Caso a instância de receita prevista não
                seja de um tipo reconhecido.
        """
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
        """Verifica e retorna as prioridades que serão impactadas.

        Usado para confirmação prévia do usuário.

        Returns:
            Lista de dicionários com 'uuid', 'valor_total' e
            'tipo_aplicacao' das prioridades impactadas, ou lista vazia
            caso as pré-condições não sejam satisfeitas.
        """
        if not self._validar_pre_condicoes():
            logger.error("Pré condições não validadas!")
            return []

        prioridades = self._buscar_prioridades_impactadas()
        return list(prioridades.values('uuid', 'valor_total', 'tipo_aplicacao'))

    @transaction.atomic
    def _update_valor_prioridades(self, prioridades_updates: models.QuerySet) -> list:
        """Define como None o valor_total das prioridades impactadas.

        Args:
            prioridades_updates: QuerySet de PrioridadePaa cujo
                valor_total deve ser limpo.

        Returns:
            Lista com os UUIDs das prioridades que tiveram o valor_total
            definido como None.
        """
        if prioridades_updates.exists():
            logger.info(
                f"Limpando valor_total de {prioridades_updates.count()} prioridades "
                f"para açãoo {str(self.acao_receita)}"
            )
            logger.info('#### LIMPAR PRIORIDADES ####')
            prioridades_updates.update(valor_total=None)

        return list(prioridades_updates.values_list('uuid', flat=True))

    def limpar_valor_prioridades_impactadas(self) -> list:
        """Define como NULL o valor_total das prioridades impactadas.

        Returns:
            Lista com os UUIDs das prioridades impactadas cujo valor_total
            foi definido como NULL, ou lista vazia caso as pré-condições
            não sejam satisfeitas.
        """
        if not self._validar_pre_condicoes():
            return []

        prioridades_impactadas = self._buscar_prioridades_impactadas()

        return self._update_valor_prioridades(prioridades_impactadas)

    def _validar_pre_condicoes(self) -> bool:
        """Valida se as pré-condições estão satisfeitas.

        Returns:
            True se houver instância de receita prevista em edição, ação/
            recurso e recurso definidos, False caso contrário.
        """
        if not self.instance_receita_prevista:
            logger.info(f"Receita sem instância(Não há objeto de edição): {self.instance_receita_prevista}")
            return False
        if not self.acao_receita:
            logger.info(f"Receita prevista sem acao definida: {self.acao_receita}")
            return False

        if not self.recurso:
            logger.info("Recurso não definido!")
            return False

        return True

    def _query_base(self) -> models.QuerySet:
        """Retorna um queryset com as prioridades que atendem as pré-condições para limpar o valor_total.

        As pré-condições são:
        - PAA em elaboração ou em retificação
        - Valor total diferente de NULL (prioridades já limpas)
        - Tipo de aplicação igual ao da receita prevista (caso tenha)

        Esta função pode ser sobrescrita para customização para diversos
        tipos de Receita (PTRF, PDDE, Outros Recursos).

        Returns:
            QuerySet de PrioridadePaa filtrado pelas pré-condições
            básicas.
        """
        from sme_ptrf_apps.paa.models import Paa

        paas_em_elaboracao = Paa.objects.filter(
            pk=models.OuterRef('paa_id')).paas_em_elaboracao()

        paas_em_retificacao = Paa.objects.filter(
            pk=models.OuterRef('paa_id')).paas_em_retificacao()

        qs = PrioridadePaa.objects.filter(
            models.Exists(paas_em_elaboracao) | models.Exists(paas_em_retificacao),
            valor_total__isnull=False,
        )

        return qs

    def _verifica_tem_saldo_prioridades_acao_receita(self) -> models.QuerySet:
        """Verifica se há saldo disponível nas prioridades da ação/recurso da receita.

        Checar nas prioridades do PAA, independente de edição/criação, se
        há saldos disponíveis. Checagem pode ser realizada fora do fluxo
        de edição/criação de despesas e prioridades.

        Por exemplo, utilizar este recurso ao descongelar o saldo de
        receitas previstas, para evitar que o Resumo de Prioridades seja
        impactado por despesas criadas durante o congelamento do saldo
        (passando a ficar negativo o saldo das prioridades ao
        descongelar).

        Returns:
            QuerySet de PrioridadePaa com as prioridades cujo saldo
            ficaria indisponível.
        """
        from sme_ptrf_apps.paa.services.resumo_prioridades_service import ValidacaoSaldoIndisponivel
        """
            Checar nas prioridades do PAA, independente de edição/criação, se há saldos disponíveis
            Checagem pode ser realizada for do fluxo de edição/criação de despesas e prioridades
            Por exemplo:
                - Utilizar este recurso ao descongelar o Saldo de receitas previstas:
                    Para evitar que o Resumo de Prioridades seja impactado por despesas criadas durante o congelamento
                    do saldo, passando a ficar negativo, o saldo das prioridades, ao descongelar)
        """
        prioridades = self._query_base()
        prioridades_saldo_indisponivel = []
        logger.info(f"Verificando saldo das prioridades da acao receita: {self.recurso} - {self.acao_receita}")
        for prioridade in prioridades:
            try:
                # simula valor_total zerado apenas para checagem de saldo, simulando sem acrescimo de valor atual
                self._verifica_saldo(prioridade, 0)
            except ValidacaoSaldoIndisponivel as e:
                logger.error(str(e))
                prioridades_saldo_indisponivel.append(prioridade.id)
            except Exception as e:
                logger.error((
                    "Erro ao verificar saldo das prioridades criadas"
                    f"para a acao receita: {self.acao_receita} : {str(e)}"))
                prioridades_saldo_indisponivel.append(prioridade.id)

        # Retornar um tipo Queryset
        prioridades_saldo_indisponivel = self._query_base().filter(id__in=prioridades_saldo_indisponivel)
        return prioridades_saldo_indisponivel

    def limpar_valor_prioridades_saldo_indisponivel_da_acao_receita(self) -> list:
        """Limpa o valor_total das prioridades da ação/recurso com saldo indisponível.

        Returns:
            Lista com os UUIDs das prioridades que tiveram o valor_total
            definido como None.
        """
        prioridades_impactadas = self._verifica_tem_saldo_prioridades_acao_receita()
        return self._update_valor_prioridades(prioridades_impactadas)

    def _verifica_saldo(self, prioridade: PrioridadePaa, valor_total: Decimal | int) -> None:
        """Valida se há saldo disponível para o valor informado na prioridade.

        Args:
            prioridade: Prioridade do PAA a ser validada.
            valor_total: Valor a ser somado ao saldo atual da prioridade
                para simular a validação.

        Raises:
            ValidacaoSaldoIndisponivel: Quando o saldo é insuficiente para
                o valor informado.
        """
        # Validar no service de Resumo de Prioridades
        # Reaproveita a instância (e o resumo memoizado nela) entre prioridades do mesmo PAA,
        # em vez de recriar o service (e recalcular todo o resumo) a cada iteração do loop.
        resumo = self._resumo_service_cache.get(prioridade.paa_id)
        if resumo is None:
            resumo = ResumoPrioridadesService(prioridade.paa)
            self._resumo_service_cache[prioridade.paa_id] = resumo

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

    def _buscar_prioridades_impactadas(self) -> models.QuerySet:
        """Busca prioridades cujo saldo seria afetado pela edição da receita prevista.

        Compara os valores atuais e editados de custeio, capital e livre
        aplicação e, para cada tipo reduzido, valida o saldo das
        prioridades correspondentes via `_verifica_saldo`.

        Returns:
            QuerySet de PrioridadePaa com as prioridades impactadas cujo
            saldo seria afetado pela edição.
        """
        qs = self._query_base()

        if qs.exists():
            prioridades_com_saldo_afetados = []
            if self.instance_receita_prevista:
                logger.info(f"Checando edição de receita prevista: {self.instance_receita_prevista}")
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
                logger.info(f"valor_custeio_foi_reduzido: {valor_custeio_foi_reduzido}")

                # verifica se capital foi reduzido
                valor_capital_foi_reduzido = valor_capital_edicao < valor_capital_atual
                logger.info(f"valor_capital_foi_reduzido: {valor_capital_foi_reduzido}")

                # verifica se livre foi reduzido
                valor_livre_foi_reduzido = valor_livre_edicao < valor_livre_atual
                logger.info(f"valor_livre_foi_reduzido: {valor_livre_foi_reduzido}")

                valor_total = 0
                valor_total += valor_custeio_atual - valor_custeio_edicao
                valor_total += valor_capital_atual - valor_capital_edicao
                valor_total += valor_livre_atual - valor_livre_edicao

                if valor_custeio_foi_reduzido:
                    # verificar somente as prioridades de custeio para validação de saldo
                    prioridades_a_verificar = qs.filter(tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name)
                    logger.info((
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
                    logger.info((
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
                    logger.info((
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
    """Service de prioridades do PAA impactadas por Receitas Previstas PTRF."""

    def __init__(self, receita_prevista: dict, instance_receita_prevista: ReceitaPrevistaPaa | None = None):
        """Inicializa o service com a receita prevista PTRF e a instância opcional em edição.

        Args:
            receita_prevista: Dados da receita prevista PTRF (dicionário
                recebido no serializer).
            instance_receita_prevista: Instância existente de
                ReceitaPrevistaPaa, usada quando a receita está sendo
                editada. Padrão None, para criação de uma nova receita
                prevista.
        """
        super().__init__(receita_prevista, instance_receita_prevista)

    def get_acao_receita(self) -> AcaoAssociacao | None:
        """Retorna a ação de associação vinculada à receita prevista PTRF.

        Returns:
            A AcaoAssociacao da instância em edição, ou None quando não
            há instância em edição.
        """
        return self.instance_receita_prevista.acao_associacao if self.instance_receita_prevista else None

    def get_recurso(self) -> str:
        """Retorna o nome do recurso PTRF.

        Returns:
            O valor de RecursoOpcoesEnum.PTRF.name.
        """
        return RecursoOpcoesEnum.PTRF.name

    def _query_base(self) -> models.QuerySet:
        """Restringe o queryset base às prioridades PTRF da ação/associação da receita.

        Returns:
            QuerySet de PrioridadePaa filtrado pela associação, ação e
            recurso PTRF.
        """
        qs = super()._query_base()
        qs = qs.filter(
            paa__associacao=self.acao_receita.associacao,
            acao_associacao=self.acao_receita,
            recurso=self.recurso,
        )
        return qs


class PrioridadesPaaImpactadasReceitasPrevistasPDDEService(PrioridadesPaaImpactadasBaseService):
    """Service de prioridades do PAA impactadas por Receitas Previstas PDDE."""

    def __init__(self, receita_prevista: dict, instance_receita_prevista: ReceitaPrevistaPdde | None = None):
        """Inicializa o service com a receita prevista PDDE e a instância opcional em edição.

        Args:
            receita_prevista: Dados da receita prevista PDDE (dicionário
                recebido no serializer).
            instance_receita_prevista: Instância existente de
                ReceitaPrevistaPdde, usada quando a receita está sendo
                editada. Padrão None, para criação de uma nova receita
                prevista.
        """
        super().__init__(receita_prevista, instance_receita_prevista)

    def get_recurso(self) -> str:
        """Retorna o nome do recurso PDDE.

        Returns:
            O valor de RecursoOpcoesEnum.PDDE.name.
        """
        return RecursoOpcoesEnum.PDDE.name

    def get_acao_receita(self) -> AcaoPdde | None:
        """Retorna a ação PDDE vinculada à receita prevista.

        Returns:
            A AcaoPdde da instância em edição, ou None quando não há
            instância em edição.
        """
        logger.info(f"get_acao_receita: {self.instance_receita_prevista}")
        return self.instance_receita_prevista.acao_pdde if self.instance_receita_prevista else None

    def _query_base(self) -> models.QuerySet:
        """Restringe o queryset base às prioridades PDDE da ação/programa da receita.

        Returns:
            QuerySet de PrioridadePaa filtrado pela associação, ação
            PDDE, programa e recurso PDDE.
        """
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
    """Service de prioridades do PAA impactadas por Receitas Previstas de Outros Recursos."""

    def __init__(
        self, receita_prevista: dict, instance_receita_prevista: ReceitaPrevistaOutroRecursoPeriodo | None = None
    ):
        """Inicializa o service com a receita prevista de Outros Recursos e a instância opcional em edição.

        Args:
            receita_prevista: Dados da receita prevista de Outros
                Recursos (dicionário recebido no serializer).
            instance_receita_prevista: Instância existente de
                ReceitaPrevistaOutroRecursoPeriodo, usada quando a receita
                está sendo editada. Padrão None, para criação de uma nova
                receita prevista.
        """
        super().__init__(receita_prevista, instance_receita_prevista)

    def get_recurso(self) -> str:
        """Retorna o nome do recurso Outros Recursos.

        Returns:
            O valor de RecursoOpcoesEnum.OUTRO_RECURSO.name.
        """
        return RecursoOpcoesEnum.OUTRO_RECURSO.name

    def get_acao_receita(self) -> OutroRecursoPeriodoPaa | None:
        """Retorna o Outro Recurso do Período vinculado à receita prevista.

        Returns:
            O OutroRecursoPeriodoPaa da instância em edição, ou None
            quando não há instância em edição.
        """
        logger.info(f"get_acao_receita: {self.instance_receita_prevista}")
        return self.instance_receita_prevista.outro_recurso_periodo if self.instance_receita_prevista else None

    def _query_base(self) -> models.QuerySet:
        """Restringe o queryset base às prioridades do Outro Recurso do Período da receita.

        Returns:
            QuerySet de PrioridadePaa filtrado pela associação, outro
            recurso e recurso.
        """
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
    """Service de prioridades do PAA impactadas por Receitas Previstas de Recurso Próprio."""

    def __init__(self, receita_prevista: dict, instance_receita_prevista: RecursoProprioPaa | None = None):
        """Inicializa o service com a receita prevista de Recurso Próprio e a instância opcional em edição.

        Args:
            receita_prevista: Dados da receita prevista de Recurso Próprio
                (dicionário recebido no serializer).
            instance_receita_prevista: Instância existente de
                RecursoProprioPaa, usada quando a receita está sendo
                editada. Padrão None, para criação de uma nova receita
                prevista.
        """
        super().__init__(receita_prevista, instance_receita_prevista)

    def get_recurso(self) -> str:
        """Retorna o nome do Recurso Próprio.

        Returns:
            O valor de RecursoOpcoesEnum.RECURSO_PROPRIO.name.
        """
        return RecursoOpcoesEnum.RECURSO_PROPRIO.name

    def get_acao_receita(self) -> str:
        """Retorna o identificador de ação/recurso usado no Resumo de Prioridades.

        RECURSO_PROPRIO utiliza o próprio Enum para o Node de saldo em
        Resumo de Recurso.

        Returns:
            O valor de RecursoOpcoesEnum.RECURSO_PROPRIO.name.
        """
        return self.get_recurso()

    def _query_base(self) -> models.QuerySet:
        """Restringe o queryset base às prioridades de Recurso Próprio da associação da receita.

        Returns:
            QuerySet de PrioridadePaa filtrado pela associação e pelo
            Recurso Próprio.
        """
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
    def limpar_valor_prioridades_impactadas_ao_excluir_instancia(self, confirmar: bool = False) -> list:
        """Define como NULL o valor_total das prioridades impactadas pela exclusão do Recurso Próprio.

        Args:
            confirmar: Quando False (padrão) e houver prioridades
                impactadas, levanta
                `ConfirmarExlusaoPrioridadesPaaRecursoProprioService` para
                que o usuário confirme a exclusão antes de limpar os
                valores.

        Returns:
            Lista com os UUIDs das prioridades impactadas cujo valor_total
            foi definido como NULL, ou lista vazia caso as pré-condições
            não sejam satisfeitas.

        Raises:
            ConfirmarExlusaoPrioridadesPaaRecursoProprioService: Quando há
                prioridades impactadas e `confirmar` é False.
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
