from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import AssociacaoLookupSerializer
from sme_ptrf_apps.core.models import ProcessoAssociacao, Associacao


class ProcessoAssociacaoCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    class Meta:
        model = ProcessoAssociacao
        fields = ('uuid', 'associacao', 'numero_processo', 'ano',)

class ProcessoAssociacaoRetrieveSerializer(serializers.ModelSerializer):
    associacao = AssociacaoLookupSerializer()

    class Meta:
        model = ProcessoAssociacao
        fields = ('uuid', 'associacao', 'numero_processo', 'ano', 'criado_em', 'alterado_em')
