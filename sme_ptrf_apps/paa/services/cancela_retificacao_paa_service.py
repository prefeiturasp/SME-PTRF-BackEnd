from django.db import transaction
from waffle import get_waffle_flag_model

from sme_ptrf_apps.logging.loggers import ContextualLogger

from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models.paa import Paa

from sme_ptrf_apps.paa.models.atividade_estatutaria import (
    AtividadeEstatutaria,
)

from sme_ptrf_apps.paa.models.atividade_estatutaria_paa import (
    AtividadeEstatutariaPaa,
)

from sme_ptrf_apps.paa.models.recurso_proprio_paa import (
    RecursoProprioPaa,
)

from sme_ptrf_apps.paa.models.fonte_recurso_paa import (
    FonteRecursoPaa,
)

from sme_ptrf_apps.paa.models.receita_prevista_outro_recurso_periodo import (
    ReceitaPrevistaOutroRecursoPeriodo,
)

from sme_ptrf_apps.paa.models.outros_recursos_periodo_paa import (
    OutroRecursoPeriodoPaa,
)

from sme_ptrf_apps.paa.models.prioridade_paa import (
    PrioridadePaa,
)

from sme_ptrf_apps.paa.models.programa_pdde import (
    ProgramaPdde,
)

from sme_ptrf_apps.paa.models.acao_pdde import (
    AcaoPdde,
)

from sme_ptrf_apps.paa.models.outros_recursos import (
    OutroRecurso,
)

from sme_ptrf_apps.core.models.associacao import (
    Associacao,
)

from sme_ptrf_apps.core.models.acao_associacao import (
    AcaoAssociacao,
)

from sme_ptrf_apps.core.models.recurso import (
    Recurso,
)

from sme_ptrf_apps.despesas.models.tipo_custeio import (
    TipoCusteio,
)

from sme_ptrf_apps.despesas.models.especificacao_material_servico import (
    EspecificacaoMaterialServico,
)

from sme_ptrf_apps.paa.services.retificacao_paa_service import (
    RetificacaoPaaService,
)


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

    ###########################################################
    # HELPERS
    ###########################################################

    def _get_by_uuid_or_none(self, model, uuid):

        if not uuid:
            return None

        return model.objects.filter(uuid=uuid).first()

    def _log_inicio_secao(self, nome_sessao, alteracoes):

        self.logger.info(
            f'[ROLLBACK][{nome_sessao}] '
            f'Iniciando rollback. '
            f'Quantidade alterações: {len(alteracoes)}'
        )

    def _log_fim_secao(self, nome_sessao):

        self.logger.info(
            f'[ROLLBACK][{nome_sessao}] '
            f'Rollback concluído.'
        )

    ###########################################################
    # EXECUTOR
    ###########################################################

    def executar_rollbacks(self, sessoes_afetadas):

        self.logger.info(
            f'Iniciando execução de rollback. '
            f'Seções afetadas: {list(sessoes_afetadas.keys())}'
        )

        self._rollback_campos_simples(sessoes_afetadas)

        for nome_sessao, alteracoes in sessoes_afetadas.items():

            handler_name = self.SECTION_HANDLERS.get(nome_sessao)

            if not handler_name:
                self.logger.warning(
                    f'Nenhum handler encontrado para seção: '
                    f'{nome_sessao}'
                )
                continue

            handler = getattr(self, handler_name, None)

            if not handler:
                self.logger.warning(
                    f'Handler {handler_name} não encontrado.'
                )
                continue

            self._log_inicio_secao(
                nome_sessao,
                alteracoes,
            )

            handler(alteracoes)

            self._log_fim_secao(nome_sessao)

    ###########################################################
    # CAMPOS SIMPLES
    ###########################################################

    def _rollback_campos_simples(self, sessoes_afetadas):

        campos_simples = [
            'texto_introducao',
            'texto_conclusao',
        ]

        alterou = False

        for campo in campos_simples:

            if campo not in sessoes_afetadas:
                continue

            valor_anterior = (
                sessoes_afetadas[campo]['anterior']
            )

            self.logger.info(
                f'Restaurando campo simples: {campo}'
            )

            setattr(
                self.paa,
                campo,
                valor_anterior,
            )

            alterou = True

        if alterou:

            self.paa.save()

            self.logger.info(
                'Campos simples restaurados com sucesso.'
            )

    ###########################################################
    # ENGINE GENÉRICA
    ###########################################################

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

            self.logger.info(
                f'[ROLLBACK ITEM] '
                f'uuid={uuid} '
                f'acao={acao}'
            )

            try:

                ###################################################
                # REMOVE ADICIONADOS
                ###################################################

                if acao == 'adicionado':

                    queryset.filter(uuid=uuid).delete()

                    self.logger.info(
                        f'Item removido uuid={uuid}'
                    )

                ###################################################
                # RESTAURA MODIFICADOS
                ###################################################

                elif acao == 'modificado':

                    obj = objetos.get(uuid)

                    if not obj:

                        self.logger.warning(
                            f'Objeto não encontrado '
                            f'para rollback uuid={uuid}'
                        )

                        continue

                    anterior = dados['anterior']

                    if update_callback:

                        update_callback(
                            obj,
                            anterior,
                            uuid,
                        )

                    else:

                        for campo, valor in anterior.items():
                            setattr(obj, campo, valor)

                        obj.save()

                    self.logger.info(
                        f'Item restaurado uuid={uuid}'
                    )

                ###################################################
                # RECRIA REMOVIDOS
                ###################################################

                elif acao == 'removido':

                    dados_removidos = dados['dados']

                    if create_callback:
                        create_callback(
                            uuid,
                            dados_removidos,
                        )

                    self.logger.info(
                        f'Item recriado uuid={uuid}'
                    )

            except Exception as e:

                self.logger.exception(
                    f'Erro ao executar rollback '
                    f'uuid={uuid} '
                    f'acao={acao} '
                    f'erro={str(e)}'
                )

                raise

    ###########################################################
    # HANDLERS
    ###########################################################

    def _rollback_atividades_estatutarias_paa(
        self,
        alteracoes,
    ):

        def _update_atividade_estatutaria(
            obj: AtividadeEstatutariaPaa,
            anterior,
            uuid=None,
        ):

            atividade = obj.atividade_estatutaria

            atividade.nome = anterior.get('nome')
            atividade.tipo = anterior.get('tipo')
            atividade.ano = anterior.get('ano')
            atividade.mes = anterior.get('mes')
            atividade.status = anterior.get('status')

            atividade.save()

            obj.data = anterior.get('data')

            obj.save()

        def _create_atividade_estatutaria(
            uuid: str,
            dados: dict,
        ):

            atividade_estatutaria = (
                AtividadeEstatutaria.objects.create(
                    uuid=uuid,
                    nome=dados['nome'],
                    tipo=dados['tipo'],
                    ano=dados['ano'],
                    mes=dados['mes'],
                    status=dados['status'],
                    paa_id=self.paa.id,
                )
            )

            self.paa.atividadeestatutariapaa_set.create(
                atividade_estatutaria=atividade_estatutaria,
                data=dados['data'],
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.atividadeestatutariapaa_set.all(),
            update_callback=_update_atividade_estatutaria,
            create_callback=_create_atividade_estatutaria,
        )

    def _rollback_objetivos_paa(self, alteracoes):

        def _create_objetivo(uuid: str, dados: dict):

            self.paa.objetivopaa_set.create(
                uuid=uuid,
                nome=dados['nome'],
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.objetivopaa_set.all(),
            create_callback=_create_objetivo,
        )

    def _rollback_receitas_ptrf(self, alteracoes):

        def _create_receita_ptrf(
            uuid: str,
            dados: dict,
        ):

            acao_associacao = (
                self._get_by_uuid_or_none(
                    AcaoAssociacao,
                    uuid,
                )
            )

            self.paa.receitaprevistapaa_set.create(
                acao_associacao=acao_associacao,
                previsao_valor_capital=dados['previsao_valor_capital'],
                previsao_valor_custeio=dados['previsao_valor_custeio'],
                previsao_valor_livre=dados['previsao_valor_livre'],
                saldo_congelado_custeio=dados['saldo_congelado_custeio'],
                saldo_congelado_capital=dados['saldo_congelado_capital'],
                saldo_congelado_livre=dados['saldo_congelado_livre'],
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.receitaprevistapaa_set.all(),
            create_callback=_create_receita_ptrf,
        )

    def _rollback_receitas_pdde(self, alteracoes):

        def _create_receita_pdde(
            uuid: str,
            dados: dict,
        ):

            acao_pdde = self._get_by_uuid_or_none(
                AcaoPdde,
                uuid,
            )

            self.paa.receitaprevistapdde_set.create(
                acao_pdde=acao_pdde,
                previsao_valor_capital=dados['previsao_valor_capital'],
                previsao_valor_custeio=dados['previsao_valor_custeio'],
                previsao_valor_livre=dados['previsao_valor_livre'],
                saldo_custeio=dados['saldo_custeio'],
                saldo_capital=dados['saldo_capital'],
                saldo_livre=dados['saldo_livre'],
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.receitaprevistapdde_set.all(),
            create_callback=_create_receita_pdde,
        )

    def _rollback_receitas_recurso_proprio(
        self,
        alteracoes,
    ):

        def _update_recurso_proprio(
            obj: RecursoProprioPaa,
            anterior,
            uuid=None,
        ):

            fonte_recurso, _ = (
                FonteRecursoPaa.objects.get_or_create(
                    nome=anterior['fonte_recurso']
                )
            )

            associacao = Associacao.objects.get(
                uuid=anterior['associacao']
            )

            obj.fonte_recurso = fonte_recurso
            obj.associacao = associacao
            obj.data_prevista = anterior.get('data_prevista')
            obj.descricao = anterior.get('descricao')
            obj.valor = anterior.get('valor')

            obj.save()

        def _create_recurso_proprio(
            uuid: str,
            dados: dict,
        ):

            fonte_recurso, _ = (
                FonteRecursoPaa.objects.get_or_create(
                    nome=dados['fonte_recurso']
                )
            )

            associacao = Associacao.objects.get(
                uuid=dados['associacao']
            )

            self.paa.recursopropriopaa_set.create(
                uuid=uuid,
                fonte_recurso=fonte_recurso,
                associacao=associacao,
                data_prevista=dados['data_prevista'],
                descricao=dados['descricao'],
                valor=dados['valor'],
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.recursopropriopaa_set.all(),
            update_callback=_update_recurso_proprio,
            create_callback=_create_recurso_proprio,
        )

    def _rollback_receitas_outros_recursos(
        self,
        alteracoes,
    ):

        def _update_outro_recurso(
            obj: ReceitaPrevistaOutroRecursoPeriodo,
            anterior,
            uuid=None,
        ):

            outro_recurso_periodo = (
                self._get_by_uuid_or_none(
                    OutroRecursoPeriodoPaa,
                    uuid,
                )
            )

            obj.outro_recurso_periodo = (
                outro_recurso_periodo
            )

            obj.previsao_valor_capital = (
                anterior.get('previsao_valor_capital')
            )

            obj.previsao_valor_custeio = (
                anterior.get('previsao_valor_custeio')
            )

            obj.previsao_valor_livre = (
                anterior.get('previsao_valor_livre')
            )

            obj.saldo_custeio = (
                anterior.get('saldo_custeio')
            )

            obj.saldo_capital = (
                anterior.get('saldo_capital')
            )

            obj.saldo_livre = (
                anterior.get('saldo_livre')
            )

            obj.save()

        def _create_outro_recurso(
            uuid: str,
            dados: dict,
        ):

            outro_recurso_periodo = (
                self._get_by_uuid_or_none(
                    OutroRecursoPeriodoPaa,
                    uuid,
                )
            )

            self.paa.receitaprevistaoutrorecursoperiodo_set.create(
                outro_recurso_periodo=outro_recurso_periodo,
                previsao_valor_capital=dados['previsao_valor_capital'],
                previsao_valor_custeio=dados['previsao_valor_custeio'],
                previsao_valor_livre=dados['previsao_valor_livre'],
                saldo_custeio=dados['saldo_custeio'],
                saldo_capital=dados['saldo_capital'],
                saldo_livre=dados['saldo_livre'],
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.receitaprevistaoutrorecursoperiodo_set.all(),
            update_callback=_update_outro_recurso,
            create_callback=_create_outro_recurso,
        )

    def _rollback_prioridades(self, alteracoes):

        def _resolve_prioridade_relations(dados):

            return {
                'recurso': Recurso.objects.filter(
                    nome=dados['recurso']
                ).first(),

                'acao_associacao': self._get_by_uuid_or_none(
                    AcaoAssociacao,
                    dados.get('acao_associacao_uuid'),
                ),

                'programa_pdde': self._get_by_uuid_or_none(
                    ProgramaPdde,
                    dados.get('programa_pdde_uuid'),
                ),

                'acao_pdde': self._get_by_uuid_or_none(
                    AcaoPdde,
                    dados.get('acao_pdde_uuid'),
                ),

                'outro_recurso': self._get_by_uuid_or_none(
                    OutroRecurso,
                    dados.get('outro_recurso_uuid'),
                ),

                'tipo_despesa_custeio': (
                    self._get_by_uuid_or_none(
                        TipoCusteio,
                        dados.get('tipo_despesa_custeio_uuid'),
                    )
                ),

                'especificacao_material': (
                    self._get_by_uuid_or_none(
                        EspecificacaoMaterialServico,
                        dados.get(
                            'especificacao_material_uuid'
                        ),
                    )
                ),
            }

        def _update_prioridade(
            obj: PrioridadePaa,
            anterior,
            uuid=None,
        ):

            relacoes = (
                _resolve_prioridade_relations(anterior)
            )

            obj.prioridade = anterior['prioridade']
            obj.tipo_aplicacao = anterior['tipo_aplicacao']
            obj.valor_total = anterior['valor_total']

            obj.recurso = relacoes['recurso']
            obj.acao_associacao = relacoes['acao_associacao']
            obj.programa_pdde = relacoes['programa_pdde']
            obj.acao_pdde = relacoes['acao_pdde']
            obj.outro_recurso = relacoes['outro_recurso']

            obj.tipo_despesa_custeio = (
                relacoes['tipo_despesa_custeio']
            )

            obj.especificacao_material = (
                relacoes['especificacao_material']
            )

            obj.save()

        def _create_prioridade(
            uuid: str,
            dados: dict,
        ):

            relacoes = (
                _resolve_prioridade_relations(dados)
            )

            self.paa.prioridadepaa_set.create(
                uuid=uuid,
                prioridade=dados['prioridade'],
                tipo_aplicacao=dados['tipo_aplicacao'],
                valor_total=dados['valor_total'],

                recurso=relacoes['recurso'],
                acao_associacao=relacoes['acao_associacao'],
                programa_pdde=relacoes['programa_pdde'],
                acao_pdde=relacoes['acao_pdde'],
                outro_recurso=relacoes['outro_recurso'],

                tipo_despesa_custeio=(
                    relacoes['tipo_despesa_custeio']
                ),

                especificacao_material=(
                    relacoes['especificacao_material']
                ),
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.prioridadepaa_set.all(),
            update_callback=_update_prioridade,
            create_callback=_create_prioridade,
        )


class CancelaRetificacaoPaaService(
    RetificacaoRollbackService
):

    def __init__(self, paa: Paa, usuario):

        super().__init__(paa, usuario)

        self.retificacao_service = (
            RetificacaoPaaService(
                paa=paa,
                usuario=usuario,
            )
        )

        self.logger = ContextualLogger.get_logger(
            __name__,
            operacao='Cancela Retificação PAA',
            operacao_id=None,
            username=getattr(
                usuario,
                'username',
                str(usuario),
            )
        )

        self._identifica_operacao_no_logger()

    ###########################################################
    # VALIDAÇÕES
    ###########################################################

    def valida_pode_cancelar_retificacao(self):

        flag_habilitada = (
            get_waffle_flag_model()
            .objects
            .filter(
                name='paa-retificacao',
                everyone=True,
            )
            .exists()
        )

        if not flag_habilitada:

            self.logger.info(
                'Flag paa-retificacao não habilitada.'
            )

            raise ValidacaoCancelaRetificacao(
                'Funcionalidade de retificação '
                'não está disponível.'
            )

        if self.paa.status != PaaStatusEnum.EM_RETIFICACAO.name:

            self.logger.info(
                f'Status inválido para cancelamento: '
                f'{self.paa.status}'
            )

            raise ValidacaoCancelaRetificacao(
                'Apenas PAA`s em retificação '
                'podem ser cancelados.'
            )

        documento_final_retificado = (
            self.paa.documento_final()
        )

        if not documento_final_retificado:
            return

        replica_doc_retificado = (
            self.paa.replica.historico.get(
                'documento_retificado'
            ) or {}
        )

        uuid_replica = (
            replica_doc_retificado.get('uuid')
        )

        if uuid_replica != documento_final_retificado.uuid:

            self.logger.info(
                'Documento retificado divergente '
                'do snapshot.'
            )

            raise ValidacaoCancelaRetificacao(
                'Não é possível cancelar a '
                'retificação pois já possui '
                'Documento Final Retificado Gerado.'
            )

    ###########################################################
    # EXECUÇÃO
    ###########################################################

    @transaction.atomic
    def iniciar_cancelamento_retificacao(self):

        self.valida_pode_cancelar_retificacao()

        self.logger.info(
            f'Iniciando cancelamento de '
            f'retificação do PAA {self.paa.id}'
        )

        sessoes_afetadas = (
            self.retificacao_service
            .identificar_alteracoes()
        )

        self.executar_rollbacks(
            sessoes_afetadas
        )

        self.logger.info(
            f'Rollback concluído com sucesso '
            f'para PAA {self.paa.id}'
        )

    ###########################################################
    # LOGGER
    ###########################################################

    def _identifica_operacao_no_logger(self):

        unidade = (
            f'UN:{self.paa.associacao.unidade.codigo_eol}'
            if self.paa.associacao else ''
        )

        periodo = (
            f'PER:{self.paa.periodo_paa.referencia}'
            if self.paa.periodo_paa else ''
        )

        paa = (
            f'PAA:{self.paa.id}'
            if self.paa else ''
        )

        identificador = (
            f'{unidade}-{periodo}-{paa}'
        )

        self.logger.update_context(
            operacao_id=identificador
        )
