from rest_framework import serializers
from sme_ptrf_apps.core.api.serializers.recurso_serializer import RecursoSerializer
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict
from ...api.serializers.unidade_serializer import (UnidadeInfoAtaSerializer, UnidadeLookUpSerializer,
                                                   UnidadeListEmAssociacoesSerializer, UnidadeSerializer,
                                                   UnidadeCreateSerializer)
from ...api.serializers.periodo_serializer import PeriodoLookUpSerializer
from ...api.serializers.periodo_inicial_associacao_serializer import SimplePeriodoInicialAssociacaoSerializer
from ...models import Associacao, Unidade, Periodo, PeriodoInicialAssociacao


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
    data_de_encerramento = serializers.SerializerMethodField('get_data_de_encerramento')

    def get_data_de_encerramento(self, obj):
        response = {
            "data": obj.data_de_encerramento,
            "help_text": "A associação deixará de ser exibida nos períodos posteriores à data de encerramento informada.",
            "pode_editar_dados_associacao_encerrada": obj.pode_editar_dados_associacao_encerrada
        }
        return response

    class Meta:
        model = Associacao
        fields = ('id', 'nome', 'data_de_encerramento',)


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

    periodos_iniciais = serializers.ListField(
        child=SimplePeriodoInicialAssociacaoSerializer(), required=True, write_only=True
    )

    class Meta:
        model = Associacao
        fields = '__all__'

    def create(self, validated_data):
        unidade = validated_data.pop('unidade')
        periodos_iniciais = validated_data.pop('periodos_iniciais', [])
        observacao = ""

        if "unidade__observacao" in validated_data:
            observacao = validated_data.pop('unidade__observacao')

        if not unidade.get('nome_dre'):
            raise serializers.ValidationError({"nome_dre": ["EOL informado não possui DRE."]})

        associacao = Associacao.objects.create(**validated_data)
        unidade['observacao'] = observacao

        unidade_object = Unidade.objects.filter(codigo_eol=unidade.get('codigo_eol')).first()

        if not unidade_object:
            unidade_object = UnidadeCreateSerializer().create(unidade)

        associacao.unidade = unidade_object
        associacao.save()

        for periodo_inicial in periodos_iniciais:
            associacao.periodos_iniciais.create(**periodo_inicial)

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
    periodos_iniciais = serializers.ListField(
        child=SimplePeriodoInicialAssociacaoSerializer(), required=True, write_only=True
    )

    class Meta:
        model = Associacao
        fields = '__all__'

    def update(self, instance, validated_data):
        periodos_iniciais = validated_data.pop('periodos_iniciais', [])
        observacao = ""

        if validated_data.get("unidade__observacao"):
            observacao = validated_data.pop('unidade__observacao')

        instance.unidade.observacao = observacao
        instance.unidade.save()

        if instance.pode_editar_dados_associacao_encerrada:
            update_instance_from_dict(instance, validated_data)

        instance.save()

        if instance.pode_editar_dados_associacao_encerrada and \
                instance.pode_editar_periodo_inicial['pode_editar_periodo_inicial'] and \
                len(periodos_iniciais) > 0:
            periodos_iniciais_list = []

            for periodo_inicial in periodos_iniciais:
                uuid = periodo_inicial.pop('uuid', None)

                periodo_inicial_obj = None

                if uuid:
                    periodo_inicial_obj = instance.periodos_iniciais.filter(uuid=uuid).first()
                    if periodo_inicial_obj:
                        update_instance_from_dict(periodo_inicial_obj, periodo_inicial)
                        periodo_inicial_obj.save()
                else:
                    periodo_inicial_obj = instance.periodos_iniciais.create(**periodo_inicial)

                periodos_iniciais_list.append(periodo_inicial_obj)

            periodos_iniciais_a_remover = PeriodoInicialAssociacao.objects.exclude(
                id__in=[d.id for d in periodos_iniciais_list]
            ).filter(associacao=instance)

            periodos_iniciais_a_remover.delete()

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
    encerrada = serializers.SerializerMethodField('get_encerrada')
    status_valores_reprogramados = serializers.SerializerMethodField('get_status_valores_reprogramados')
    recursos = serializers.SerializerMethodField('get_recursos_da_associacao', required=False)

    informacoes = serializers.SerializerMethodField(method_name='get_informacoes', required=False)

    def get_encerrada(self, obj):
        return obj.encerrada

    def get_informacoes(self, obj):
        return obj.tags_de_informacao

    def get_status_valores_reprogramados(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        recurso = getattr(request, "recurso", None) if request else None
        return obj.get_status_valores_reprogramados(recurso=recurso)

    def get_recursos_da_associacao(self, obj):
        recursos = []

        for periodo_inicial in obj.periodos_iniciais.all():
            recursos.append(periodo_inicial.recurso.nome)

        return recursos

    class Meta:
        model = Associacao
        fields = [
            'uuid',
            'nome',
            'cnpj',
            'status_valores_reprogramados',
            'data_de_encerramento',
            'tooltip_data_encerramento',
            'tooltip_encerramento_conta',
            'unidade',
            'encerrada',
            'informacoes',
            'recursos'
        ]


class AssociacaoCompletoSerializer(serializers.ModelSerializer):
    unidade = UnidadeSerializer(many=False)
    periodo_inicial = PeriodoLookUpSerializer()
    periodos_iniciais = SimplePeriodoInicialAssociacaoSerializer(many=True, read_only=True)
    data_de_encerramento = serializers.SerializerMethodField('get_data_de_encerramento')
    recursos_da_associacao = serializers.SerializerMethodField('get_recursos_da_associacao')

    def get_data_de_encerramento(self, obj):
        response = {
            "data": obj.data_de_encerramento,
            "help_text": "A associação deixará de ser exibida nos períodos posteriores à data de encerramento informada.",
            "pode_editar_dados_associacao_encerrada": obj.pode_editar_dados_associacao_encerrada
        }
        return response

    def get_recursos_da_associacao(self, obj):
        recursos = set()
        for periodo_inicial in obj.periodos_iniciais.all():
            recursos.add(periodo_inicial.recurso)

        response = RecursoSerializer(recursos, many=True).data

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
            'pode_editar_periodo_inicial',
            'recursos_da_associacao',
            'periodos_iniciais'
        ]
