from rest_framework import serializers

from ...models import PrestacaoConta
from ...services.processos_services import get_processo_sei_da_prestacao


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


    class Meta:
        model = PrestacaoConta
        fields = (
        'uuid', 'unidade_eol', 'unidade_nome', 'status', 'tecnico_responsavel', 'processo_sei', 'data_recebimento',
        'data_ultima_analise', 'periodo_uuid', 'associacao_uuid')
