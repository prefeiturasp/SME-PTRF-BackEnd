from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import AssociacaoSerializer
from sme_ptrf_apps.mandatos.api.serializers.mandato_serializer import MandatoSerializer
from ...services.composicao_service import ServicoComposicaoVigente

from ...models import Composicao


class ComposicaoSerializer(serializers.ModelSerializer):

    associacao = AssociacaoSerializer()
    mandato = MandatoSerializer()
    info_composicao_anterior = serializers.SerializerMethodField('get_info_composicao_anterior')

    def get_info_composicao_anterior(self, obj):
        if obj.mandato and obj.associacao:
            servico = ServicoComposicaoVigente(associacao=obj.associacao, mandato=obj.mandato)

            return servico.get_info_composicao_anterior() if servico.get_info_composicao_anterior() else None

        return None

    class Meta:
        model = Composicao
        fields = (
            'id',
            'uuid',
            'associacao',
            'mandato',
            'data_inicial',
            'data_final',
            'info_composicao_anterior'
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
