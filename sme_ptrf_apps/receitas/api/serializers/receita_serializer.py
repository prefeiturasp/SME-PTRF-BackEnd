from rest_framework import serializers

from sme_ptrf_apps.core.models import Associacao, AcaoAssociacao, ContaAssociacao
from sme_ptrf_apps.receitas.models import Receita
from .tipo_receita_serializer import TipoReceitaSerializer
from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import ContaAssociacaoLookUpSerializer



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


class ReceitaListaSerializer(serializers.ModelSerializer):
    tipo_receita = TipoReceitaSerializer()
    acao_associacao = AcaoAssociacaoLookUpSerializer()
    conta_associacao = ContaAssociacaoLookUpSerializer()

    class Meta:
        model = Receita
        fields = (
            'uuid',
            'data',
            'valor',
            'descricao',
            'tipo_receita',
            'acao_associacao',
            'conta_associacao'
        )
