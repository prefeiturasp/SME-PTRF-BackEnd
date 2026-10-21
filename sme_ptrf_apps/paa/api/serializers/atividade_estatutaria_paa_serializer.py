from rest_framework import serializers
from sme_ptrf_apps.paa.models import AtividadeEstatutaria, AtividadeEstatutariaPaa
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.api.serializers.atividade_estatutaria_serializer import AtividadeEstatutariaSerializer


class AtividadeEstatutariaPaaSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por serializar os dados da atividade estatutaria do PAA.
    """
    atividade_estatutaria = AtividadeEstatutariaSerializer()

    class Meta:
        model = AtividadeEstatutariaPaa
        fields = ('uuid', 'paa', 'atividade_estatutaria', 'data')


class AtividadeEstatutariaPaaDocumentoPaaSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por serializar os dados da atividade estatutaria do PAA
    para o Documento PAA.
    """
    tipo_atividade = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()
    atividades_previstas = serializers.SerializerMethodField()
    mes_ano = serializers.SerializerMethodField()

    class Meta:
        model = AtividadeEstatutariaPaa
        fields = ('tipo_atividade', 'data', 'atividades_previstas', 'mes_ano')

    def get_tipo_atividade(self, obj: AtividadeEstatutariaPaa) -> str:
        """
        Retorna a descrição do tipo da atividade estatutária.

        Args:
            obj: Instância que contém a atividade estatutária PAA.

        Returns:
            str: Descrição legível do tipo da atividade estatutária.
        """
        return obj.atividade_estatutaria.get_tipo_display()

    def get_data(self, obj: AtividadeEstatutariaPaa) -> str:
        """
        Retorna a data da atividade estatutária PAA formatada.

        Args:
            obj: Instância da atividade estatutária do PAA.

        Returns:
            str: Data da atividade no formato ``DD/MM/AAAA``.
        """
        return obj.data.strftime("%d/%m/%Y")

    def get_atividades_previstas(self, obj) -> str:
        """
        Retorna o nome da atividade estatutária prevista.

        Args:
            obj: Instância que contém a atividade estatutária.

        Returns:
            str: Nome da atividade estatutária.
        """
        return obj.atividade_estatutaria.nome

    def get_mes_ano(self, obj: AtividadeEstatutariaPaa) -> str:
        """
        Retorna o mês e o ano da atividade formatados em português.

        O mês é obtido utilizando a localidade ``pt_BR.UTF-8`` e retornado
        em letras maiúsculas no formato ``MÊS/AAAA``.

        Args:
            obj: Instância da atividade estatutária do PAA.

        Returns:
            str: Mês e ano da atividade no formato ``MÊS/AAAA``.
        """
        import locale
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
        return obj.data.strftime("%B/%Y").upper()


class AtividadeEstaturariaPaaUpdateSerializer(serializers.Serializer):
    """
    Serializer responsável por serializar os dados da atividade estatutaria do PAA
    na operação de atualização.
    """
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
