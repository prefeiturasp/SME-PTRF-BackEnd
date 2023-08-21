from rest_framework import serializers

from ...models import CargoComposicao


class CargoComposicaoSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.mandatos.api.serializers.ocupante_cargo_serializer import OcupanteCargoSerializer
    from sme_ptrf_apps.mandatos.api.serializers.composicao_serializer import ComposicaoSerializer

    composicao = ComposicaoSerializer()
    ocupante_do_cargo = OcupanteCargoSerializer()

    class Meta:
        model = CargoComposicao
        fields = (
            'id',
            'uuid',
            'composicao',
            'ocupante_do_cargo',
            'cargo_associacao',
            'substituto',
            'substituido',
        )


class CargoComposicaoLookupSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.mandatos.api.serializers.ocupante_cargo_serializer import OcupanteCargoSerializer

    cargo_associacao_label = serializers.CharField(source='get_cargo_associacao_display')

    def get_cargo_associacao_label(self, obj):
        pass

    ocupante_do_cargo = OcupanteCargoSerializer()

    class Meta:
        model = CargoComposicao
        fields = (
            'id',
            'uuid',
            'ocupante_do_cargo',
            'cargo_associacao',
            'cargo_associacao_label',
            'substituto',
            'substituido',
        )
