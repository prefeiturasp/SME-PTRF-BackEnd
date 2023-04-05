from rest_framework import serializers
from ...models import FalhaGeracaoPc
from .associacao_serializer import AssociacaoSerializer
from .periodo_serializer import PeriodoSerializer


class FalhaGeracaoPcSerializer(serializers.ModelSerializer):
    associacao = AssociacaoSerializer(many=False)
    periodo = PeriodoSerializer(many=False)

    ultimo_usuario = serializers.SerializerMethodField(method_name="get_usuario", required=False, allow_null=True)

    def get_usuario(self, obj):
        return obj.ultimo_usuario.username if obj.ultimo_usuario.username else ''

    class Meta:
        model = FalhaGeracaoPc
        fields = ('uuid', 'ultimo_usuario', 'associacao', 'periodo', 'data_hora_ultima_ocorrencia',
                  'qtd_ocorrencias_sucessivas', 'resolvido')
