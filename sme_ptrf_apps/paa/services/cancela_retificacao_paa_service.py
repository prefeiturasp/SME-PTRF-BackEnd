from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import DecimalField
from django.core.exceptions import FieldDoesNotExist
from waffle import get_waffle_flag_model
from sme_ptrf_apps.logging.loggers import ContextualLogger

from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models import (
    Paa,
    AtividadeEstatutaria,
    AtividadeEstatutariaPaa,
    RecursoProprioPaa,
    FonteRecursoPaa,
    ReceitaPrevistaOutroRecursoPeriodo,
    OutroRecursoPeriodoPaa,
    PrioridadePaa,
    ProgramaPdde,
    AcaoPdde,
    ObjetivoPaa,
    OutroRecurso,
    DocumentoPaa,
    AtaPaa,
    LogReplicaPaa,
)

from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.core.models.acao_associacao import AcaoAssociacao
from sme_ptrf_apps.despesas.models.tipo_custeio import TipoCusteio
from sme_ptrf_apps.despesas.models.especificacao_material_servico import EspecificacaoMaterialServico
from sme_ptrf_apps.paa.services.retificacao_paa_service import RetificacaoPaaService


class ValidacaoCancelaRetificacao(Exception):
    pass


class CancelaRetificacaoPaaServiceBase:
    """Infraestrutura compartilhada: paa, usuario, logger e helpers."""

    def __init__(self, paa: Paa, usuario):
        self.paa = paa
        self.usuario = usuario
        self.logger = ContextualLogger.get_logger(
            __name__,
            operacao=self._nome_operacao(),
            operacao_id=None,
            username=getattr(usuario, 'username', str(usuario)),
        )
        self._atualiza_operacao_id()

    def _nome_operacao(self) -> str:
        return 'Cancela Retificação PAA Service Base'

    def _atualiza_operacao_id(self):
        partes = []
        assoc = getattr(self.paa, 'associacao', None)
        unidade = getattr(assoc, 'unidade', None)
        if unidade:
            partes.append(f'UN:{unidade.codigo_eol}')
        periodo = getattr(self.paa, 'periodo_paa', None)
        if periodo:
            partes.append(f'PER:{periodo.referencia}')
        if self.paa:
            partes.append(f'PAA:{self.paa.id}')
        self.logger.update_context(operacao_id='-'.join(partes) or None)

    def _get_by_uuid_or_none(self, model, uuid):
        if not uuid:
            return None

        return model.objects.get(uuid=uuid)

    def _str_data_para_date(self, data: str):
        return datetime.strptime(data, '%Y-%m-%d').date()

    def _str_cash_para_decimal(self, valor: str):
        if valor in (None, ""):
            return Decimal("0.00")

        try:
            return Decimal(valor)
        except (InvalidOperation, TypeError):
            raise ValueError(f"Valor monetário inválido: {valor}")


class RollbackEngine(CancelaRetificacaoPaaServiceBase):
    """Engine genérica: sabe COMO reverter itens, independente de domínio."""

    def _log_inicio_secao(self, nome_sessao, alteracoes):
        self.logger.info(
            f'[ROLLBACK][{nome_sessao}] '
            f'Iniciando rollback. '
            f'Quantidade alterações: {len(alteracoes)}'
        )

    def _log_fim_secao(self, nome_sessao):
        self.logger.info(
            f'[ROLLBACK][{nome_sessao}] Rollback concluído.'
        )

    def _rollback_campos_simples(self, sessoes_afetadas):
        CAMPOS = ['texto_introducao', 'texto_conclusao']
        campos_alterados = []

        for campo in CAMPOS:
            if campo not in sessoes_afetadas:
                continue
            self.logger.info(f'Restaurando campo simples: {campo}')
            setattr(self.paa, campo, sessoes_afetadas[campo]['anterior'])
            campos_alterados.append(campo)

        if campos_alterados:
            self.paa.save(update_fields=campos_alterados)
            self.logger.info('Campos simples restaurados com sucesso.')

    def _rollback_relacionados(
        self,
        alteracoes,
        queryset,
        update_callback=None,
        create_callback=None,
        delete_callback=None,
        key_resolver=None,
    ):
        key_resolver = key_resolver or (lambda obj: str(obj.uuid))

        objetos = {key_resolver(obj): obj for obj in queryset}

        for uuid, dados in alteracoes.items():
            acao = dados['acao']
            self.logger.info(f'[ROLLBACK ITEM] uuid={uuid} acao={acao}')

            try:
                if acao == 'adicionado':
                    obj = objetos.get(uuid)
                    if delete_callback:
                        delete_callback(uuid)
                    elif obj:
                        obj.delete()
                    self.logger.info(f'Item removido uuid={uuid}')

                elif acao == 'modificado':
                    obj = objetos.get(uuid)
                    if not obj:
                        self.logger.warning(
                            f'Objeto não encontrado para rollback uuid={uuid}'
                        )
                        continue

                    anterior = dados['anterior']
                    if update_callback:
                        update_callback(obj, anterior, uuid)
                    else:
                        for campo, valor in anterior.items():
                            try:
                                field = obj._meta.get_field(campo)

                                if isinstance(field, DecimalField):
                                    valor = self._str_cash_para_decimal(valor)

                            except FieldDoesNotExist:
                                pass

                            setattr(obj, campo, valor)
                        obj.save()
                    self.logger.info(f'Item restaurado uuid={uuid}')

                elif acao == 'removido':
                    dados_removidos = dados['dados']
                    if create_callback:
                        create_callback(uuid, dados_removidos)
                    self.logger.info(f'Item recriado uuid={uuid}')

            except Exception as e:
                self.logger.exception(
                    f'Erro ao executar rollback '
                    f'uuid={uuid} acao={acao} erro={str(e)}'
                )
                raise ValidacaoCancelaRetificacao(
                    f'Erro ao executar rollback: {str(e)}'
                )


class PaaRollbackHandlers(RollbackEngine):
    """
    Handlers de domínio: sabe O QUE reverter para cada seção do PAA.

    SECTION_HANDLERS é um class-attr substituível por subclasses para
    adicionar ou remover seções sem sobrescrever executar_rollbacks.
    """

    SECTION_HANDLERS = {
        'atividades_estatutarias_paa': '_rollback_atividades_estatutarias_paa',
        'atividades_estatutarias_globais': '_rollback_atividades_estatutarias_globais',
        'objetivos_paa': '_rollback_objetivos_paa',
        'objetivos_globais': '_rollback_objetivos_globais',
        'receitas_ptrf': '_rollback_receitas_ptrf',
        'receitas_pdde': '_rollback_receitas_pdde',
        'receitas_recurso_proprio': '_rollback_receitas_recurso_proprio',
        'receitas_outros_recursos': '_rollback_receitas_outros_recursos',
        'prioridades': '_rollback_prioridades',
    }

    def executar_rollbacks(self, sessoes_afetadas):
        self.logger.info(
            f'Iniciando execução de rollback. '
            f'Seções afetadas: {list(sessoes_afetadas.keys())}'
        )

        self._rollback_campos_simples(sessoes_afetadas)

        for nome_sessao, alteracoes in sessoes_afetadas.items():
            handler_name = self.SECTION_HANDLERS.get(nome_sessao)
            if not handler_name:
                continue

            handler = getattr(self, handler_name, None)
            if not handler:
                continue

            self._log_inicio_secao(nome_sessao, alteracoes)
            handler(alteracoes)
            self._log_fim_secao(nome_sessao)

    # ----------------------------------------------------------
    # Handlers de seção
    # ----------------------------------------------------------

    def _rollback_atividades_estatutarias_paa(self, alteracoes):

        def _update(obj: AtividadeEstatutariaPaa, anterior, uuid=None):
            atividade = obj.atividade_estatutaria
            atividade.nome = anterior.get('nome')
            atividade.tipo = anterior.get('tipo')
            atividade.ano = anterior.get('ano')
            atividade.mes = anterior.get('mes')
            atividade.status = anterior.get('status')
            atividade.save()
            obj.data = self._str_data_para_date(anterior.get('data'))
            obj.save()

        def _create(uuid: str, dados: dict):
            atividade = AtividadeEstatutaria.objects.create(
                uuid=uuid,
                nome=dados['nome'],
                tipo=dados['tipo'],
                ano=dados['ano'],
                mes=dados['mes'],
                status=dados['status'],
                paa_id=self.paa.id,
            )
            self.paa.atividadeestatutariapaa_set.create(
                atividade_estatutaria=atividade,
                data=self._str_data_para_date(dados['data']),
            )

        def _delete(uuid: str):
            # Atividades PAA têm paa_id setado — ao desfazer 'adicionado',
            # devemos deletar tanto o vínculo quanto a AtividadeEstatutaria pai.
            try:
                atv_paa = (
                    self.paa.atividadeestatutariapaa_set
                    .select_related('atividade_estatutaria')
                    .get(atividade_estatutaria__uuid=uuid)
                )
                atividade = atv_paa.atividade_estatutaria
                atv_paa.delete()
                if atividade.paa_id:
                    atividade.delete()
            except AtividadeEstatutariaPaa.DoesNotExist:
                self.logger.warning(
                    f'AtividadeEstatutariaPaa não encontrada para delete uuid={uuid}'
                )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.atividadeestatutariapaa_set.select_related(
                'atividade_estatutaria'
            ).filter(atividade_estatutaria__paa__isnull=False),
            update_callback=_update,
            create_callback=_create,
            delete_callback=_delete,
            key_resolver=lambda obj: str(obj.atividade_estatutaria.uuid),
        )

    def _rollback_atividades_estatutarias_globais(self, alteracoes):
        # Atividades globais (paa=None): não criamos/deletamos o objeto raiz,
        # apenas gerenciamos o vínculo AtividadeEstatutariaPaa e o campo `data`.

        def _create(uuid: str, dados: dict):
            # ação 'removido' no diff → restaura o vínculo desfeito durante retificação
            try:
                atividade = AtividadeEstatutaria.objects.get(uuid=uuid)
                self.paa.atividadeestatutariapaa_set.get_or_create(
                    atividade_estatutaria=atividade,
                    defaults={
                        'data': self._str_data_para_date(dados['data'])
                    },
                )
            except AtividadeEstatutaria.DoesNotExist:
                self.logger.warning(
                    f'AtividadeEstatutaria global não encontrada uuid={uuid}'
                )

        def _update(obj: AtividadeEstatutariaPaa, anterior, uuid=None):
            # apenas o campo `data` pertence ao vínculo — os demais são do objeto global
            obj.data = self._str_data_para_date(anterior.get('data'))
            obj.save()

        def _delete(uuid: str):
            # ação 'adicionado' no diff → remove o vínculo sem tocar na AtividadeEstatutaria
            try:
                self.paa.atividadeestatutariapaa_set.filter(
                    atividade_estatutaria__uuid=uuid
                ).delete()
            except AtividadeEstatutariaPaa.DoesNotExist:
                self.logger.warning(
                    f'Vínculo global não encontrado para delete uuid={uuid}'
                )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.atividadeestatutariapaa_set.select_related(
                'atividade_estatutaria'
            ).filter(atividade_estatutaria__paa__isnull=True),
            create_callback=_create,
            update_callback=_update,
            delete_callback=_delete,
            key_resolver=lambda obj: str(obj.atividade_estatutaria.uuid),
        )

    def _rollback_objetivos_paa(self, alteracoes):

        def _create(uuid: str, dados: dict):
            self.paa.objetivopaa_set.create(uuid=uuid, nome=dados['nome'])

        def _update(obj, anterior, uuid=None):
            self.logger.info(f'Restaurando objetivo {uuid}')
            obj.nome = anterior['nome']
            obj.save()

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.objetivopaa_set.all(),
            create_callback=_create,
            update_callback=_update,
        )

    def _rollback_objetivos_globais(self, alteracoes):

        def _create(uuid: str, dados: dict):
            objetivo = self._get_by_uuid_or_none(ObjetivoPaa, uuid)
            self.paa.objetivos.add(objetivo)

        def _update(obj, anterior, uuid=None):
            pass

        def _delete(uuid):
            objetivo = self._get_by_uuid_or_none(ObjetivoPaa, uuid)
            self.paa.objetivos.remove(objetivo)

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.objetivos.all(),
            create_callback=_create,
            update_callback=_update,
            delete_callback=_delete,
        )

    def _rollback_receitas_ptrf(self, alteracoes):

        def _create(uuid: str, dados: dict):
            acao_associacao = self._get_by_uuid_or_none(AcaoAssociacao, uuid)
            self.paa.receitaprevistapaa_set.create(
                acao_associacao=acao_associacao,
                previsao_valor_capital=self._str_cash_para_decimal(dados['previsao_valor_capital']),
                previsao_valor_custeio=self._str_cash_para_decimal(dados['previsao_valor_custeio']),
                previsao_valor_livre=self._str_cash_para_decimal(dados['previsao_valor_livre']),
                saldo_congelado_custeio=self._str_cash_para_decimal(dados['saldo_congelado_custeio']),
                saldo_congelado_capital=self._str_cash_para_decimal(dados['saldo_congelado_capital']),
                saldo_congelado_livre=self._str_cash_para_decimal(dados['saldo_congelado_livre']),
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.receitaprevistapaa_set.select_related('acao_associacao').all(),
            create_callback=_create,
            key_resolver=lambda obj: str(obj.acao_associacao.uuid),
        )

    def _rollback_receitas_pdde(self, alteracoes):

        def _create(uuid: str, dados: dict):
            acao_pdde = self._get_by_uuid_or_none(AcaoPdde, uuid)
            self.paa.receitaprevistapdde_set.create(
                acao_pdde=acao_pdde,
                previsao_valor_capital=self._str_cash_para_decimal(dados['previsao_valor_capital']),
                previsao_valor_custeio=self._str_cash_para_decimal(dados['previsao_valor_custeio']),
                previsao_valor_livre=self._str_cash_para_decimal(dados['previsao_valor_livre']),
                saldo_custeio=self._str_cash_para_decimal(dados['saldo_custeio']),
                saldo_capital=self._str_cash_para_decimal(dados['saldo_capital']),
                saldo_livre=self._str_cash_para_decimal(dados['saldo_livre']),
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.receitaprevistapdde_set.select_related('acao_pdde').all(),
            create_callback=_create,
            key_resolver=lambda obj: str(obj.acao_pdde.uuid),
        )

    def _rollback_receitas_recurso_proprio(self, alteracoes):

        def _resolve(dados):
            fonte_recurso, _ = FonteRecursoPaa.objects.get_or_create(
                nome=dados['fonte_recurso']
            )
            associacao = Associacao.objects.get(uuid=dados['associacao'])
            return fonte_recurso, associacao

        def _update(obj: RecursoProprioPaa, anterior, uuid=None):
            fonte_recurso, associacao = _resolve(anterior)
            obj.fonte_recurso = fonte_recurso
            obj.associacao = associacao
            obj.data_prevista = self._str_data_para_date(anterior.get('data_prevista'))
            obj.descricao = anterior.get('descricao')
            obj.valor = self._str_cash_para_decimal(anterior.get('valor'))
            obj.save()

        def _create(uuid: str, dados: dict):
            fonte_recurso, associacao = _resolve(dados)
            self.paa.recursopropriopaa_set.create(
                uuid=uuid,
                fonte_recurso=fonte_recurso,
                associacao=associacao,
                data_prevista=dados['data_prevista'],
                descricao=dados['descricao'],
                valor=self._str_cash_para_decimal(dados['valor']),
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.recursopropriopaa_set.all(),
            update_callback=_update,
            create_callback=_create,
        )

    def _rollback_receitas_outros_recursos(self, alteracoes):

        def _update(obj: ReceitaPrevistaOutroRecursoPeriodo, anterior, uuid=None):
            # `outro_recurso_periodo` é a chave de identificação do item — não muda
            obj.previsao_valor_capital = self._str_cash_para_decimal(anterior.get('previsao_valor_capital'))
            obj.previsao_valor_custeio = self._str_cash_para_decimal(anterior.get('previsao_valor_custeio'))
            obj.previsao_valor_livre = self._str_cash_para_decimal(anterior.get('previsao_valor_livre'))
            obj.saldo_custeio = self._str_cash_para_decimal(anterior.get('saldo_custeio'))
            obj.saldo_capital = self._str_cash_para_decimal(anterior.get('saldo_capital'))
            obj.saldo_livre = self._str_cash_para_decimal(anterior.get('saldo_livre'))
            obj.save()

        def _create(uuid: str, dados: dict):
            outro_recurso_periodo = self._get_by_uuid_or_none(
                OutroRecursoPeriodoPaa, uuid
            )
            self.paa.receitaprevistaoutrorecursoperiodo_set.create(
                outro_recurso_periodo=outro_recurso_periodo,
                previsao_valor_capital=self._str_cash_para_decimal(dados['previsao_valor_capital']),
                previsao_valor_custeio=self._str_cash_para_decimal(dados['previsao_valor_custeio']),
                previsao_valor_livre=self._str_cash_para_decimal(dados['previsao_valor_livre']),
                saldo_custeio=self._str_cash_para_decimal(dados['saldo_custeio']),
                saldo_capital=self._str_cash_para_decimal(dados['saldo_capital']),
                saldo_livre=self._str_cash_para_decimal(dados['saldo_livre']),
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.receitaprevistaoutrorecursoperiodo_set.select_related(
                'outro_recurso_periodo'
            ).all(),
            update_callback=_update,
            create_callback=_create,
            key_resolver=lambda obj: str(obj.outro_recurso_periodo.uuid),
        )

    def _rollback_prioridades(self, alteracoes):

        def _resolve_relacoes(dados):
            return {
                'acao_associacao': self._get_by_uuid_or_none(
                    AcaoAssociacao, dados.get('acao_associacao_uuid')
                ),
                'programa_pdde': self._get_by_uuid_or_none(
                    ProgramaPdde, dados.get('programa_pdde_uuid')
                ),
                'acao_pdde': self._get_by_uuid_or_none(
                    AcaoPdde, dados.get('acao_pdde_uuid')
                ),
                'outro_recurso': self._get_by_uuid_or_none(
                    OutroRecurso, dados.get('outro_recurso_uuid')
                ),
                'tipo_despesa_custeio': self._get_by_uuid_or_none(
                    TipoCusteio, dados.get('tipo_despesa_custeio_uuid')
                ),
                'especificacao_material': self._get_by_uuid_or_none(
                    EspecificacaoMaterialServico,
                    dados.get('especificacao_material_uuid'),
                ),
            }

        def _update(obj: PrioridadePaa, anterior, uuid=None):
            rel = _resolve_relacoes(anterior)
            obj.prioridade = anterior['prioridade']
            obj.tipo_aplicacao = anterior['tipo_aplicacao']
            obj.valor_total = self._str_cash_para_decimal(anterior['valor_total'])
            obj.recurso = anterior['recurso']
            obj.acao_associacao = rel['acao_associacao']
            obj.programa_pdde = rel['programa_pdde']
            obj.acao_pdde = rel['acao_pdde']
            obj.outro_recurso = rel['outro_recurso']
            obj.tipo_despesa_custeio = rel['tipo_despesa_custeio']
            obj.especificacao_material = rel['especificacao_material']
            obj.save()

        def _create(uuid: str, dados: dict):
            rel = _resolve_relacoes(dados)
            self.paa.prioridadepaa_set.create(
                uuid=uuid,
                prioridade=dados['prioridade'],
                tipo_aplicacao=dados['tipo_aplicacao'],
                valor_total=self._str_cash_para_decimal(dados['valor_total']),
                recurso=dados['recurso'],
                acao_associacao=rel['acao_associacao'],
                programa_pdde=rel['programa_pdde'],
                acao_pdde=rel['acao_pdde'],
                outro_recurso=rel['outro_recurso'],
                tipo_despesa_custeio=rel['tipo_despesa_custeio'],
                especificacao_material=rel['especificacao_material'],
            )

        self._rollback_relacionados(
            alteracoes=alteracoes,
            queryset=self.paa.prioridadepaa_set.all(),
            update_callback=_update,
            create_callback=_create,
        )


class CancelaRetificacaoPaaService(PaaRollbackHandlers):
    """Orquestra a validação, rollback e limpeza do cancelamento de retificação."""

    def __init__(self, paa: Paa, usuario):
        super().__init__(paa, usuario)
        self.retificacao_service = RetificacaoPaaService(paa=paa, usuario=usuario)

    def _nome_operacao(self) -> str:
        return 'Cancela Retificação PAA'

    def valida_pode_cancelar_retificacao(self):
        # Se tem Flag
        flag_habilitada = (
            get_waffle_flag_model()
            .objects
            .filter(name='paa-retificacao', everyone=True)
            .exists()
        )

        if not flag_habilitada:
            self.logger.info('Flag paa-retificacao não habilitada.')
            raise ValidacaoCancelaRetificacao(
                'Funcionalidade de retificação não está disponível.'
            )
        # Se não é Retificação
        if self.paa.status != PaaStatusEnum.EM_RETIFICACAO.name:
            self.logger.info(
                f'Status inválido para cancelamento: {self.paa.status}'
            )
            raise ValidacaoCancelaRetificacao(
                'Apenas PAA`s em retificação podem ser cancelados.'
            )

        documento_final_retificado = self.paa.documento_final
        if not documento_final_retificado:
            return

        replica = getattr(self.paa, 'replica', None)
        if not replica:
            self.logger.error(f'PAA {self.paa.id} não possui réplica.')
            raise ValidacaoCancelaRetificacao('PAA não possui réplica.')

        replica_doc_retificado = replica.historico.get('documento_retificado') or {}
        uuid_replica = replica_doc_retificado.get('uuid')

        if uuid_replica != documento_final_retificado.uuid:
            self.logger.info('Documento retificado divergente do snapshot.')
            raise ValidacaoCancelaRetificacao(
                'Não é possível cancelar a retificação pois já possui '
                'Documento Final Retificado Gerado.'
            )

    @transaction.atomic
    def iniciar_cancelamento_retificacao(self):
        self.valida_pode_cancelar_retificacao()

        self.logger.info(
            f'Iniciando cancelamento de retificação do PAA {self.paa.id}'
        )

        replica = getattr(self.paa, 'replica', None)

        sessoes_afetadas = self.retificacao_service.identificar_alteracoes()
        self.logger.info(
            f'Seções afetadas identificadas: {list(sessoes_afetadas.keys())}'
        )

        self.executar_rollbacks(sessoes_afetadas)
        self._remover_documentos_previos()
        self._remover_atas_previas()
        self._restaurar_status_paa()
        self._salvar_log_replica(replica=replica)
        self._remover_replica(replica=replica)

        self.logger.info(
            f'Cancelamento de retificação concluído com sucesso '
            f'para PAA {self.paa.id}'
        )

    # limpeza
    def _remover_documentos_previos(self):
        removidos, _ = DocumentoPaa.objects.filter(
            paa=self.paa,
            versao=DocumentoPaa.VersaoChoices.PREVIA,
            retificacao=True,
        ).delete()
        self.logger.info(f'Documentos prévios removidos: {removidos}')

    def _remover_atas_previas(self):
        removidos, _ = AtaPaa.objects.filter(
            paa=self.paa,
            tipo_ata=AtaPaa.ATA_RETIFICACAO,
            previa=True,
        ).delete()
        self.logger.info(f'Atas prévias removidas: {removidos}')

    def _restaurar_status_paa(self):
        status_anterior = self.paa.status
        self.paa.set_paa_status_gerado()
        self.logger.info(
            f'Status restaurado de {status_anterior} para {self.paa.status}'
        )

    def _salvar_log_replica(self, replica):
        historico = replica.historico or {}
        versao_documento = (
            historico
            .get('documento_retificado', {})
            .get('versao_documento', 1)
        )
        LogReplicaPaa.objects.create(
            paa=self.paa,
            origem=LogReplicaPaa.CANCELAMENTO,
            replica=historico,
            numero_versao_documento=versao_documento,
        )
        self.logger.info(f'Log da réplica salvo com versão={versao_documento}')

    def _remover_replica(self, replica):
        replica_id = replica.id
        replica.delete()
        self.logger.info(f'Réplica removida id={replica_id}')
