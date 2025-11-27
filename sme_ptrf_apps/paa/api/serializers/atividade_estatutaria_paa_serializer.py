from rest_framework import serializers
from sme_ptrf_apps.paa.models import AtividadeEstatutaria, AtividadeEstatutariaPaa
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.api.serializers.atividade_estatutaria_serializer import AtividadeEstatutariaSerializer


class AtividadeEstatutariaPaaSerializer(serializers.ModelSerializer):
    atividade_estatutaria = AtividadeEstatutariaSerializer()

    class Meta:
        model = AtividadeEstatutariaPaa
        fields = ('uuid', 'paa', 'atividade_estatutaria', 'data')


class AtividadeEstatutariaPaaDocumentoPaaSerializer(serializers.ModelSerializer):
    tipo_atividade = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()
    atividades_previstas = serializers.SerializerMethodField()
    mes_ano = serializers.SerializerMethodField()

    class Meta:
        model = AtividadeEstatutariaPaa
        fields = ('tipo_atividade', 'data', 'atividades_previstas', 'mes_ano')

    def get_tipo_atividade(self, obj):
        return obj.atividade_estatutaria.get_tipo_display()

    def get_data(self, obj):
        return obj.data.strftime("%d/%m/%Y")

    def get_atividades_previstas(self, obj):
        return obj.atividade_estatutaria.nome

    def get_mes_ano(self, obj):
        import locale
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
        return obj.data.strftime("%B/%Y").upper()


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
