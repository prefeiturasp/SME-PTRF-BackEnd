from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers.periodo_serializer import PeriodoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.unidade_serializer import UnidadeLookUpSerializer
from sme_ptrf_apps.dre.api.serializers.tecnico_dre_serializer import TecnicoDreLookUpSerializer
from sme_ptrf_apps.dre.models import Atribuicao, TecnicoDre
from sme_ptrf_apps.core.models import Periodo, Unidade


class AtribuicaoSerializer(serializers.ModelSerializer):
    periodo = PeriodoLookUpSerializer()
    tecnico = TecnicoDreLookUpSerializer()
    unidade = UnidadeLookUpSerializer()

    class Meta:
        model = Atribuicao
        fields = ('periodo', 'tecnico', 'unidade')


class AtribuicaoCreateSerializer(serializers.ModelSerializer):
    unidade = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.objects.all()
    )

    periodo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all()
    )

    tecnico = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=TecnicoDre.objects.all()
    )

    class Meta:
        model = Atribuicao
        exclude = ('id',)
