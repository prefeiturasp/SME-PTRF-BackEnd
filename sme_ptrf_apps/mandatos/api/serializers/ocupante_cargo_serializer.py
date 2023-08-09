from rest_framework import serializers

from ...models import OcupanteCargo


class OcupanteCargoSerializer(serializers.ModelSerializer):
    representacao_label = serializers.CharField(source='get_representacao_display')

    class Meta:
        model = OcupanteCargo
        fields = (
            'id',
            'uuid',
            'nome',
            'codigo_identificacao',
            'cargo_educacao',
            'representacao',
            'representacao_label',
            'email',
            'cpf_responsavel',
            'telefone',
            'cep',
            'bairro',
            'endereco',
        )
