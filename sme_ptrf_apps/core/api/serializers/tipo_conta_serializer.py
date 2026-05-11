from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers.recurso_serializer import RecursoSerializer

from ...models import TipoConta, Recurso


class TipoContaSerializer(serializers.ModelSerializer):
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    recurso_completo = RecursoSerializer(source='recurso', read_only=True, required=False, allow_null=True)

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
            'recurso',
            'recurso_completo'
        )
