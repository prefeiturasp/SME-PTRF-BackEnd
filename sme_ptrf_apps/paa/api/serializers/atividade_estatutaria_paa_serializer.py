from rest_framework import serializers
from sme_ptrf_apps.paa.models import AtividadeEstatutaria, AtividadeEstatutariaPaa
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.api.serializers.atividade_estatutaria_serializer import AtividadeEstatutariaSerializer


class AtividadeEstatutariaPaaSerializer(serializers.ModelSerializer):
    atividade_estatutaria = AtividadeEstatutariaSerializer()

    class Meta:
        model = AtividadeEstatutariaPaa
        fields = ('uuid', 'paa', 'atividade_estatutaria', 'data')


class AtividadeEstaturariaPaaUpdateSerializer(serializers.Serializer):
    atividade_estatutaria = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AtividadeEstatutaria.objects.all()
    )
    nome = serializers.CharField(required=False)
    tipo = serializers.ChoiceField(
        choices=TipoAtividadeEstatutariaEnum.choices(),
        required=True
    )
    data = serializers.DateField(required=True)
    _destroy = serializers.BooleanField(required=False, default=False)
