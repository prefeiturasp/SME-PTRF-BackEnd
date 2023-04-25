from rest_framework import serializers
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict
from ...api.serializers.unidade_serializer import (UnidadeInfoAtaSerializer, UnidadeLookUpSerializer,
                                                   UnidadeListEmAssociacoesSerializer, UnidadeSerializer, UnidadeCreateSerializer)
from ...api.serializers.periodo_serializer import PeriodoLookUpSerializer
from ...models import Associacao, Unidade, Periodo


class AssociacaoSerializer(serializers.ModelSerializer):
    unidade = UnidadeLookUpSerializer(many=False)

    class Meta:
        model = Associacao
        fields = (
            'uuid',
            'ccm',
            'cnpj',
            'email',
            'nome',
            'unidade',
            'id',
            'processo_regularidade',
        )


class AssociacaoLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Associacao
        fields = ('id', 'nome')


class AssociacaoCreateSerializer(serializers.ModelSerializer):
    observacao = serializers.CharField(source="unidade__observacao", required=False, allow_blank=True, allow_null=True)

    unidade = UnidadeCreateSerializer(many=False)
    periodo_inicial = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all(),
        allow_null=True,
        allow_empty=True,
    )

    class Meta:
        model = Associacao
        fields = '__all__'

    def create(self, validated_data):
        unidade = validated_data.pop('unidade')
        observacao = ""

        if validated_data.get("unidade__observacao"):
            observacao = validated_data.pop('unidade__observacao')

        associacao = Associacao.objects.create(**validated_data)
        unidade['observacao'] = observacao
        unidade_object = UnidadeCreateSerializer().create(unidade)
        associacao.unidade = unidade_object
        associacao.save()

        return associacao


class AssociacaoUpdateSerializer(serializers.ModelSerializer):
    observacao = serializers.CharField(source="unidade__observacao", required=False, allow_blank=True, allow_null=True)

    unidade = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.objects.all()
    )
    periodo_inicial = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all(),
        allow_null=True,
        allow_empty=True,
    )

    class Meta:
        model = Associacao
        fields = '__all__'

    def update(self, instance, validated_data):
        observacao = ""

        if validated_data.get("unidade__observacao"):
            observacao = validated_data.pop('unidade__observacao')

        instance.unidade.observacao = observacao
        instance.unidade.save()

        update_instance_from_dict(instance, validated_data)
        instance.save()

        return instance

class AssociacaoInfoAtaSerializer(serializers.ModelSerializer):
    unidade = UnidadeInfoAtaSerializer(many=False)

    class Meta:
        model = Associacao
        fields = [
            'uuid',
            'nome',
            'cnpj',
            'unidade',
        ]


class AssociacaoListSerializer(serializers.ModelSerializer):
    unidade = UnidadeListEmAssociacoesSerializer(many=False)

    class Meta:
        model = Associacao
        fields = [
            'uuid',
            'nome',
            'cnpj',
            'status_valores_reprogramados',
            'data_de_encerramento',
            'unidade'
        ]


class AssociacaoCompletoSerializer(serializers.ModelSerializer):
    unidade = UnidadeSerializer(many=False)
    periodo_inicial = PeriodoLookUpSerializer()

    data_de_encerramento = serializers.SerializerMethodField('get_data_de_encerramento')

    def get_data_de_encerramento(self, obj):
        response = {
            "data": obj.data_de_encerramento,
            "help_text": "A associação deixará de ser exibida nos períodos posteriores à data de encerramento informada."
        }
        return response

    class Meta:
        model = Associacao
        fields = [
            'uuid',
            'nome',
            'unidade',
            'cnpj',
            'ccm',
            'email',
            'presidente_associacao',
            'presidente_conselho_fiscal',
            'processo_regularidade',
            'periodo_inicial',
            'data_de_encerramento',
            'id',
            'retorna_se_pode_editar_periodo_inicial',
        ]
