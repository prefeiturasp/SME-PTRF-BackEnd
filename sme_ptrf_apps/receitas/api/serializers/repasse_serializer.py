from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import AssociacaoSerializer
from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import ContaAssociacaoLookUpSerializer
from sme_ptrf_apps.core.models import Periodo, Associacao, ContaAssociacao, AcaoAssociacao

from ...models import Repasse


class PeriodoSerializer(serializers.ModelSerializer):
    serializers.DateField(format="")

    class Meta:
        model = Periodo
        fields = [
            'uuid',
            'data_inicio_realizacao_despesas',
            'data_fim_realizacao_despesas',
            'referencia'
        ]


class RepasseSerializer(serializers.ModelSerializer):
    valor_capital = serializers.SerializerMethodField('get_valor_capital')
    valor_custeio = serializers.SerializerMethodField('get_valor_custeio')
    valor_livre = serializers.SerializerMethodField('get_valor_livre')
    acao_associacao = AcaoAssociacaoLookUpSerializer()
    conta_associacao = ContaAssociacaoLookUpSerializer()
    periodo = PeriodoSerializer()
    associacao = AssociacaoSerializer()

    carga_origem = serializers.SerializerMethodField('get_carga_origem')
    campos_editaveis = serializers.SerializerMethodField('get_campos_editaveis')

    def get_carga_origem(self, obj):
        import os

        if obj.carga_origem:
            if obj.carga_origem.conteudo:
                nome_do_arquivo = os.path.basename(obj.carga_origem.conteudo.name)
                return nome_do_arquivo

        return ""

    def get_campos_editaveis(self, obj):
        return obj.get_campos_editaveis()

    def get_valor_capital(self, obj):
        """Quando o repasse tiver a receita do tipo capital realizado é retornado zero."""
        return '0.00' if obj.realizado_capital else str(obj.valor_capital)

    def get_valor_custeio(self, obj):
        """Quando o repasse tiver a receita do tipo custeio realizado é retornado zero."""
        return '0.00' if obj.realizado_custeio else str(obj.valor_custeio)

    def get_valor_livre(self, obj):
        """Quando o repasse tiver a receita do tipo livre realizado é retornado zero."""
        return '0.00' if obj.realizado_livre else str(obj.valor_livre)

    class Meta:
        model = Repasse
        fields = [
            'associacao',
            'uuid',
            'valor_capital',
            'valor_custeio',
            'valor_livre',
            'acao_associacao',
            'conta_associacao',
            'periodo',
            'status',
            'realizado_capital',
            'realizado_custeio',
            'realizado_livre',
            'carga_origem',
            'carga_origem_linha_id',
            'id',
            'campos_editaveis'
        ]


class RepasseListSerializer(serializers.ModelSerializer):
    acao_associacao = AcaoAssociacaoLookUpSerializer()
    conta_associacao = ContaAssociacaoLookUpSerializer()
    periodo = PeriodoSerializer()
    associacao = AssociacaoSerializer()

    carga_origem = serializers.SerializerMethodField('get_carga_origem')
    campos_editaveis = serializers.SerializerMethodField('get_campos_editaveis')

    def get_carga_origem(self, obj):
        import os

        if obj.carga_origem:
            if obj.carga_origem.conteudo:
                nome_do_arquivo = os.path.basename(obj.carga_origem.conteudo.name)
                return nome_do_arquivo

        return ""

    def get_campos_editaveis(self, obj):
        return obj.get_campos_editaveis()

    class Meta:
        model = Repasse
        fields = [
            'associacao',
            'uuid',
            'valor_capital',
            'valor_custeio',
            'valor_livre',
            'acao_associacao',
            'conta_associacao',
            'periodo',
            'status',
            'realizado_capital',
            'realizado_custeio',
            'realizado_livre',
            'carga_origem',
            'carga_origem_linha_id',
            'id',
            'campos_editaveis'
        ]


class RepasseCreateSerializer(serializers.ModelSerializer):
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

    periodo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all()
    )

    class Meta:
        model = Repasse
        fields = [
            'associacao',
            'uuid',
            'valor_capital',
            'valor_custeio',
            'valor_livre',
            'acao_associacao',
            'conta_associacao',
            'periodo',
            'status',
            'realizado_capital',
            'realizado_custeio',
            'realizado_livre',
        ]
