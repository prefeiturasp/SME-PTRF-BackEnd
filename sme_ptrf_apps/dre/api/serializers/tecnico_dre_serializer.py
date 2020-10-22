from rest_framework import serializers

from ...models import TecnicoDre
from ....core.api.serializers.unidade_serializer import DreSerializer
from ....core.models import Unidade


class TecnicoDreSerializer(serializers.ModelSerializer):
    dre = DreSerializer()

    class Meta:
        model = TecnicoDre
        fields = ('uuid', 'rf', 'nome', 'dre', 'email')


class TecnicoDreLookUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = TecnicoDre
        fields = ('uuid', 'rf', 'nome', 'email')



class TecnicoDreCreateSerializer(serializers.ModelSerializer):
    dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.objects.all()
    )
    class Meta:
        model = TecnicoDre
        exclude = ('id',)
