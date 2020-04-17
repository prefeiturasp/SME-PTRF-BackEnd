import logging
from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from sme_ptrf_apps.core.models import Associacao, AcaoAssociacao, ContaAssociacao
from sme_ptrf_apps.receitas.models import Receita, Repasse
from .tipo_receita_serializer import TipoReceitaSerializer
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
        if validated_data['tipo_receita'].nome == 'Repasse':
            repasse = Repasse.objects\
                .filter(acao_associacao__uuid=validated_data['acao_associacao'].uuid, 
                        status='PENDENTE',
                        periodo__data_inicio_realizacao_despesas__lte=validated_data['data'],
                        periodo__data_fim_realizacao_despesas__gte=validated_data['data'])\
                .order_by('-criado_em').last()

            if not repasse:
                msgError = "Repasse não encontrado."
                logger.info(msgError)
                raise ValidationError(msgError)

            valores_iguais = validated_data['valor'] == repasse.valor_total

            if not valores_iguais:
                msgError = "Valor do payload não é igual ao valor total do repasse."
                logger.info(msgError)
                raise ValidationError(msgError)

            repasse.status = 'REALIZADO'
            repasse.save()
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
