import logging

from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import ContaAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.periodo_serializer import PeriodoLookUpSerializer
from sme_ptrf_apps.core.models import Associacao, AcaoAssociacao, ContaAssociacao, Periodo
from sme_ptrf_apps.receitas.models import Receita
from .detalhe_tipo_receita_serializer import DetalheTipoReceitaSerializer
from .tipo_receita_serializer import TipoReceitaSerializer
from ...services import atualiza_repasse_para_realizado, atualiza_repasse_para_pendente

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

    referencia_devolucao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all()
    )

    def create(self, validated_data):
        if validated_data['tipo_receita'].e_repasse:
            repasse = atualiza_repasse_para_realizado(validated_data)
            validated_data['repasse'] = repasse

        receita = Receita.objects.create(**validated_data)

        return receita

    def update(self, instance, validated_data):
        if instance.repasse:
            atualiza_repasse_para_pendente(instance)

        if validated_data['tipo_receita'].e_repasse:
            repasse = atualiza_repasse_para_realizado(validated_data)
            validated_data['repasse'] = repasse

        return super().update(instance, validated_data)

    class Meta:
        model = Receita
        exclude = ('id',)


class ReceitaListaSerializer(serializers.ModelSerializer):
    tipo_receita = TipoReceitaSerializer()
    acao_associacao = AcaoAssociacaoLookUpSerializer()
    conta_associacao = ContaAssociacaoLookUpSerializer()
    detalhe_tipo_receita = DetalheTipoReceitaSerializer()
    referencia_devolucao = PeriodoLookUpSerializer()

    class Meta:
        model = Receita
        fields = (
            'uuid',
            'data',
            'valor',
            'tipo_receita',
            'acao_associacao',
            'conta_associacao',
            'conferido',
            'categoria_receita',
            'detalhe_tipo_receita',
            'detalhe_outros',
            'referencia_devolucao',
            'notificar_dias_nao_conferido'
        )
