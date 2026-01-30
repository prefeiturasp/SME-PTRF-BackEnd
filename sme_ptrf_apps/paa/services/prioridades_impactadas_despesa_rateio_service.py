import logging
from django.db import transaction
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.enums import PaaStatusEnum, RecursoOpcoesEnum
from sme_ptrf_apps.paa.services import ResumoPrioridadesService, ValidacaoSaldoIndisponivel

logger = logging.getLogger(__name__)


class PrioridadesPaaImpactadasDespesaRateioService:
    """
    Service para sincronizar prioridades do PAA quando despesas são cadastradas.

    Regras:
    - PAA deve estar em elaboração (status = EM_ELABORACAO)
    - Saldo NÃO deve estar congelado (saldo_congelado_em IS NULL)
    - Prioridades devem usar a mesma acao_associacao do rateio
    - Prioridades devem ser do tipo PTRF
    """

    def __init__(self, rateio_attrs: dict, instance_despesa=None):
        self.instance_despesa = instance_despesa  # Quando despesa é um objeto existente (edição)
        self.rateio = rateio_attrs
        self.acao_associacao = rateio_attrs.get('acao_associacao')
        self.associacao = rateio_attrs.get('associacao')
        self.tipo_aplicacao = rateio_attrs.get('aplicacao_recurso')

    def verificar_prioridades_impactadas(self):
        """
        Verifica e retorna as prioridades que serão impactadas.
        Usado para confirmação prévia do usuário.
        """
        if not self._validar_pre_condicoes():
            return []

        prioridades = self._buscar_prioridades_impactadas()
        return list(prioridades.values('uuid', 'valor_total', 'tipo_aplicacao'))

    @transaction.atomic
    def limpar_valor_prioridades_impactadas(self):
        """
        Define como NULL o valor_total das prioridades impactadas pelo cadastro da despesa.
        """
        if not self._validar_pre_condicoes():
            return []

        prioridades_impactadas = self._buscar_prioridades_impactadas()

        if prioridades_impactadas.exists():
            logger.info(
                f"Limpando valor_total de {prioridades_impactadas.count()} prioridades "
                f"para acao_associacao {self.acao_associacao.uuid}"
            )
            logger.info(
                '#### LIMPAR PRIORIDADES ####'
            )
            prioridades_impactadas.update(valor_total=None)

        return list(prioridades_impactadas.values_list('uuid', flat=True))

    def _validar_pre_condicoes(self):
        """Valida se as pré-condições estão satisfeitas."""
        if not self.acao_associacao:
            return False

        if not self.associacao:
            return False

        return True

    def _buscar_prioridades_impactadas(self):
        """
        Busca prioridades que devem ter valor limpo (NULL).

        Critérios:
        - PAA em elaboração
        - Saldo NÃO congelado
        - Mesma acao_associacao do rateio
        - Recurso = PTRF
        """

        qs = PrioridadePaa.objects.filter(
            paa__associacao=self.associacao,
            paa__status=PaaStatusEnum.EM_ELABORACAO.name,
            paa__saldo_congelado_em__isnull=True,
            acao_associacao=self.acao_associacao,
            recurso=RecursoOpcoesEnum.PTRF.name,
            valor_total__isnull=False
        )

        if self.tipo_aplicacao:
            qs = qs.filter(tipo_aplicacao=self.tipo_aplicacao)

        if qs.exists():
            prioridades_com_saldo_afetados = []
            for prioridade in qs:
                logger.info(f'Iterando Prioridade: {prioridade.uuid} no valor de {prioridade.valor_total}')
                # Checar Valores
                resumo = ResumoPrioridadesService(prioridade.paa)
                try:
                    try:
                        rateio_instance = self.instance_despesa.rateios.get(uuid=self.rateio.get('uuid'))
                        valor_total = (
                            # novo valor do rateio (em edição)
                            round(float(self.rateio.get('valor_rateio')), 2) -
                            # valor antigo do rateio
                            round(float(rateio_instance.valor_rateio), 2)
                        )
                    except Exception:
                        # Exceção quando não há rateio no cadastro da despesa ou se trata de criação de nova despesa
                        # Considera somente o valor do rateio (criação)
                        valor_total = self.rateio.get('valor_rateio')
                    resumo.validar_valor_prioridade(
                        valor_total=valor_total,
                        acao_uuid=self.acao_associacao.uuid,
                        tipo_aplicacao=self.tipo_aplicacao,
                        recurso=RecursoOpcoesEnum.PTRF.name,
                        prioridade_uuid=prioridade.uuid,
                        # Considera 0 apenas para simular uma validação de saldo(simula uma prioridade sem valor para checar o saldo)  # noqa
                        valor_atual_prioridade=0
                    )
                    pass
                except ValidacaoSaldoIndisponivel as e:
                    logger.error(f"Saldo insuficiente para a prioridade {prioridade.uuid}: {e.args[0]}")
                    prioridades_com_saldo_afetados.append(str(prioridade.uuid))
                except Exception as e:
                    logger.error(f"Erro ao validar saldo para a prioridade {prioridade.uuid}: {e}")
            # retornar somente prioridades com saldos afetados
            qs = qs.filter(uuid__in=prioridades_com_saldo_afetados)

        logger.info(f"Encontradas {qs.count()} prioridades impactadas.")
        return qs
