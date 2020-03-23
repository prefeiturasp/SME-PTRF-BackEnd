from rest_framework import serializers

from ...models import RateioDespesa, Despesa

from ....core.api.serializers.acao_serializer import AcaoSerializer
from ....core.api.serializers.associacao_serializer import AssociacaoSerializer
from ....core.api.serializers.conta_associacao_serializer import ContaAssociacaoSerializer

from .especificacao_material_servico_serializer import EspecificacaoMaterialServicoSerializer
from .tipo_aplicacao_recurso_serializer import TipoAplicacaoRecursoSerializer
from .tipo_custeio_serializer import TipoCusteioSerializer


class RateioDespesaSerializer(serializers.ModelSerializer):
    despesa = serializers.SlugRelatedField(
        slug_field='id',
        required=False,
        queryset=Despesa.objects.all()
    )
    acao = AcaoSerializer()
    associacao = AssociacaoSerializer()
    conta_associacao = ContaAssociacaoSerializer()
    especificacao_material_servico = EspecificacaoMaterialServicoSerializer()
    tipo_aplicacao_recurso = TipoAplicacaoRecursoSerializer()
    tipo_custeio = TipoCusteioSerializer()

    class Meta:
        model = RateioDespesa
        fields = '__all__'
