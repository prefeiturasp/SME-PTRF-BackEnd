from rest_framework import serializers

from ...models import TipoConta, Recurso


class TipoContaSerializer(serializers.ModelSerializer):
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    class Meta:
        model = TipoConta
        fields = (
            'uuid',
            'id',
            'nome',
            'banco_nome',
            'agencia',
            'numero_conta',
            'numero_cartao',
            'apenas_leitura',
            'permite_inativacao',
            'recurso'
        )
