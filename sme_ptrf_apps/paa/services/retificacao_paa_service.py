from sme_ptrf_apps.logging.loggers import ContextualLogger
from django.db import transaction
from waffle import get_waffle_flag_model
from sme_ptrf_apps.paa.models import Paa
from sme_ptrf_apps.paa.enums import PaaStatusAndamentoEnum


class ValidacaoRetificacao(Exception):
    pass


class RetificacaoPaaService:
    def __init__(self, paa: Paa, usuario):
        self.paa = paa
        self.usuario = usuario
        self.logger = ContextualLogger.get_logger(
            __name__,
            operacao='Retificação PAA',
            username=getattr(usuario, 'username', str(usuario))
        )

    def _snapshot_objetivos_globais(self):
        result = {}
        # Lista de objetivos criados dentro do PAA (diferencia dos objetivos globais)
        objs_paa = self.paa.objetivopaa_set.values_list('uuid', flat=True)
        objs_globais = self.paa.objetivos.exclude(uuid__in=objs_paa)
        for obj in objs_globais:
            result[str(obj.uuid)] = {'nome': obj.nome}
        return result

    def _snapshot_objetivos_paa(self):
        result = {
            str(obj.uuid): {'nome': obj.nome}
            for obj in self.paa.objetivopaa_set.all()
        }
        return result

    def _snapshot_atividades_estatutarias_paa(self):
        result = {}
        # Atividade Estatutárias(Instância AtividadePrevista) Globais (Não relacionadasa nenhum PAA)
        _atvs_paa = self.paa.atividades_estatutarias.select_related('paa').filter(paa__isnull=False).all()

        # filtra todas as atividades estatutárias(Instância AtividadePrevistaPaa) relacionadas ao m2m no PAA,
        # filtrando apenas as atividades acima
        atvs_paa = self.paa.atividadeestatutariapaa_set \
            .select_related('paa', 'atividade_estatutaria') \
            .filter(atividade_estatutaria__in=_atvs_paa) \
            .all()
        for atividadepaa in atvs_paa:
            result[str(atividadepaa.atividade_estatutaria.uuid)] = {
                'nome': str(atividadepaa.atividade_estatutaria.nome),
                'tipo': str(atividadepaa.atividade_estatutaria.tipo),
                'ano': str(atividadepaa.atividade_estatutaria.ano),
                'mes': str(atividadepaa.atividade_estatutaria.mes),
                'status': str(atividadepaa.atividade_estatutaria.status),
                'data': str(atividadepaa.data),
            }
        return result

    def _snapshot_atividades_estatutarias_globais(self):
        result = {}
        # Atividade Estatutárias Globais (Não relacionadas a nenhum PAA)
        _atvs_globais = self.paa.atividades_estatutarias.select_related('paa').filter(paa__isnull=True).all()

        # filtra todas as atividades estatutárias relacionadas ao m2m no PAA, filtrando apenas as atividades globais
        atvs_globais = self.paa.atividadeestatutariapaa_set \
            .select_related('paa', 'atividade_estatutaria') \
            .filter(atividade_estatutaria__in=_atvs_globais) \
            .all()
        for atividadepaa in atvs_globais:
            result[str(atividadepaa.atividade_estatutaria.uuid)] = {
                'nome': str(atividadepaa.atividade_estatutaria.nome),
                'tipo': str(atividadepaa.atividade_estatutaria.tipo),
                'ano': str(atividadepaa.atividade_estatutaria.ano),
                'mes': str(atividadepaa.atividade_estatutaria.mes),
                'status': str(atividadepaa.atividade_estatutaria.status),
                'data': str(atividadepaa.data),
            }
        return result

    def _snapshot_receitas_ptrf(self):
        result = {}
        for receita in self.paa.receitaprevistapaa_set.select_related('acao_associacao').all():
            result[str(receita.acao_associacao.uuid)] = {
                'previsao_valor_capital': str(receita.previsao_valor_capital),
                'previsao_valor_custeio': str(receita.previsao_valor_custeio),
                'previsao_valor_livre': str(receita.previsao_valor_livre),
                'saldo_congelado_custeio': str(receita.saldo_congelado_custeio),
                'saldo_congelado_capital': str(receita.saldo_congelado_capital),
                'saldo_congelado_livre': str(receita.saldo_congelado_livre),
            }
        return result

    def _snapshot_receitas_pdde(self):
        result = {}
        for receita in self.paa.receitaprevistapdde_set.select_related('acao_pdde').all():
            result[str(receita.acao_pdde.uuid)] = {
                'previsao_valor_capital': str(receita.previsao_valor_capital),
                'previsao_valor_custeio': str(receita.previsao_valor_custeio),
                'previsao_valor_livre': str(receita.previsao_valor_livre),
                'saldo_custeio': str(receita.saldo_custeio),
                'saldo_capital': str(receita.saldo_capital),
                'saldo_livre': str(receita.saldo_livre),
            }
        return result

    def _snapshot_receitas_outros_recursos(self):
        result = {}
        for receita in self.paa.receitaprevistaoutrorecursoperiodo_set.select_related('outro_recurso_periodo').all():
            result[str(receita.outro_recurso_periodo.uuid)] = {
                'previsao_valor_capital': str(receita.previsao_valor_capital),
                'previsao_valor_custeio': str(receita.previsao_valor_custeio),
                'previsao_valor_livre': str(receita.previsao_valor_livre),
                'saldo_custeio': str(receita.saldo_custeio),
                'saldo_capital': str(receita.saldo_capital),
                'saldo_livre': str(receita.saldo_livre),
            }
        return result

    def _snapshot_receitas_recurso_proprio(self):
        result = {}
        for receita in self.paa.recursopropriopaa_set.select_related('fonte_recurso', 'associacao').all():
            result[str(receita.uuid)] = {
                'fonte_recurso': str(receita.fonte_recurso),
                'associacao': str(receita.associacao.uuid),
                'data_prevista': str(receita.data_prevista),
                'descricao': str(receita.descricao),
                'valor': str(receita.valor),
            }
        return result

    def _snapshot_prioridades(self):
        result = {}
        for prioridade in self.paa.prioridadepaa_set.all():
            result[str(prioridade.uuid)] = {
                'recurso': prioridade.recurso,
                'prioridade': prioridade.prioridade,
                'tipo_aplicacao': prioridade.tipo_aplicacao,
                'valor_total': str(prioridade.valor_total),
                'acao_associacao_uuid': str(prioridade.acao_associacao.uuid) if prioridade.acao_associacao else None,
                'programa_pdde_uuid': str(prioridade.programa_pdde.uuid) if prioridade.programa_pdde else None,
                'acao_pdde_uuid': str(prioridade.acao_pdde.uuid) if prioridade.acao_pdde else None,
                'outro_recurso_uuid': str(prioridade.outro_recurso.uuid) if prioridade.outro_recurso else None,
                'tipo_despesa_custeio_uuid': (
                    str(prioridade.tipo_despesa_custeio.uuid) if prioridade.tipo_despesa_custeio else None
                ),
                'especificacao_material_uuid': (
                    str(prioridade.especificacao_material.uuid) if prioridade.especificacao_material else None
                ),
            }
        return result

    def gerar_snapshot(self):
        self.logger.info(f'Gerando snapshot do PAA {self.paa.uuid}...')
        snapshot = {
            'texto_introducao': self.paa.texto_introducao or '',
            'texto_conclusao': self.paa.texto_conclusao or '',
            'atividades_estatutarias_globais': self._snapshot_atividades_estatutarias_globais(),
            'atividades_estatutarias_paa': self._snapshot_atividades_estatutarias_paa(),
            'objetivos_globais': self._snapshot_objetivos_globais(),
            'objetivos_paa': self._snapshot_objetivos_paa(),
            'receitas_ptrf': self._snapshot_receitas_ptrf(),
            'receitas_pdde': self._snapshot_receitas_pdde(),
            'receitas_recurso_proprio': self._snapshot_receitas_recurso_proprio(),
            'receitas_outros_recursos': self._snapshot_receitas_outros_recursos(),
            'prioridades': self._snapshot_prioridades(),
        }
        self.logger.info('Snapshot gerado com sucesso.')
        return snapshot

    def criar_replica(self):
        from sme_ptrf_apps.paa.models import ReplicaPaa

        self.logger.info(f'Criando réplica do PAA {self.paa.uuid}...')
        snapshot = self.gerar_snapshot()
        replica, criada = ReplicaPaa.objects.get_or_create(
            paa=self.paa,
            defaults={'historico': snapshot}
        )
        if criada:
            self.logger.info(f'Réplica criada com sucesso (uuid={replica.uuid}).')
        else:
            self.logger.info(f'Réplica já existente retornada sem alteração (uuid={replica.uuid}).')
        return replica

    def criar_ata_retificacao(self, justificativa):
        if not justificativa:
            raise ValidacaoRetificacao('A justificativa para iniciar a retificação deve ser informada!')
        from sme_ptrf_apps.paa.models import AtaPaa

        self.logger.info(f'Criando Ata de Retificação para o PAA {self.paa.uuid}...')
        ata = AtaPaa.objects.create(
            paa=self.paa,
            tipo_ata=AtaPaa.ATA_RETIFICACAO,
            justificativa=justificativa,
        )
        self.logger.info(f'Ata de Retificação criada com sucesso (uuid={ata.uuid}).')
        return ata

    def _comparar_campos_texto(self, historico, snapshot_atual):
        alteracoes = {}
        for campo in ('texto_introducao', 'texto_conclusao'):
            anterior = str(historico.get(campo) or '')
            atual = str(snapshot_atual.get(campo) or '')
            if anterior != atual:
                alteracoes[campo] = {'anterior': anterior, 'atual': atual}
        return alteracoes

    def _comparar_secao_dict(self, anterior, atual):
        alteracoes = {}
        for uuid_key, dados_atual in atual.items():
            dados_anterior = anterior.get(uuid_key)

            # Verifica Itens adicionados
            if dados_anterior is None:
                # utilizar linha comentada abaixo caso haja necessidade de recuperar diferença entre dados
                alteracoes[uuid_key] = {'acao': 'adicionado', 'dados': dados_atual}

            # Verifica Itens modificados
            elif dados_anterior != dados_atual:
                # utilizar linha comentada abaixo caso haja necessidade de recuperar diferença entre dados
                alteracoes[uuid_key] = {'acao': 'modificado', 'anterior': dados_anterior, 'atual': dados_atual}

        # Verifica Itens removidos
        for uuid_key in anterior:
            if uuid_key not in atual:
                alteracoes[uuid_key] = {'acao': 'removido', 'dados': anterior[uuid_key]}

        return alteracoes

    def identificar_alteracoes(self):
        """
        Compara o estado atual do PAA com o snapshot armazenado na réplica.
        Retorna um dict com os campos/seções que foram alterados.
        """
        from sme_ptrf_apps.paa.models import ReplicaPaa

        try:
            replica = self.paa.replica
        except ReplicaPaa.DoesNotExist:
            self.logger.warning(
                f'Nenhuma réplica encontrada para o PAA {self.paa.uuid}. '
                'Execute iniciar_retificacao antes de identificar alterações.'
            )
            return {}

        historico = replica.historico
        snapshot_atual = self.gerar_snapshot()

        alteracoes = self._comparar_campos_texto(historico, snapshot_atual)

        secoes_dict = (
            'objetivos_paa',
            'objetivos_globais',
            'atividades_estatutarias_paa',
            'atividades_estatutarias_globais',
            'receitas_ptrf',
            'receitas_pdde',
            'receitas_recurso_proprio',
            'receitas_outros_recursos',
            'prioridades',
        )
        for secao in secoes_dict:
            secao_alteracoes = self._comparar_secao_dict(
                historico.get(secao, {}),
                snapshot_atual.get(secao, {})
            )
            if secao_alteracoes:
                alteracoes[secao] = secao_alteracoes

        self.logger.info(
            f'Alterações identificadas no PAA {self.paa.uuid}: '
            f'{list(alteracoes.keys()) or "nenhuma"}'
        )
        return alteracoes

    def define_status_paa_em_retificacao(self):
        self.paa.set_paa_status_em_retificacao()

    def valida_pode_retificar(self):
        flags = get_waffle_flag_model()
        if not flags.objects.filter(name='paa-retificacao', everyone=True).exists():
            self.logger.info('Flag paa-retificacao não habilitada.')
            raise ValidacaoRetificacao('Funcionalidade de retificação não está disponível.')

        if self.paa.get_status_andamento() != PaaStatusAndamentoEnum.GERADO.name:
            self.logger.info(f'Status de andamento do PAA é {self.paa.get_status_andamento()}.')
            raise ValidacaoRetificacao('Apenas PAA`s gerados podem ser retificados.')

    @transaction.atomic
    def iniciar_retificacao(self, justificativa):
        """
        Fluxo completo de retificação:
        1. Cria/atualiza réplica com snapshot do estado atual.
        2. Cria Ata de Retificação com a justificativa informada.
        Retorna a réplica e a ata criadas.
        """

        self.logger.info(
            f'Iniciando retificação do PAA {self.paa.uuid} '
            f'pelo usuário {getattr(self.usuario, "username", str(self.usuario))}.'
        )
        # Valida se o PAA pode ser retificado
        self.valida_pode_retificar()
        # Cria o snapshot do PAA
        self.criar_replica()
        # Cria a Ata de Retificação com a justificativa
        self.criar_ata_retificacao(justificativa)
        # atualiza o status do PAA para Retificação
        self.define_status_paa_em_retificacao()

        self.logger.info(f'Retificação do PAA {self.paa.uuid} iniciada com sucesso.')
        return self.paa
