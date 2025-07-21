from rest_framework import serializers

from ..serializers.tipo_custeio_serializer import TipoCusteioSerializer
from ...models import EspecificacaoMaterialServico


class EspecificacaoMaterialServicoSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecificacaoMaterialServico
        fields = ('uuid', 'nome')


class EspecificacaoMaterialServicoSerializer(serializers.ModelSerializer):
    tipo_custeio_objeto = TipoCusteioSerializer(read_only=True, source='tipo_custeio')

    class Meta:
        model = EspecificacaoMaterialServico
        fields = ('id', 'uuid', 'descricao', 'aplicacao_recurso', 'tipo_custeio', 'tipo_custeio_objeto', 'ativa')


class EspecificacaoMaterialServicoLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecificacaoMaterialServico
        fields = ('id', 'uuid', 'descricao', 'aplicacao_recurso', 'tipo_custeio', 'ativa')


class EspecificacaoMaterialServicoListaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspecificacaoMaterialServico
        fields = ('id', 'descricao')
