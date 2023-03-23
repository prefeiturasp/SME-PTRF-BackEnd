from rest_framework import serializers

from sme_ptrf_apps.core.models import PrestacaoConta, ObservacaoConciliacao
from sme_ptrf_apps.core.api.serializers import (
    AssociacaoCompletoSerializer,
    DevolucaoPrestacaoContaRetrieveSerializer,
    DevolucaoAoTesouroRetrieveSerializer
)
from sme_ptrf_apps.core.services.processos_services import get_processo_sei_da_prestacao

from sme_ptrf_apps.dre.api.serializers.motivo_aprovacao_ressalva_serializer import MotivoAprovacaoRessalvaSerializer
from sme_ptrf_apps.dre.api.serializers.motivo_reprovacao_serializer import MotivoReprovacaoSerializer
from ....dre.models import ConsolidadoDRE


class PrestacaoContaLookUpSerializer(serializers.ModelSerializer):
    periodo_uuid = serializers.SerializerMethodField('get_periodo_uuid')

    def get_periodo_uuid(self, obj):
        return obj.periodo.uuid

    class Meta:
        model = PrestacaoConta
        fields = ('uuid', 'periodo_uuid', 'status')


class PrestacaoContaListSerializer(serializers.ModelSerializer):
    unidade_eol = serializers.SerializerMethodField('get_unidade_eol')
    unidade_nome = serializers.SerializerMethodField('get_unidade_nome')
    processo_sei = serializers.SerializerMethodField('get_processo_sei')
    periodo_uuid = serializers.SerializerMethodField('get_periodo_uuid')
    associacao_uuid = serializers.SerializerMethodField('get_associacao_uuid')
    tecnico_responsavel = serializers.SerializerMethodField('get_tecnico_responsavel')
    devolucao_ao_tesouro = serializers.SerializerMethodField('get_devolucao_ao_tesouro')
    unidade_tipo_unidade = serializers.SerializerMethodField('get_unidade_tipo_unidade')

    def get_unidade_eol(self, obj):
        return obj.associacao.unidade.codigo_eol if obj.associacao and obj.associacao.unidade else ''

    def get_unidade_nome(self, obj):
        return obj.associacao.unidade.nome if obj.associacao and obj.associacao.unidade else ''

    def get_processo_sei(self, obj):
        return get_processo_sei_da_prestacao(prestacao_contas=obj)

    def get_periodo_uuid(self, obj):
        return obj.periodo.uuid if obj.periodo else ''

    def get_associacao_uuid(self, obj):
        return obj.associacao.uuid if obj.associacao else ''

    def get_tecnico_responsavel(self, obj):
        return obj.tecnico_responsavel.nome if obj.tecnico_responsavel else ''

    def get_devolucao_ao_tesouro(self, obj):
        return obj.total_devolucao_ao_tesouro_str

    def get_unidade_tipo_unidade(self, obj):
        return obj.associacao.unidade.tipo_unidade if obj.associacao and obj.associacao.unidade else ''

    class Meta:
        model = PrestacaoConta
        fields = (
            'uuid', 'unidade_eol', 'unidade_nome', 'status', 'tecnico_responsavel', 'processo_sei', 'data_recebimento',
            'data_ultima_analise', 'periodo_uuid', 'associacao_uuid', 'devolucao_ao_tesouro', 'unidade_tipo_unidade')


class PrestacaoContaRetrieveSerializer(serializers.ModelSerializer):
    # O serializer do técnico responsável foi criado aqui porque estava
    # ocorrendo erro de importação ao tentar-se importar o serializer
    # criado no módulo DRE.
    class TecnicoResponsavelSerializer(serializers.ModelSerializer):
        class Meta:
            from ....dre.models import TecnicoDre
            model = TecnicoDre
            fields = ('uuid', 'rf', 'nome',)

    class AnalisePrestacaoContaSerializer(serializers.ModelSerializer):
        devolucao_prestacao_conta = DevolucaoPrestacaoContaRetrieveSerializer(many=False)

        class Meta:
            from sme_ptrf_apps.core.models import AnalisePrestacaoConta
            model = AnalisePrestacaoConta
            fields = ('uuid', 'id', 'devolucao_prestacao_conta', 'status', 'criado_em')

    class ConciliacaoBancariaSerializer(serializers.ModelSerializer):
        class Meta:
            from sme_ptrf_apps.core.models import ObservacaoConciliacao
            model = ObservacaoConciliacao
            fields = ('saldo_extrato')

    associacao = AssociacaoCompletoSerializer(many=False)
    periodo_uuid = serializers.SerializerMethodField('get_periodo_uuid')
    tecnico_responsavel = TecnicoResponsavelSerializer(many=False)
    devolucoes_da_prestacao = DevolucaoPrestacaoContaRetrieveSerializer(many=True)
    processo_sei = serializers.SerializerMethodField('get_processo_sei')
    devolucao_ao_tesouro = serializers.SerializerMethodField('get_devolucao_ao_tesouro')
    analises_de_conta_da_prestacao = serializers.SerializerMethodField('get_ajustes_por_analise')
    devolucoes_ao_tesouro_da_prestacao = DevolucaoAoTesouroRetrieveSerializer(many=True)
    motivos_aprovacao_ressalva = MotivoAprovacaoRessalvaSerializer(many=True)
    motivos_reprovacao = MotivoReprovacaoSerializer(many=True)
    arquivos_referencia = serializers.SerializerMethodField('get_arquivos_referencia')
    analise_atual = AnalisePrestacaoContaSerializer(many=False)
    pode_reabrir = serializers.SerializerMethodField('get_pode_reabrir')
    informacoes_conciliacao_ue = serializers.SerializerMethodField('get_conciliacao_bancaria_ue')
    referencia_consolidado_dre = serializers.SerializerMethodField('get_referencia_consolidado_dre')
    referencia_consolidado_dre_original = serializers.SerializerMethodField('get_referencia_consolidado_dre_original')

    def get_periodo_uuid(self, obj):
        return obj.periodo.uuid

    def get_processo_sei(self, obj):
        return get_processo_sei_da_prestacao(prestacao_contas=obj)

    def get_devolucao_ao_tesouro(self, obj):
        return obj.total_devolucao_ao_tesouro_str

    def get_arquivos_referencia(self, prestacao_contas):
        result = []

        for demonstrativo in prestacao_contas.demonstrativos_da_prestacao.all():
            result.append(
                {
                    'tipo': 'DF',
                    'nome': f'Demonstrativo Financeiro da Conta {demonstrativo.conta_associacao.tipo_conta.nome}',
                    'uuid': f'{demonstrativo.uuid}',
                    'conta_uuid': f'{demonstrativo.conta_associacao.uuid}'
                }
            )

        for rel_bens in prestacao_contas.relacoes_de_bens_da_prestacao.all():
            result.append(
                {
                    'tipo': 'RB',
                    'nome': f'Relação de Bens da Conta {rel_bens.conta_associacao.tipo_conta.nome}',
                    'uuid': f'{rel_bens.uuid}',
                    'conta_uuid': f'{rel_bens.conta_associacao.uuid}'
                }
            )

        extratos = ObservacaoConciliacao.objects.filter(
            associacao=prestacao_contas.associacao).filter(periodo=prestacao_contas.periodo)

        for extrato in extratos:
            if extrato.comprovante_extrato:
                result.append(
                    {
                        'tipo': 'EB',
                        'nome': f'Extrato Bancário da Conta {extrato.conta_associacao.tipo_conta.nome}',
                        'uuid': f'{extrato.uuid}',
                        'conta_uuid': f'{extrato.conta_associacao.uuid}'
                    }
                )
        return result

    def get_conciliacao_bancaria_ue(self, prestacao_contas):
        result = []

        for conciliacao in prestacao_contas.associacao.observacoes_conciliacao_da_associacao.all():
            result.append({
                'conta_uuid': f'{conciliacao.conta_associacao.uuid}',
                'data_extrato': conciliacao.data_extrato,
                'saldo_extrato': conciliacao.saldo_extrato,
                'periodo_uuid': conciliacao.periodo.uuid,
            })

        return result

    def get_pode_reabrir(self, obj):
        return obj.pode_reabrir()

    def get_ajustes_por_analise(self, prestacao_contas):
        result = []

        analise_atual = prestacao_contas.analise_atual
        analises_de_contas = []

        if analise_atual:
            analises_de_contas = analise_atual.analises_de_extratos.all()
        else:
            if prestacao_contas.analises_da_prestacao.all():
                ultima_analise = prestacao_contas.analises_da_prestacao.latest('id')
                if ultima_analise:
                    analises_de_contas = ultima_analise.analises_de_extratos.all()

        for analise in analises_de_contas:
            result.append(
                {
                    "uuid": f'{analise.uuid}',
                    "prestacao_conta": f'{analise.prestacao_conta.uuid}',
                    "conta_associacao": {
                        "uuid": f'{analise.conta_associacao.uuid}',
                        "tipo_conta": {
                            "uuid": f'{analise.conta_associacao.tipo_conta.uuid}',
                            "id": analise.conta_associacao.tipo_conta.id,
                            "nome": analise.conta_associacao.tipo_conta.nome,
                            "apenas_leitura": analise.conta_associacao.tipo_conta.apenas_leitura
                        },
                        "banco_nome": analise.conta_associacao.banco_nome,
                        "agencia": analise.conta_associacao.agencia,
                        "numero_conta": analise.conta_associacao.numero_conta
                    },
                    "data_extrato": analise.data_extrato,
                    "saldo_extrato": analise.saldo_extrato,
                    "analise_prestacao_conta": f'{analise.analise_prestacao_conta.uuid}'
                }
            )

        return result

    def get_referencia_consolidado_dre(self, obj):
        return obj.get_referencia_do_consolidado

    def get_referencia_consolidado_dre_original(self, obj):
        if(obj.consolidado_dre and obj.consolidado_dre.id):
            consolidado_vinculado_id = obj.consolidado_dre.id

            while consolidado_vinculado_id:
                consolidado_anterior = ConsolidadoDRE.objects.get(id=consolidado_vinculado_id)
                if consolidado_anterior and consolidado_anterior.consolidado_retificado_id:
                    consolidado_vinculado_id = consolidado_anterior.consolidado_retificado_id
                else:
                    consolidado_original = ConsolidadoDRE.objects.get(id=consolidado_anterior.id)
                    return consolidado_original.referencia if consolidado_original and consolidado_original.referencia else ""

    class Meta:
        model = PrestacaoConta
        fields = (
            'uuid',
            'status',
            'associacao',
            'periodo_uuid',
            'tecnico_responsavel',
            'data_recebimento',
            'data_recebimento_apos_acertos',
            'devolucoes_da_prestacao',
            'processo_sei',
            'data_ultima_analise',
            'devolucao_ao_tesouro',
            'analises_de_conta_da_prestacao',
            'motivos_reprovacao',
            'outros_motivos_reprovacao',
            'devolucoes_ao_tesouro_da_prestacao',
            'motivos_aprovacao_ressalva',
            'outros_motivos_aprovacao_ressalva',
            'arquivos_referencia',
            'analise_atual',
            'recomendacoes',
            'pode_reabrir',
            'informacoes_conciliacao_ue',
            'publicada',
            'referencia_consolidado_dre',
            'referencia_consolidado_dre_original',
            'justificativa_pendencia_realizacao',
            'em_retificacao'
        )


class PrestacaoContaListRetificaveisSerializer(serializers.ModelSerializer):
    unidade_eol = serializers.SerializerMethodField('get_unidade_eol')
    unidade_nome = serializers.SerializerMethodField('get_unidade_nome')
    unidade_tipo_unidade = serializers.SerializerMethodField('get_unidade_tipo_unidade')

    pode_desfazer_retificacao = serializers.SerializerMethodField('get_pode_desfazer_retificacao')
    tooltip_nao_pode_desfazer_retificacao = serializers.SerializerMethodField('get_tooltip_nao_pode_desfazer_retificacao')

    def get_unidade_eol(self, obj):
        return obj.associacao.unidade.codigo_eol if obj.associacao and obj.associacao.unidade else ''

    def get_unidade_nome(self, obj):
        return obj.associacao.unidade.nome if obj.associacao and obj.associacao.unidade else ''

    def get_unidade_tipo_unidade(self, obj):
        return obj.associacao.unidade.tipo_unidade if obj.associacao and obj.associacao.unidade else ''

    def get_pode_desfazer_retificacao(self, obj):
        return obj.pode_desfazer_retificacao

    def get_tooltip_nao_pode_desfazer_retificacao(self, obj):
        return obj.tooltip_nao_pode_desfazer_retificacao

    class Meta:
        model = PrestacaoConta
        fields = (
            'uuid',
            'unidade_eol',
            'unidade_nome',
            'unidade_tipo_unidade',
            'pode_desfazer_retificacao',
            'tooltip_nao_pode_desfazer_retificacao',
        )

