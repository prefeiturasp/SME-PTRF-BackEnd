from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import AssociacaoLookupSerializer
from sme_ptrf_apps.core.models import MembroAssociacao, Associacao


class MembroAssociacaoCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    class Meta:
        model = MembroAssociacao
        exclude = ('id',)

class MembroAssociacaoListSerializer(serializers.ModelSerializer):
    associacao = AssociacaoLookupSerializer()

    class Meta:
        model = MembroAssociacao
        fields = '__all__'
