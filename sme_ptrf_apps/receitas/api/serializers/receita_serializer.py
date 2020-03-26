from rest_framework import serializers

from sme_ptrf_apps.core.models import Associacao, AcaoAssociacao, ContaAssociacao
from sme_ptrf_apps.receitas.models import Receita


class ReceitaCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    conta_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ContaAssociacao.objects.all()
    )

    acao_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AcaoAssociacao.objects.all()
    )

    class Meta:
        model = Receita
        exclude = ('id',)
