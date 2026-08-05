from rest_framework import serializers

from sme_ptrf_apps.paa.models import ProgramaPdde


class ProgramaPddeSimplesSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por serializar o Programa PDDE Simples.
    """
    class Meta:
        model = ProgramaPdde
        fields = ('uuid', 'nome')


class ProgramaPddeSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por serializar o Programa PDDE.

    Além dos campos do modelo, expõe campos calculados para apresentação.
    """
    pode_ser_excluida = serializers.SerializerMethodField()

    class Meta:
        model = ProgramaPdde
        fields = ('id', 'uuid', 'nome', 'pode_ser_excluida')

    def get_pode_ser_excluida(self, obj):
        return obj.acaopdde_set.count() == 0


class ProgramaPddeComTotaisSerializer(serializers.Serializer):
    """
        Serializer referente ao dados de totais de um Programa
    """
    uuid = serializers.UUIDField(read_only=True)
    nome = serializers.CharField(max_length=255, read_only=True)
    total_valor_custeio = serializers.FloatField(read_only=True)
    total_valor_capital = serializers.FloatField(read_only=True)
    total_valor_livre_aplicacao = serializers.FloatField(read_only=True)
    total = serializers.FloatField(read_only=True)


class TotalGeralSerializer(serializers.Serializer):
    """
        Serializer referente ao dados de totais de todas as ações de um Programa
    """
    total_valor_custeio = serializers.FloatField(read_only=True)
    total_valor_capital = serializers.FloatField(read_only=True)
    total_valor_livre_aplicacao = serializers.FloatField(read_only=True)
    total = serializers.FloatField(read_only=True)


class ProgramasPddeSomatorioTotalSerializer(serializers.Serializer):
    """
    Serializer responsável por serializar o Programa PDDE Somatório Total.
    """
    programas = ProgramaPddeComTotaisSerializer(many=True, read_only=True)
    total = TotalGeralSerializer(read_only=True)
