from rest_framework import serializers

from ...models import PrestacaoConta


class PrestacaoContaLookUpSerializer(serializers.ModelSerializer):
    periodo_uuid = serializers.SerializerMethodField('get_periodo_uuid')
    conta_associacao_uuid = serializers.SerializerMethodField('get_conta_associacao_uuid')

    def get_periodo_uuid(self, obj):
        return obj.periodo.uuid

    def get_conta_associacao_uuid(self, obj):
        return obj.conta_associacao.uuid

    class Meta:
        model = PrestacaoConta
        fields = (
        'uuid', 'periodo_uuid', 'conta_associacao_uuid', 'status', 'conciliado', 'conciliado_em', 'observacoes',
        'motivo_reabertura')
