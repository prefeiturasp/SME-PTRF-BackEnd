from rest_framework import serializers

from ...models import PrestacaoConta


class PrestacaoContaLookUpSerializer(serializers.ModelSerializer):
    periodo_uuid = serializers.SerializerMethodField('get_periodo_uuid')

    def get_periodo_uuid(self, obj):
        return obj.periodo.uuid

    class Meta:
        model = PrestacaoConta
        fields = ('uuid', 'periodo_uuid', 'status')
