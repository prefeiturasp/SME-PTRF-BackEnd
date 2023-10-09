from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import AssociacaoSerializer
from sme_ptrf_apps.mandatos.api.serializers.mandato_serializer import MandatoSerializer

from ...models import Composicao


class ComposicaoSerializer(serializers.ModelSerializer):

    associacao = AssociacaoSerializer()
    mandato = MandatoSerializer()

    class Meta:
        model = Composicao
        fields = (
            'id',
            'uuid',
            'associacao',
            'mandato',
            'data_inicial',
            'data_final'
        )


class ComposicaoComCargosSerializer(serializers.ModelSerializer):

    from .cargo_composicao_serializer import CargoComposicaoLookupSerializer

    cargos_associacao = CargoComposicaoLookupSerializer(source='cargos_da_composicao_da_composicao', many=True)

    class Meta:
        model = Composicao
        fields = (
            'id',
            'uuid',
            'cargos_associacao',
            'data_inicial',
            'data_final'
        )
