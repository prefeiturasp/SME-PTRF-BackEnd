from django.db import transaction
from rest_framework import serializers
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.models import FonteRecursoPaa, RecursoProprioPaa, Paa
from sme_ptrf_apps.paa.api.serializers.fonte_recurso_paa_serializer import FonteRecursoPaaSerializer


class RecursoProprioPaaCreateSerializer(serializers.ModelSerializer):

    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Paa.objects.all()
    )

    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Associacao.objects.all()
    )

    fonte_recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=FonteRecursoPaa.objects.all()
    )
    confirmar_limpeza_prioridades_paa = serializers.BooleanField(
        required=False,
        default=False,
        write_only=True,
        help_text='Se True, confirma a limpeza do valor das prioridades do PAA impactadas.'
    )

    class Meta:
        model = RecursoProprioPaa
        fields = ('id', 'paa', 'uuid', 'associacao', 'fonte_recurso', 'data_prevista', 'descricao', 'valor',
                  'confirmar_limpeza_prioridades_paa')

    def validate(self, attrs):
        # Verifica prioridades do PAA impactadas
        self._verificar_prioridades_paa_impactadas(attrs, self.instance)
        return super().validate(attrs)

    def _verificar_prioridades_paa_impactadas(self, attrs, instance) -> list:
        """
        Verifica se há prioridades do PAA que serão impactadas.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService

        confirmar_limpeza = attrs.get('confirmar_limpeza_prioridades_paa', False)

        prioridades_impactadas = []
        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(attrs, instance)
        prioridades = service.verificar_prioridades_impactadas()
        prioridades_impactadas.extend(prioridades)

        if prioridades_impactadas and not confirmar_limpeza:
            raise serializers.ValidationError({
                "confirmar": (
                    "Existem prioridades cadastradas que utilizam o valor da receita prevista. "
                    "O valor total será removido das prioridades cadastradas e é necessário revisá-las para "
                    "alterar o valor total.")
            })

    def _limpar_prioridades_paa(self, recurso_attrs, instance_despesa):
        """
        Limpa o valor_total das prioridades do PAA impactadas.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService

        service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(
            recurso_attrs, instance_despesa)
        service.limpar_valor_prioridades_impactadas()

    @transaction.atomic
    def update(self, instance, validated_data):
        # Remove flag de confirmação do validated_data (não é campo do model)
        confirmar_limpeza_prioridades = validated_data.pop('confirmar_limpeza_prioridades_paa', False)

        # Limpa prioridades do PAA se confirmado, com dados e instance antes de salvar
        if confirmar_limpeza_prioridades:
            self._limpar_prioridades_paa(validated_data, instance)

        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data.pop('confirmar_limpeza_prioridades_paa', False)
        return super().create(validated_data)


class RecursoProprioPaaListSerializer(serializers.ModelSerializer):
    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Paa.objects.all()
    )
    fonte_recurso = FonteRecursoPaaSerializer()
    valor = serializers.FloatField()
    associacao = serializers.SerializerMethodField('get_associacao_uuid')

    def get_associacao_uuid(self, obj):
        return obj.associacao.uuid

    class Meta:
        model = RecursoProprioPaa
        fields = ('id', 'paa', 'uuid', 'associacao', 'fonte_recurso', 'data_prevista', 'descricao', 'valor')


class RecursoProprioPaaListDocumentoPaaSerializer(serializers.ModelSerializer):
    data_prevista = serializers.SerializerMethodField()
    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Paa.objects.all()
    )
    fonte_recurso = FonteRecursoPaaSerializer()
    valor = serializers.FloatField()
    associacao = serializers.SerializerMethodField('get_associacao_uuid')

    def get_data_prevista(self, obj):
        return obj.data_prevista.strftime("%d/%m/%Y")

    def get_associacao_uuid(self, obj):
        return obj.associacao.uuid

    class Meta:
        model = RecursoProprioPaa
        fields = ('id', 'paa', 'uuid', 'associacao', 'fonte_recurso', 'data_prevista', 'descricao', 'valor')
