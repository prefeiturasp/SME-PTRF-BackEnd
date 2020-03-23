from rest_framework import serializers

from ...models import EspecificacaoMaterialServico

from ..serializers.tipo_aplicacao_recurso_serializer import TipoAplicacaoRecursoSerializer
from ..serializers.tipo_custeio_serializer import TipoCusteioSerializer


class EspecificacaoMaterialServicoSerializer(serializers.ModelSerializer):
    tipo_aplicacao_recurso = TipoAplicacaoRecursoSerializer()
    tipo_custeio = TipoCusteioSerializer()

    class Meta:
        model = EspecificacaoMaterialServico
        fields = ('id', 'descricao', 'tipo_aplicacao_recurso', 'tipo_custeio')

