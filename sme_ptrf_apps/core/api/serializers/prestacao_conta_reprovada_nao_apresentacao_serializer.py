from rest_framework import serializers
from sme_ptrf_apps.core.models import PrestacaoContaReprovadaNaoApresentacao, Associacao, Periodo
from sme_ptrf_apps.core.api.serializers import PeriodoLookUpSerializer, AssociacaoCompletoSerializer


class PrestacaoContaReprovadaNaoApresentacaoSerializer(serializers.ModelSerializer):
    periodo = PeriodoLookUpSerializer(many=False)
    associacao = AssociacaoCompletoSerializer(many=False)
    unidade_eol = serializers.SerializerMethodField('get_unidade_eol')
    periodo_uuid = serializers.SerializerMethodField('get_periodo_uuid')
    status = serializers.SerializerMethodField('get_status')

    def get_unidade_eol(self, obj):
        return obj.associacao.unidade.codigo_eol if obj.associacao and obj.associacao.unidade else ''

    def get_periodo_uuid(self, obj):
        return obj.periodo.uuid if obj.periodo and obj.periodo.uuid else ''

    def get_status(self, obj):
        return "REPROVADA_NAO_APRESENTACAO"

    class Meta:
        model = PrestacaoContaReprovadaNaoApresentacao
        fields = ('id', 'uuid', 'periodo', 'associacao', 'data_de_reprovacao', 'unidade_eol', 'periodo_uuid', 'status')


class PrestacaoContaReprovadaNaoApresentacaoCreateSerializer(serializers.ModelSerializer):
    periodo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Periodo.objects.all()
    )

    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Associacao.objects.all()
    )

    class Meta:
        model = PrestacaoContaReprovadaNaoApresentacao
        fields = ('id', 'uuid', 'periodo', 'associacao', 'data_de_reprovacao')

