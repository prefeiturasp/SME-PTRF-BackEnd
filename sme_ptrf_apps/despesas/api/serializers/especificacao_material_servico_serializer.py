from rest_framework import serializers

from ..serializers.tipo_custeio_serializer import TipoCusteioSerializer
from ...models import EspecificacaoMaterialServico


class EspecificacaoMaterialServicoSerializer(serializers.ModelSerializer):
    tipo_custeio = TipoCusteioSerializer()

    class Meta:
        model = EspecificacaoMaterialServico
        fields = ('id', 'descricao', 'aplicacao_recurso', 'tipo_custeio')
