import logging

from rest_framework import serializers

from sme_ptrf_apps.core.models import Associacao, AcaoAssociacao, ContaAssociacao
from sme_ptrf_apps.receitas.models import Receita, Repasse
from .tipo_receita_serializer import TipoReceitaSerializer
from ...services import atualiza_repasse_para_realizado
from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import ContaAssociacaoLookUpSerializer


logger = logging.getLogger(__name__)


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

    def create(self, validated_data):
        if validated_data['tipo_receita'].e_repasse:
            atualiza_repasse_para_realizado(validated_data)

        receita = Receita.objects.create(**validated_data)
        return receita

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
