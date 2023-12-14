import logging

from celery import chain, group

from sme_ptrf_apps.core.models import (
    TaskCelery,
    Periodo,
    Associacao,
    AcaoAssociacao,
    ObservacaoConciliacao,
    PrestacaoConta,
    DemonstrativoFinanceiro,
    RelacaoBens,
)

from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL

from sme_ptrf_apps.core.services import concluir_prestacao_de_contas

from sme_ptrf_apps.core.services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro
from sme_ptrf_apps.core.services.persistencia_dados_demo_financeiro_service import PersistenciaDadosDemoFinanceiro

from sme_ptrf_apps.core.services.relacao_bens import _persistir_arquivo_relacao_de_bens

from sme_ptrf_apps.core.tasks import (
    concluir_prestacao_de_contas_v2_async,
    gerar_relatorio_apos_acertos_async,
    gerar_demonstrativo_financeiro_async,
    gerar_relacao_bens_async,
)

logger = logging.getLogger(__name__)


class PrestacaoContaService:
    """
    Classe responsável pelo novo processo de prestação de contas.
    Por hora executado apenas quando a feature flag "novo-processo-pc" está ativa.
    """
    def __init__(self, periodo_uuid, associacao_uuid, username=""):
        try:
            self._periodo = Periodo.by_uuid(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            raise Exception(f"Período com uuid {periodo_uuid} não encontrado")

        try:
            self._associacao = Associacao.by_uuid(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            raise Exception(f"Associação com uuid {associacao_uuid} não encontrada")

        self._prestacao = PrestacaoConta.by_periodo(associacao=self._associacao, periodo=self._periodo)

        self._acoes = self._associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)
        self._contas = self._prestacao.contas_ativas_no_periodo() if self._prestacao else None
        self._username = username

    def concluir_pc(self, usuario, justificativa_acertos_pendentes):
        logger.info(f"Conclusão de PC V2. Período:{self._periodo.referencia} Associação:{self._associacao.nome}")

        dados = concluir_prestacao_de_contas(
            associacao=self._associacao,
            periodo=self._periodo,
            usuario=usuario,
            monitoraPc=True,
        )
        prestacao_de_contas = dados["prestacao"]

        erro_pc = dados["erro"]
        if erro_pc:
            raise Exception(erro_pc)
        else:
            task_celery_gerar_demonstrativo_financeiro = TaskCelery.objects.create(
                nome_task="gerar_demonstrativo_financeiro_async",
                usuario=usuario,
                associacao=self._associacao,
                periodo=self._periodo,
                prestacao_conta=prestacao_de_contas,
            )

            task_celery_gerar_relacao_bens = TaskCelery.objects.create(
                nome_task="gerar_relacao_bens_async",
                usuario=usuario,
                associacao=self._associacao,
                periodo=self._periodo,
                prestacao_conta=prestacao_de_contas,
            )

            chain_tasks = chain(
                concluir_prestacao_de_contas_v2_async.s(
                    periodo_uuid=self._periodo.uuid,
                    associacao_uuid=self._associacao.uuid,
                    username=usuario.username,
                    e_retorno_devolucao=dados["e_retorno_devolucao"],
                    requer_geracao_documentos=dados["requer_geracao_documentos"],
                    requer_geracao_fechamentos=dados["requer_geracao_fechamentos"],
                    requer_acertos_em_extrato=dados["requer_acertos_em_extrato"],
                    justificativa_acertos_pendentes=justificativa_acertos_pendentes,
                ),
                group(
                    gerar_demonstrativo_financeiro_async.si(
                        task_celery_gerar_demonstrativo_financeiro.uuid,
                        prestacao_de_contas.uuid,
                        self._periodo.uuid,
                    ),
                    gerar_relacao_bens_async.si(
                        task_celery_gerar_relacao_bens.uuid,
                        prestacao_de_contas.uuid
                    )
                )

            )

            id_task_chain = chain_tasks.apply_async(countdown=1)

            TaskCelery.objects.create(
                nome_task="concluir_prestacao_de_contas_async",
                usuario=usuario,
                associacao=self._associacao,
                periodo=self._periodo,
                prestacao_conta=prestacao_de_contas,
                id_task_assincrona=id_task_chain,
            )
            if dados["e_retorno_devolucao"]:
                task_celery_geracao_relatorio_apos_acerto = TaskCelery.objects.create(
                    nome_task="gerar_relatorio_apos_acertos_async",
                    associacao=self._associacao,
                    periodo=self._periodo,
                    usuario=usuario
                )

                id_task_geracao_relatorio_apos_acerto = gerar_relatorio_apos_acertos_async.apply_async(
                    (
                        task_celery_geracao_relatorio_apos_acerto.uuid,
                        self._associacao.uuid,
                        self._periodo.uuid,
                        usuario.name
                    ), countdown=1
                )

                task_celery_geracao_relatorio_apos_acerto.id_task_assincrona = id_task_geracao_relatorio_apos_acerto
                task_celery_geracao_relatorio_apos_acerto.save()

        return prestacao_de_contas

    def persiste_dados_docs(self):
        logger.info(f'Criando documentos do período {self._periodo} e prestacao {self._prestacao}...')

        for conta in self._contas:
            logger.info(f'Persistindo dados do demonstrativo financeiro da conta {conta}.')
            self._persiste_dados_demonstrativo_financeiro(conta_associacao=conta)

            logger.info(f'Persistindo dados da relação de bens da conta {conta}.')
            self._persiste_dados_relacao_de_bens(conta_associacao=conta)

    def _persiste_dados_demonstrativo_financeiro(self, conta_associacao, previa=False):
        logger.info(f'Criando registro do demonstrativo financeiro da conta {conta_associacao}.')

        demonstrativo, _ = DemonstrativoFinanceiro.objects.update_or_create(
            conta_associacao=conta_associacao,
            prestacao_conta=self._prestacao,
            periodo_previa=None if self._prestacao else self._periodo,
            versao=DemonstrativoFinanceiro.VERSAO_PREVIA if previa else DemonstrativoFinanceiro.VERSAO_FINAL,
            status=DemonstrativoFinanceiro.STATUS_A_PROCESSAR,
        )

        try:
            observacao_conciliacao = ObservacaoConciliacao.objects.filter(
                periodo__uuid=self._periodo.uuid,
                conta_associacao__uuid=conta_associacao.uuid
            ).first()
        except Exception:
            observacao_conciliacao = None

        logger.info(f'Persistindo dados do demonstrativo financeiro da conta {conta_associacao}.')

        dados_demonstrativo = gerar_dados_demonstrativo_financeiro(
            usuario=self._username,
            acoes=self._acoes,
            periodo=self._periodo,
            conta_associacao=conta_associacao,
            prestacao=self._prestacao,
            observacao_conciliacao=observacao_conciliacao,
            previa=previa
        )

        PersistenciaDadosDemoFinanceiro(dados=dados_demonstrativo, demonstrativo=demonstrativo)

        return demonstrativo

    def _persiste_dados_relacao_de_bens(self, conta_associacao,  previa=False):
        # TODO - Rever implementação para seguir o padrão do demonstrativo financeiro

        compras_de_capital = RateioDespesa.rateios_da_conta_associacao_no_periodo(
            conta_associacao=conta_associacao,
            periodo=self._periodo,
            aplicacao_recurso=APLICACAO_CAPITAL
        )

        if compras_de_capital.exists():

            relacao_bens = _persistir_arquivo_relacao_de_bens(
                periodo=self._periodo,
                conta_associacao=conta_associacao,
                usuario=self._username,
                prestacao=self._prestacao,
                previa=False
            )

            return relacao_bens
