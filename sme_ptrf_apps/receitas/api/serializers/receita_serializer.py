import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import ContaAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.periodo_serializer import PeriodoLookUpSerializer
from sme_ptrf_apps.core.models import AcaoAssociacao, Associacao, ContaAssociacao, Periodo
from sme_ptrf_apps.receitas.models import Receita, Repasse

from ...services import atualiza_repasse_para_pendente, atualiza_repasse_para_realizado
from .detalhe_tipo_receita_serializer import DetalheTipoReceitaSerializer
from .tipo_receita_serializer import TipoReceitaSerializer
from .repasse_serializer import RepasseSerializer

logger = logging.getLogger(__name__)


class ReceitaCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    repasse = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Repasse.objects.all()
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
        if validated_data['conta_associacao'].tipo_conta.id not in [t.id for t in validated_data['tipo_receita'].tipos_conta.all()]:
            raise ValidationError(f"O tipo de receita {validated_data['tipo_receita'].nome} não permite salvar créditos com contas do tipo {validated_data['conta_associacao'].tipo_conta.nome}")
        
        if validated_data['tipo_receita'].e_repasse:
            atualiza_repasse_para_realizado(validated_data)

        receita = Receita.objects.create(**validated_data)

        return receita

    def update(self, instance, validated_data):
        if validated_data['conta_associacao'].tipo_conta.id not in [t.id for t in validated_data['tipo_receita'].tipos_conta.all()]:
            raise ValidationError(f"O tipo de receita {validated_data['tipo_receita'].nome} não permite salvar créditos com contas do tipo {validated_data['conta_associacao'].tipo_conta.nome}")

        if instance.repasse:
            atualiza_repasse_para_pendente(instance)

        if validated_data['tipo_receita'].e_repasse:
            atualiza_repasse_para_realizado(validated_data)

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
    repasse = RepasseSerializer()

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
            'notificar_dias_nao_conferido',
            'repasse'
        )
