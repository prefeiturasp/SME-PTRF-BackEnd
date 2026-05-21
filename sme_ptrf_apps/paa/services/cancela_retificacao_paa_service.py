from django.db import transaction
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from waffle import get_waffle_flag_model
from sme_ptrf_apps.paa.models.paa import Paa
from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa
from sme_ptrf_apps.paa.models.log_replica_paa import LogReplicaPaa
from sme_ptrf_apps.paa.services.retificacao_paa_service import RetificacaoPaaService
from sme_ptrf_apps.logging.loggers import ContextualLogger


class ValidacaoCancelaRetificacao(Exception):
    pass


class RetificacaoRollbackService:

    SECTION_HANDLERS = {
        'atividades_estatutarias_paa': '_rollback_atividades_estatutarias_paa',
        'objetivos_paa': '_rollback_objetivos_paa',
        'receitas_ptrf': '_rollback_receitas_ptrf',
        'receitas_pdde': '_rollback_receitas_pdde',
        'receitas_recurso_proprio': '_rollback_receitas_recurso_proprio',
        'receitas_outros_recursos': '_rollback_receitas_outros_recursos',
        'prioridades': '_rollback_prioridades',
    }

    def __init__(self, paa: Paa, usuario):
        self.paa = paa
        self.usuario = usuario

    def executar_rollbacks(self, sessoes_afetadas):

        self._rollback_campos_simples(sessoes_afetadas)

        for nome_sessao, alteracoes in sessoes_afetadas.items():

            handler_name = self.SECTION_HANDLERS.get(nome_sessao)

            if not handler_name:
                continue

            handler = getattr(self, handler_name)

            handler(alteracoes)

    def _rollback_campos_simples(self, sessoes_afetadas):

        campos_simples = [
            'texto_introducao',
            'texto_conclusao',
        ]

        alterou = False

        for campo in campos_simples:

            if campo in sessoes_afetadas:

                setattr(
                    self.paa,
                    campo,
                    sessoes_afetadas[campo]['anterior']
                )

                alterou = True

        if alterou:
            self.paa.save()

    def _rollback_relacionados(
        self,
        alteracoes,
        queryset,
        update_callback=None,
        create_callback=None,
    ):

        objetos = {
            str(obj.uuid): obj
            for obj in queryset
        }

        for uuid, dados in alteracoes.items():

            acao = dados['acao']

            # remove itens adicionados
            if acao == 'adicionado':
                queryset.filter(uuid=uuid).delete()

            # restaura estado anterior
            elif acao == 'modificado':

                obj = objetos.get(uuid)

                if not obj:
                    continue

                anterior = dados['anterior']

                if update_callback:
                    update_callback(obj, anterior)

                else:
                    for campo, valor in anterior.items():
                        setattr(obj, campo, valor)

                    obj.save()

            # recria removidos
            elif acao == 'removido':

                dados_removidos = dados['dados']

                if create_callback:
                    create_callback(uuid, dados_removidos)


    # HANDLERS ABAIXO:

    def _rollback_atividades_estatutarias_paa(self, alteracoes):

        from sme_ptrf_apps.paa.models.atividade_estatutaria_paa import AtividadeEstatutariaPaa

        def _update_atividade_estatutaria(obj: AtividadeEstatutariaPaa, anterior):

            obj.atividade_estatutaria.nome = anterior.get('nome')
            obj.atividade_estatutaria.tipo = anterior.get('tipo')
            obj.atividade_estatutaria.ano = anterior.get('ano')
            obj.atividade_estatutaria.mes = anterior.get('mes')
            obj.atividade_estatutaria.status = anterior.get('status')
            obj.atividade_estatutaria.save()

            obj.data = anterior.data
            obj.save()

        
        def _create_atividade_estatutaria(dados: dict):
            ...
            
        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.atividadeestatutariapaa_set.all(),
            update_callback=_update_atividade_estatutaria,
            create_callback=_create_atividade_estatutaria,
        )

    def _rollback_objetivos_paa(self, alteracoes):

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.objetivopaa_set.all(),
            update_callback=self._update_objetivo,
            create_callback=self._create_objetivo,
        )

    def _rollback_receitas_ptrf(self, alteracoes):

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.receitaprevistapaa_set.all(),
            update_callback=self._update_receita_ptrf,
            create_callback=self._create_receita_ptrf,
        )

    def _rollback_receitas_pdde(self, alteracoes):

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.receitaprevistapdde_set.all(),
            update_callback=self._update_receita_pdde,
            create_callback=self._create_receita_pdde,
        )

    def _rollback_receitas_recurso_proprio(self, alteracoes):

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.recursopropriopaa_set.all(),
            update_callback=self._update_recurso_proprio,
            create_callback=self._create_recurso_proprio,
        )

    def _rollback_receitas_outros_recursos(self, alteracoes):

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.receitaprevistaoutrorecursoperiodo_set.all(),
            update_callback=self._update_outro_recurso,
            create_callback=self._create_outro_recurso,
        )

    def _rollback_prioridades(self, alteracoes):

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.prioridadepaa_set.all(),
            update_callback=self._update_prioridade,
            create_callback=self._create_prioridade,
        )


class CancelaRetificacaoPaaService(RetificacaoRollbackService):
    
    def __init__(self, paa: Paa, usuario):

        super().__init__(paa, usuario)
        
        self.retificacao_service = RetificacaoPaaService(
            paa=paa,
            usuario=usuario,
        )

        self.logger = ContextualLogger.get_logger(
            __name__,
            operacao='Cancela Retificação PAA',
            operacao_id=None,
            username=getattr(usuario, 'username', str(usuario))
        )

        self._identifica_operacao_no_logger()

    def valida_pode_cancelar_retificacao(self):
        flag_habilitada = get_waffle_flag_model().objects.filter(
            name='paa-retificacao',
            everyone=True,
        ).exists()

        if not flag_habilitada:
            self.logger.info('Flag paa-retificacao não habilitada.')
            raise ValidacaoCancelaRetificacao(
                'Funcionalidade de retificação não está disponível.'
            )

        if self.paa.status != PaaStatusEnum.EM_RETIFICACAO.name:
            self.logger.info(f'Status do PAA é {self.paa.status}.')
            raise ValidacaoCancelaRetificacao(
                'Apenas PAA`s em retificação podem ser cancelados.'
            )

        documento_final_retificado = self.paa.documento_final()

        if not documento_final_retificado:
            return

        replica_doc_retificado = (
            self.paa.replica.historico.get('documento_retificado') or {}
        )

        uuid_replica = replica_doc_retificado.get('uuid')

        if uuid_replica != documento_final_retificado.uuid:
            self.logger.info('Não é possível cancelar a retificação pois já possui documento.')
            raise ValidacaoCancelaRetificacao(
                'Não é possível cancelar a retificação pois já possui '
                'Documento Final Retificado Gerado.'
            )
        
    @transaction.atomic
    def iniciar_cancelamento_retificacao(self):

        self.valida_pode_cancelar_retificacao()

        self.logger.info(f'Iniciando cancelamento de retificação do PAA: {self.paa.id}.')

        sessoes_afetadas = self.retificacao_service.identificar_alteracoes()

        sessoes_afetadas = (
            self.retificacao_service.identificar_alteracoes()
        )

        self.executar_rollbacks(sessoes_afetadas)

 
    def _identifica_operacao_no_logger(self):
        unidade = f'UN:{self.paa.associacao.unidade.codigo_eol}' if self.paa.associacao else ''
        periodo = f'PER:{self.paa.periodo_paa.referencia}' if self.paa.periodo_paa else ''
        paa = f'PAA:{self.paa.id}' if self.paa else ''        
        identificador = f'{unidade}-{periodo}-{paa}'
        self.logger.update_context(operacao_id=identificador)






