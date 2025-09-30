import logging

from celery import chain, group, Celery

from django.contrib.auth import get_user_model

from sme_ptrf_apps.core.models import (
    TaskCelery,
    Periodo,
    Associacao,
    AcaoAssociacao,
    ObservacaoConciliacao,
    PrestacaoConta,
    DemonstrativoFinanceiro,
    RelacaoBens, FechamentoPeriodo,
)

from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL

from sme_ptrf_apps.core.services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro
from sme_ptrf_apps.core.services.persistencia_dados_demo_financeiro_service import PersistenciaDadosDemoFinanceiro
from sme_ptrf_apps.core.services.relacao_bens import _persistir_arquivo_relacao_de_bens
from sme_ptrf_apps.receitas.models import Receita


class PrestacaoContaService:
    """
    Classe responsável pelo novo processo de prestação de contas.
    Por hora executado apenas quando a feature flag "novo-processo-pc" está ativa.
    """

    def __init__(self, periodo_uuid, associacao_uuid, username="", logger=None):
        try:
            self._periodo = Periodo.by_uuid(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            raise Exception(f"Período com uuid {periodo_uuid} não encontrado")

        try:
            self._associacao = Associacao.by_uuid(uuid=associacao_uuid)
        except Associacao.DoesNotExist:
            raise Exception(f"Associação com uuid {associacao_uuid} não encontrada")

        self._prestacao = PrestacaoConta.by_periodo(associacao=self._associacao, periodo=self._periodo)

        # Apenas PCs devolvidas tem o campo data_recebimento preenchido
        self._e_retorno_devolucao = self._prestacao.data_recebimento is not None if self._prestacao else False

        self._acoes = self._associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)
        self._contas = self._prestacao.contas_ativas_no_periodo() if self._prestacao else None
        self._username = username
        self._user = get_user_model().objects.get(username=self._username) if self._username else None

        # Define o logger
        if not logger or not hasattr(logger, 'update_context'):
            raise Exception("É necessário informar um ContextualLogger para a execução do serviço.")
        self.logger = logger
        self._identifica_operacao_no_logger()

        # Instancia do celery
        self.app = Celery("sme_ptrf_apps")
        self.app.config_from_object("django.conf:settings", namespace="CELERY")

    def _identifica_operacao_no_logger(self):
        identificacao_unidade = f'U:{self._associacao.unidade.codigo_eol}' if self._associacao.unidade else ''
        identificacao_periodo = f'P:{self._periodo.referencia}' if self._periodo else ''
        identificacao_prestacao = f'ID:{self._prestacao.id}' if self._prestacao else ''
        identificacao_analise_pc = f'AN:{self.analise_atual_id}'
        self.logger.update_context(
            operacao='Prestação de Contas',
            operacao_id=f'{identificacao_unidade}-{identificacao_periodo}-{identificacao_prestacao}-{identificacao_analise_pc}',
            username=self._username,
        )

    @property
    def periodo(self):
        return self._periodo

    @property
    def associacao(self):
        return self._associacao

    @property
    def prestacao(self):
        return self._prestacao

    @property
    def usuario(self):
        return self._user

    @property
    def contas(self):
        return self._contas

    @property
    def acoes(self):
        return self._acoes

    @property
    def pc_e_devolucao_com_solicitacoes_mudanca(self):
        if self._e_retorno_devolucao:
            ultima_analise = self._prestacao.analises_da_prestacao.last()
            return ultima_analise is not None and ultima_analise.verifica_se_requer_alteracao_em_lancamentos(considera_realizacao=False)
        else:
            return False

    @property
    def pc_e_devolucao_com_solicitacoes_mudanca_realizadas(self):
        if self._e_retorno_devolucao:
            ultima_analise = self._prestacao.analises_da_prestacao.last()
            return ultima_analise is not None and ultima_analise.verifica_se_requer_alteracao_em_lancamentos(considera_realizacao=True)
        else:
            return False

    @property
    def pc_e_devolucao_com_solicitacao_acerto_em_extrato(self):
        if self._e_retorno_devolucao:
            ultima_analise = self._prestacao.analises_da_prestacao.last()
            return ultima_analise is not None and ultima_analise.acertos_em_extrato_requer_gerar_documentos
        else:
            return False

    @property
    def e_retorno_devolucao(self):
        return self._e_retorno_devolucao

    @property
    def requer_apagar_fechamentos(self):
        """
        Na verdade, não deveria haver fechamentos para a PC nesse caso, já que eles são apagados no ato da
        devolução quanto as solicitações de ajuste demandam alteração de lançamentos.
        Mas, por segurança, devem ser apagados casos existam nessas condições.
        """
        return self.e_retorno_devolucao and self.pc_e_devolucao_com_solicitacoes_mudanca

    @property
    def requer_apagar_documentos(self):
        """
        No caso de devoluções de PC os documentos são regerados apenas se:
            - Houver solicitações de ajustes REALIZADAS e que demandem alteração de lançamentos,
            - Houver solicitações de ajustes nas informações de extrato.
        Nesses casos, os originais precisam ser apagados para que os novos sejam gerados.
        """
        return self.e_retorno_devolucao and (
            self.pc_e_devolucao_com_solicitacoes_mudanca_realizadas or self.pc_e_devolucao_com_solicitacao_acerto_em_extrato)

    @property
    def requer_criar_fechamentos(self):
        """
        Fechamentos devem ser criados nas seguintes situações:
            - Na primeira geração de uma PC (quando não é uma devolução)
            - Devoluções com solicitações de ajustes que demandem alteração de lançamentos, realizadas ou não
        """
        return (not self.e_retorno_devolucao) or self.pc_e_devolucao_com_solicitacoes_mudanca

    @property
    def requer_gerar_documentos(self):
        """
        Os dados para os documentos da PC precisam ser calculados e persistidos nas seguintes situações:
            - Na primeira geração de uma PC (quando não é uma devolução)
            - Houver solicitações de ajustes REALIZADAS e que demandem alteração de lançamentos,
            - Houver solicitações de ajustes nas informações de extrato.
        Além disso, qualquer prévia de documento deve ser apagada, nas mesmas situações.
        """
        return (not self.e_retorno_devolucao) or (
            self.pc_e_devolucao_com_solicitacoes_mudanca_realizadas or self.pc_e_devolucao_com_solicitacao_acerto_em_extrato)

    @property
    def analise_atual_id(self):
        ultima_analise = None
        if self._e_retorno_devolucao:
            ultima_analise = self._prestacao.analises_da_prestacao.last()
        return ultima_analise.id if ultima_analise else 0

    @classmethod
    def from_prestacao_conta_uuid(cls, prestacao_conta_uuid, username="", logger=None):
        try:
            prestacao = PrestacaoConta.by_uuid(uuid=prestacao_conta_uuid)
        except PrestacaoConta.DoesNotExist:
            raise Exception(f"Prestação de Conta com uuid {prestacao_conta_uuid} não encontrada")

        periodo_uuid = prestacao.periodo.uuid
        associacao_uuid = prestacao.associacao.uuid

        return cls(periodo_uuid, associacao_uuid, username, logger)

    def _set_pc(self):
        """Define a prestação de contas para o período e associação informados."""
        self._prestacao = PrestacaoConta.abrir(periodo=self._periodo, associacao=self._associacao)
        self._identifica_operacao_no_logger()

        self.logger.info(f'Aberta a prestação de contas {self._prestacao}.')

        if self._prestacao.status in (PrestacaoConta.STATUS_EM_PROCESSAMENTO, PrestacaoConta.STATUS_A_PROCESSAR):
            raise Exception(f'Prestação de contas {self._prestacao} já está em processamento.')

        self._e_retorno_devolucao = self._prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA

        self._prestacao.a_processar()

        self.logger.info(f'PC {self._prestacao} aguardando processamento.')

    def _persiste_dados_demonstrativo_financeiro(self, conta_associacao, previa=False):
        self.logger.info(f'Criando registro do demonstrativo financeiro da conta {conta_associacao}.')

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

        self.logger.info(f'Persistindo dados do demonstrativo financeiro da conta {conta_associacao}.')

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

    def _persiste_dados_relacao_de_bens(self, conta_associacao, previa=False):
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
            self.logger.info(f'Revoking: {task}')
            self.app.control.revoke(task_id=task.id_task_assincrona, terminate=True)
            task.registra_data_hora_finalizacao_forcada(log="Finalização forçada pela falha de PC.")

    def _reabrir_prestacao_de_contas(self):
        self.logger.info(f'Reabrindo a PC de uuid {self._prestacao.uuid}.')
        concluido = PrestacaoConta.reabrir(uuid=self._prestacao.uuid)
        if concluido:
            self.logger.info(
                f'PC de uuid {self._prestacao.uuid} foi reaberta. Seus registros foram apagados.')
        return concluido

    def trata_falha_processo_pc(self):
        from sme_ptrf_apps.core.services import FalhaGeracaoPcService

        try:

            self.logger.info(f"Revogando tasks ativas da PC {self._prestacao}.")
            self._revoke_tasks_by_id()

            self.logger.info(f"Criando um registro de falha de geração da PC {self._prestacao}.")
            registra_falha_service = FalhaGeracaoPcService(
                periodo=self._periodo,
                usuario=self._user,
                associacao=self._associacao,
                prestacao_de_contas=self._prestacao
            )
            registra_falha_service.registra_falha_geracao_pc()

            ultima_analise = self._prestacao.analises_da_prestacao.last()

            if ultima_analise:
                self.logger.info("Retorna a PC para status DEVOLVIDA.")
                self._prestacao.status = PrestacaoConta.STATUS_DEVOLVIDA
                self._prestacao.save()
                self.logger.info(f"Alterado o status da PC {self._prestacao}.")

                if ultima_analise.verifica_se_requer_alteracao_em_lancamentos(considera_realizacao=False):
                    logging.info('A devolução de PC requer alterações e por isso deve apagar os seus fechamentos.')
                    self._prestacao.apaga_fechamentos()
                    logging.info('Fechamentos apagados.')

            else:
                self.logger.info(f"Iniciando reabertura da PC {self._prestacao}.")
                reaberta = self._reabrir_prestacao_de_contas()

                if reaberta:
                    self.logger.info(
                        f"PC reaberta com sucesso. Todos os seus registros foram apagados.")
                else:
                    self.logger.warning(f"Houve algum erro ao tentar reabrir a PC.")

        except Exception as e:
            self.logger.error(f"Houve algum erro ao no registro de falha da PC. {e}", exc_info=True, stack_info=True)

    def resolve_registros_falha(self):
        from sme_ptrf_apps.core.services import FalhaGeracaoPcService

        usuario_notificacao = self._user
        self.logger.info('Verificando se há registro de falha para marcar como resolvido...')
        registra_falha_service = FalhaGeracaoPcService(
            usuario=usuario_notificacao,
            periodo=self._periodo,
            associacao=self._associacao
        )
        registra_falha_service.marcar_como_resolvido()

    def set_despesa_anterior_ao_uso_do_sistema_pc_concluida(self):
        despesas_anteriores_ao_uso_do_sistema = self.associacao.despesas.filter(
            despesa_anterior_ao_uso_do_sistema=True,
            despesa_anterior_ao_uso_do_sistema_pc_concluida=False,
        )

        for despesa in despesas_anteriores_ao_uso_do_sistema:
            despesa.set_despesa_anterior_ao_uso_do_sistema_pc_concluida()

    def terminar_processo_pc(self):
        if not self._prestacao:
            raise Exception(f"Não existe PC para o período {self._periodo} e associação {self._associacao}.")

        self.logger.info(f'Terminando processo da PC...')

        calculo_concluido = self._prestacao.status in [
            PrestacaoConta.STATUS_CALCULADA, PrestacaoConta.STATUS_DEVOLVIDA_CALCULADA]
        self.logger.info(f'PC {self._prestacao} está calculada? {calculo_concluido}')

        # Verificar se todos os demonstrativos financeiros da prestacao de contas foram concluídos
        demonstrativos_concluidos = False  # Deve ter ao menos um demonstrativo financeiro
        for demonstrativo in self._prestacao.demonstrativos_da_prestacao.all():
            if demonstrativo.status == DemonstrativoFinanceiro.STATUS_CONCLUIDO:
                demonstrativos_concluidos = True
            else:
                self.logger.info(f'Demonstrativo financeiro {demonstrativo} não está concluído.')
                demonstrativos_concluidos = False
                break

        self.logger.info(
            f'Todos os demonstrativos financeiros da PC {self._prestacao} estão concluídos? {demonstrativos_concluidos}')

        # Verificar se todos os relatórios de bens da prestacao de contas foram concluídos
        relatorios_concluidos = True  # Não é obrigatório ter relatórios de bens, mas se tiver, todos devem estar concluídos
        for relatorio in self._prestacao.relacoes_de_bens_da_prestacao.all():
            if relatorio.status != RelacaoBens.STATUS_CONCLUIDO:
                self.logger.info(f'Relatório de bens {relatorio} não está concluído.')
                relatorios_concluidos = False
                break

        self.logger.info(
            f'Todos os relatórios de bens da PC {self._prestacao} estão concluídos? {relatorios_concluidos}')

        if calculo_concluido and demonstrativos_concluidos and relatorios_concluidos:
            self.logger.info(f'Terminando o processo da PC {self._prestacao}...')
            self._prestacao.status = PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA if self.e_retorno_devolucao else PrestacaoConta.STATUS_NAO_RECEBIDA
            self._prestacao.save()

            self.set_despesa_anterior_ao_uso_do_sistema_pc_concluida()

            self.resolve_registros_falha()

            self.logger.info(f'PC {self._prestacao} concluída.')
        else:
            self.logger.warning(f'Houve um problema no processo da PC {self._prestacao}.')
            self.trata_falha_processo_pc()
            self.logger.warning(f'Feito o roll back do cálculo para a situação antes do início do processo de PC.')

    def iniciar_tasks_de_conclusao_de_pc(self, usuario, justificativa_acertos_pendentes):
        from sme_ptrf_apps.core.tasks import (
            calcular_prestacao_de_contas_async,
            gerar_relatorio_apos_acertos_v2_async,
            gerar_demonstrativo_financeiro_async,
            gerar_relacao_bens_async,
            terminar_processo_pc_async,
        )

        self._set_pc()

        self.logger.info(f"Conclusão de PC V2. Período:{self._periodo.referencia} Associação:{self._associacao.nome}")

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

        task_celery_terminar_processo_pc = TaskCelery.objects.create(
            nome_task="terminar_processo_pc_async",
            usuario=usuario,
            associacao=self._associacao,
            periodo=self._periodo,
            prestacao_conta=self._prestacao,
        )

        self.logger.info(f'Criando Celery Chain.', extra={
                         'observacao': f'Parâmetro retorno de devolução = {self.e_retorno_devolucao}'})
        chain_tasks = chain(
            calcular_prestacao_de_contas_async.s(
                task_celery_calcular_pc.uuid,
                periodo_uuid=self._periodo.uuid,
                associacao_uuid=self._associacao.uuid,
                username=usuario.username,
                justificativa_acertos_pendentes=justificativa_acertos_pendentes,
            ),

            group(
                gerar_demonstrativo_financeiro_async.si(
                    task_celery_gerar_demonstrativo_financeiro.uuid,
                    self._prestacao.uuid,
                    username=usuario.username,
                ),
                gerar_relacao_bens_async.si(
                    task_celery_gerar_relacao_bens.uuid,
                    self._prestacao.uuid,
                    username=usuario.username,
                )
            ),

            terminar_processo_pc_async.si(
                self._periodo.uuid,
                self._associacao.uuid,
                username=usuario.username,
                id_task=task_celery_terminar_processo_pc.uuid,
            )

        )

        chain_tasks.on_error(terminar_processo_pc_async.si(
            self._periodo.uuid,
            self._associacao.uuid,
            username=usuario.username,
            id_task=task_celery_terminar_processo_pc.uuid,
        ))

        chain_tasks.apply_async(countdown=1)

        if self.e_retorno_devolucao:
            task_celery_geracao_relatorio_apos_acerto = TaskCelery.objects.create(
                nome_task="gerar_relatorio_apos_acertos_v2_async",
                associacao=self._associacao,
                periodo=self._periodo,
                usuario=usuario
            )

            gerar_relatorio_apos_acertos_v2_async.apply_async(
                (
                    task_celery_geracao_relatorio_apos_acerto.uuid,
                    self._associacao.uuid,
                    self._periodo.uuid,
                    usuario.username
                ), countdown=1
            )

            self.logger.info('Celery chain criada com sucesso.')

        return self._prestacao

    def persiste_dados_docs(self):
        self.logger.info(f'Persistindo dados dos documentos da PC {self.prestacao}...')

        for conta in self._contas:
            self.logger.info(f'Persistindo dados do demonstrativo financeiro da conta {conta}.')
            self._persiste_dados_demonstrativo_financeiro(conta_associacao=conta)

            self.logger.info(f'Persistindo dados da relação de bens da conta {conta}.')
            self._persiste_dados_relacao_de_bens(conta_associacao=conta)
            self.logger.info(f'Dados dos documentos da {self.prestacao} persistidos para posterior geração dos PDFs.')

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

    def criar_fechamentos(self):
        self.logger.info(f'Criando fechamentos.')
        for conta in self.contas:
            self.logger.info(f'Criando fechamentos da conta {conta}.')
            for acao in self.acoes:
                self.logger.info(f'Criando fechamentos da ação {acao}.')
                totais_receitas = Receita.totais_por_acao_associacao_no_periodo(
                    acao_associacao=acao,
                    periodo=self.periodo,
                    conta=conta
                )
                totais_despesas = RateioDespesa.totais_por_acao_associacao_no_periodo(
                    acao_associacao=acao,
                    periodo=self.periodo,
                    conta=conta
                )
                especificacoes_despesas = RateioDespesa.especificacoes_dos_rateios_da_acao_associacao_no_periodo(
                    acao_associacao=acao,
                    periodo=self.periodo
                )
                FechamentoPeriodo.criar(
                    prestacao_conta=self.prestacao,
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
        self.logger.info(f'Fechamentos criados para a PC {self.prestacao}.')

    def apagar_previas_documentos(self):
        from ..services.relacao_bens import apagar_previas_relacao_de_bens
        self.logger.info(f'Apagando prévias de documentos...')
        for conta in self.contas:
            self.logger.info(f'Apagando prévias de relações de bens da conta {conta}.')
            apagar_previas_relacao_de_bens(periodo=self.periodo, conta_associacao=conta)

            self.logger.info(f'Apagando prévias demonstrativo financeiro da conta {conta}.')
            DemonstrativoFinanceiro.objects.filter(periodo_previa=self.periodo, conta_associacao=conta).delete()
        self.logger.info(f'Prévias de documentos apagadas.')

    def contas_com_saldo_alterado_sem_solicitacao(self):
        from sme_ptrf_apps.core.services.resumo_rescursos_service import ResumoRecursosService
        contas_alteradas = []

        if self.e_retorno_devolucao:
            contas = self.prestacao.contas_ativas_no_periodo()

            for conta in contas:
                self.logger.info(f'Conta: {conta}')
                resumo = ResumoRecursosService.resumo_recursos(
                    periodo=self.prestacao.periodo,
                    conta_associacao=conta
                )

                resumo.get_saldos_por_fechamento()
                if resumo.saldo_posterior:
                    saldo_fechamento = resumo.saldo_posterior.total_geral
                    self.logger.info(f'Saldo fechamento: {saldo_fechamento}')
                else:
                    saldo_fechamento = None
                    self.logger.info('Conta sem fechamentos')

                resumo.get_saldos_pelo_movimento()
                if resumo.saldo_posterior:
                    saldo_calculado = resumo.saldo_posterior.total_geral
                    self.logger.info(f'Saldo calculado: {saldo_calculado}')
                else:
                    saldo_calculado = 0
                    self.logger.info('Conta movimentação')

                ultima_analise = self.prestacao.ultima_analise()
                requer_acertos = ultima_analise.requer_acertos_em_saldo_na_conta_associacao(conta)

                if saldo_fechamento is not None and saldo_fechamento != saldo_calculado and not requer_acertos:
                    contas_alteradas.append(conta)

        return contas_alteradas
