from rest_framework import serializers

from sme_ptrf_apps.core.models import Associacao, FonteRecursoPaa, RecursoProprioPaa
from sme_ptrf_apps.core.api.serializers import FonteRecursoPaaSerializer


class RecursoProprioPaaCreateSerializer(serializers.ModelSerializer):

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
        fields = ('id', 'uuid', 'associacao', 'fonte_recurso', 'data_prevista', 'descricao', 'valor')


class RecursoProprioPaaListSerializer(serializers.ModelSerializer):

    fonte_recurso = FonteRecursoPaaSerializer()
    valor = serializers.FloatField()
    associacao = serializers.SerializerMethodField('get_associacao_uuid')

    def get_associacao_uuid(self, obj):
        return obj.associacao.uuid

    class Meta:
        model = RecursoProprioPaa
        fields = ('id', 'uuid', 'associacao', 'fonte_recurso', 'data_prevista', 'descricao', 'valor')
