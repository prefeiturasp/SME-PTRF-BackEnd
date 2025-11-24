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

    class Meta:
        model = RecursoProprioPaa
        fields = ('id', 'paa', 'uuid', 'associacao', 'fonte_recurso', 'data_prevista', 'descricao', 'valor')


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
