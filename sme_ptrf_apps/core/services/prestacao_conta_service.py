import logging

from celery import chain, group, chord, Celery

from django.contrib.auth import get_user_model

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

from sme_ptrf_apps.core.services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro
from sme_ptrf_apps.core.services.persistencia_dados_demo_financeiro_service import PersistenciaDadosDemoFinanceiro
from sme_ptrf_apps.core.services.relacao_bens import _persistir_arquivo_relacao_de_bens


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
        self._e_retorno_devolucao = self._prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA if self._prestacao else False

        self._acoes = self._associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)
        self._contas = self._prestacao.contas_ativas_no_periodo() if self._prestacao else None
        self._username = username
        self._user = get_user_model().objects.get(username=self._username) if self._username else None

        # Instancia do celery
        self.app = Celery("sme_ptrf_apps")
        self.app.config_from_object("django.conf:settings", namespace="CELERY")

    @property
    def pc_requer_geracao_documentos(self):
        if self._prestacao.status in (
            PrestacaoConta.STATUS_NAO_RECEBIDA,
            PrestacaoConta.STATUS_RECEBIDA,
            PrestacaoConta.STATUS_EM_ANALISE,
            PrestacaoConta.STATUS_APROVADA,
            PrestacaoConta.STATUS_APROVADA_RESSALVA,
            PrestacaoConta.STATUS_REPROVADA,
            PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA,
        ):
            return False

        if self._prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA:
            ultima_analise = self._prestacao.analises_da_prestacao.last()
            return ultima_analise is not None and ultima_analise.requer_alteracao_em_lancamentos
        else:
            return True

    @property
    def pc_requer_geracao_fechamentos(self):
        if self._prestacao.status in (
            PrestacaoConta.STATUS_NAO_RECEBIDA,
            PrestacaoConta.STATUS_RECEBIDA,
            PrestacaoConta.STATUS_EM_ANALISE,
            PrestacaoConta.STATUS_APROVADA,
            PrestacaoConta.STATUS_APROVADA_RESSALVA,
            PrestacaoConta.STATUS_REPROVADA,
            PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA,
        ):
            return False

        if self._prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA:
            ultima_analise = self._prestacao.analises_da_prestacao.last()
            return ultima_analise is not None and ultima_analise.requer_geracao_fechamentos
        else:
            return True

    @property
    def pc_requer_acerto_em_extrato(self):

        if self._prestacao.status in (
            PrestacaoConta.STATUS_NAO_RECEBIDA,
            PrestacaoConta.STATUS_RECEBIDA,
            PrestacaoConta.STATUS_EM_ANALISE,
            PrestacaoConta.STATUS_APROVADA,
            PrestacaoConta.STATUS_APROVADA_RESSALVA,
            PrestacaoConta.STATUS_REPROVADA,
            PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA,
        ):
            return False

        if self._prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA:
            ultima_analise = self._prestacao.analises_da_prestacao.last()
            return ultima_analise is not None and ultima_analise.requer_acertos_em_extrato
        else:
            return True

    @property
    def e_retorno_devolucao(self):
        return self._e_retorno_devolucao

    def _set_pc(self):
        """Define a prestação de contas para o período e associação informados."""
        self._prestacao = PrestacaoConta.abrir(periodo=self._periodo, associacao=self._associacao)
        logger.info(f'Aberta a prestação de contas {self._prestacao}.')

        if self._prestacao.status in (PrestacaoConta.STATUS_EM_PROCESSAMENTO, PrestacaoConta.STATUS_A_PROCESSAR):
            raise Exception(f'Prestação de contas {self._prestacao} já está em processamento.')

        self._e_retorno_devolucao = self._prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA

        self._prestacao.a_processar()

        logger.info(f'Prestação de contas aguardando processamento {self._prestacao}.')

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

    def _revoke_tasks_by_id(self):
        """
        Revoke one task by the id of the celery task
        :return: None
        Examples:
            revoke_tasks_by_id(self)
        """

        tasks_ativas_da_pc = self._prestacao.tasks_celery_da_prestacao_conta.filter(
            nome_task='concluir_prestacao_de_contas_async').filter(finalizada=False).all()
        for task in tasks_ativas_da_pc:
            logger.info(f'Revoking: {task}')
            self.app.control.revoke(task_id=task.id_task_assincrona, terminate=True)
            task.registra_data_hora_finalizacao_forcada(log="Finalização forçada pela falha de PC.")

    def _reabrir_prestacao_de_contas(self):
        logger.info(f'Reabrindo a prestação de contas de uuid {self._prestacao.uuid}.')
        concluido = PrestacaoConta.reabrir(uuid=self._prestacao.uuid)
        if concluido:
            logger.info(
                f'Prestação de contas de uuid {self._prestacao.uuid} foi reaberta. Seus registros foram apagados.')
        return concluido

    def registra_falha_processo_pc(self):
        from sme_ptrf_apps.core.services import FalhaGeracaoPcService

        try:

            self._revoke_tasks_by_id()

            # Registrando falha de geracao de pc
            registra_falha_service = FalhaGeracaoPcService(
                periodo=self._periodo,
                usuario=self._user,
                associacao=self._associacao,
                prestacao_de_contas=self._prestacao
            )
            registra_falha_service.registra_falha_geracao_pc()

            ultima_analise = self._prestacao.analises_da_prestacao.last()

            if ultima_analise:
                self._prestacao.status = PrestacaoConta.STATUS_DEVOLVIDA
                self._prestacao.save()
                logger.info(
                    f"Monitoramento de PC: Prestação de contas passada para status DEVOLVIDA com sucesso.")
            else:
                reaberta = self._reabrir_prestacao_de_contas()

                if reaberta:
                    logger.info(
                        f"Monitoramento de PC: Prestação de contas reaberta com sucesso. Todos os seus "
                        f"registros foram apagados.")
                else:
                    logger.info(
                        f"Monitoramento de PC: Houve algum erro ao tentar reabrir a prestação de contas.")

        except Exception as e:
            logger.info(f"Monitoramento de PC: Houve algum erro ao no processo de monitoramento de PC. {e}")

    def resolve_registros_falha(self):
        from sme_ptrf_apps.core.services import FalhaGeracaoPcService

        usuario_notificacao = self._user
        logger.info('Iniciando a marcação como resolvido do registro de falha')
        registra_falha_service = FalhaGeracaoPcService(
            usuario=usuario_notificacao,
            periodo=self._periodo,
            associacao=self._associacao
        )
        registra_falha_service.marcar_como_resolvido()

    def terminar_processo_pc(self, e_retorno_devolucao=False):
        if not self._prestacao:
            raise Exception(f"Não existe prestação de contas para o período {self._periodo} e associação {self._associacao}.")

        logger.info(f'Terminando processo de PC do período {self._periodo} e prestacao {self._prestacao}...')

        calculo_concluido = self._prestacao.status in [PrestacaoConta.STATUS_CALCULADA, PrestacaoConta.STATUS_DEVOLVIDA_CALCULADA]

        # Verificar se todos os demonstrativos financeiros da prestacao de contas foram concluídos
        demonstrativos_concluidos = False
        for demonstrativo in self._prestacao.demonstrativos_da_prestacao.all():
            if demonstrativo.status == DemonstrativoFinanceiro.STATUS_CONCLUIDO:
                demonstrativos_concluidos = True
            else:
                demonstrativos_concluidos = False
                break

        # Verificar se todos os relatórios de bens da prestacao de contas foram concluídos
        relatorios_concluidos = False
        for relatorio in self._prestacao.relacoes_de_bens_da_prestacao.all():
            if relatorio.status == RelacaoBens.STATUS_CONCLUIDO:
                relatorios_concluidos = True
            else:
                relatorios_concluidos = False
                break

        if calculo_concluido and demonstrativos_concluidos and relatorios_concluidos:
            logger.info(f'Terminando o processo de PC do período {self._periodo} e prestacao {self._prestacao}...')
            self._prestacao.status = PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA if e_retorno_devolucao else PrestacaoConta.STATUS_NAO_RECEBIDA
            self._prestacao.save()

            self.resolve_registros_falha()

            logger.info(f'PC do período {self._periodo} e prestacao {self._prestacao} concluída.')
        else:
            logger.info(f'Houve um problema no processo de PC do período {self._periodo} e prestacao {self._prestacao}.')
            self.registra_falha_processo_pc()

    def iniciar_tasks_de_conclusao_de_pc(self, usuario, justificativa_acertos_pendentes):
        from sme_ptrf_apps.core.tasks import (
            calcular_prestacao_de_contas_async,
            gerar_relatorio_apos_acertos_async,
            gerar_demonstrativo_financeiro_async,
            gerar_relacao_bens_async,
            terminar_processo_pc_async,
        )
        logger.info(f"Conclusão de PC V2. Período:{self._periodo.referencia} Associação:{self._associacao.nome}")

        self._set_pc()

        task_celery_calcular_pc = TaskCelery.objects.create(
            nome_task="calcular_prestacao_de_contas_async",
            usuario=usuario,
            associacao=self._associacao,
            periodo=self._periodo,
            prestacao_conta=self._prestacao,
        )

        task_celery_gerar_demonstrativo_financeiro = TaskCelery.objects.create(
            nome_task="gerar_demonstrativo_financeiro_async",
            usuario=usuario,
            associacao=self._associacao,
            periodo=self._periodo,
            prestacao_conta=self._prestacao,
        )

        task_celery_gerar_relacao_bens = TaskCelery.objects.create(
            nome_task="gerar_relacao_bens_async",
            usuario=usuario,
            associacao=self._associacao,
            periodo=self._periodo,
            prestacao_conta=self._prestacao,
        )

        logger.info(f'Inicia tasks com é retorno de devolução = {self.e_retorno_devolucao}')
        chain_tasks = chain(
            calcular_prestacao_de_contas_async.s(
                task_celery_calcular_pc.uuid,
                periodo_uuid=self._periodo.uuid,
                associacao_uuid=self._associacao.uuid,
                username=usuario.username,
                e_retorno_devolucao=self.e_retorno_devolucao,
                requer_geracao_documentos=self.pc_requer_geracao_documentos,
                requer_geracao_fechamentos=self.pc_requer_geracao_fechamentos,
                requer_acertos_em_extrato=self.pc_requer_acerto_em_extrato,
                justificativa_acertos_pendentes=justificativa_acertos_pendentes,
            ),

            group(
                gerar_demonstrativo_financeiro_async.si(
                    task_celery_gerar_demonstrativo_financeiro.uuid,
                    self._prestacao.uuid,
                    self._periodo.uuid,
                ),
                gerar_relacao_bens_async.si(
                    task_celery_gerar_relacao_bens.uuid,
                    self._prestacao.uuid
                )
            ),

            terminar_processo_pc_async.si(
                self._periodo.uuid,
                self._associacao.uuid,
                usuario.username,
                self.e_retorno_devolucao
            )

        )

        chain_tasks.on_error(terminar_processo_pc_async.si(
            self._periodo.uuid,
            self._associacao.uuid,
            usuario.username,
            self.e_retorno_devolucao
        ))

        chain_tasks.apply_async(countdown=1)

        if self.e_retorno_devolucao:
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

        return self._prestacao

    def persiste_dados_docs(self):
        logger.info(f'Criando documentos do período {self._periodo} e prestacao {self._prestacao}...')

        for conta in self._contas:
            logger.info(f'Persistindo dados do demonstrativo financeiro da conta {conta}.')
            self._persiste_dados_demonstrativo_financeiro(conta_associacao=conta)

            logger.info(f'Persistindo dados da relação de bens da conta {conta}.')
            self._persiste_dados_relacao_de_bens(conta_associacao=conta)

    def atualiza_justificativa_conciliacao_original(self):
        """ Atualiza o campo observacao.justificativa_original com observacao.texto """
        for conta_associacao in self._contas:
            observacao = ObservacaoConciliacao.objects.filter(
                periodo=self._periodo,
                associacao=self._associacao,
                conta_associacao=conta_associacao,
            ).first()
            if observacao:
                observacao.justificativa_original = observacao.texto
                observacao.save()

    def calcular_pc(self):
        ...
