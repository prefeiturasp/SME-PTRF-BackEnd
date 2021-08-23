from rest_framework import serializers

from sme_ptrf_apps.core.models import PrestacaoConta, ObservacaoConciliacao
from sme_ptrf_apps.core.api.serializers import (AssociacaoCompletoSerializer, DevolucaoPrestacaoContaRetrieveSerializer,
                                                AnaliseContaPrestacaoContaRetrieveSerializer,
                                                DevolucaoAoTesouroRetrieveSerializer)
from sme_ptrf_apps.core.services.processos_services import get_processo_sei_da_prestacao

from sme_ptrf_apps.dre.api.serializers.motivo_aprovacao_ressalva_serializer import MotivoAprovacaoRessalvaSerializer


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
        return _str_devolucao_ao_tesouro(obj)

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

    associacao = AssociacaoCompletoSerializer(many=False)
    periodo_uuid = serializers.SerializerMethodField('get_periodo_uuid')
    tecnico_responsavel = TecnicoResponsavelSerializer(many=False)
    devolucoes_da_prestacao = DevolucaoPrestacaoContaRetrieveSerializer(many=True)
    processo_sei = serializers.SerializerMethodField('get_processo_sei')
    devolucao_ao_tesouro = serializers.SerializerMethodField('get_devolucao_ao_tesouro')
    analises_de_conta_da_prestacao = AnaliseContaPrestacaoContaRetrieveSerializer(many=True)
    devolucoes_ao_tesouro_da_prestacao = DevolucaoAoTesouroRetrieveSerializer(many=True)
    motivos_aprovacao_ressalva = MotivoAprovacaoRessalvaSerializer(many=True)
    arquivos_referencia = serializers.SerializerMethodField('get_arquivos_referencia')
    analise_atual = AnalisePrestacaoContaSerializer(many=False)

    def get_periodo_uuid(self, obj):
        return obj.periodo.uuid

    def get_processo_sei(self, obj):
        return get_processo_sei_da_prestacao(prestacao_contas=obj)

    def get_devolucao_ao_tesouro(self, obj):
        return _str_devolucao_ao_tesouro(obj)

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

    class Meta:
        model = PrestacaoConta
        fields = (
            'uuid',
            'status',
            'associacao',
            'periodo_uuid',
            'tecnico_responsavel',
            'data_recebimento',
            'devolucoes_da_prestacao',
            'processo_sei',
            'data_ultima_analise',
            'devolucao_ao_tesouro',
            'analises_de_conta_da_prestacao',
            'motivos_reprovacao',
            'devolucoes_ao_tesouro_da_prestacao',
            'motivos_aprovacao_ressalva',
            'outros_motivos_aprovacao_ressalva',
            'arquivos_referencia',
            'analise_atual',
        )


def _str_devolucao_ao_tesouro(obj):
    return f'{obj.total_devolucao_ao_tesouro:.2f}'.replace('.', ',') if obj.devolucao_tesouro else 'Não'
