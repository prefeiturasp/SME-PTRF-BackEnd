from rest_framework import serializers
from django.db.models import Sum

from ...models import CategoriaPdde


class CategoriaPddeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoriaPdde
        fields = ('id', 'uuid', 'nome')


class CategoriaPddeComTotaisSerializer(serializers.ModelSerializer):
    total_valor_custeio = serializers.SerializerMethodField()
    total_valor_capital = serializers.SerializerMethodField()
    total_valor_livre_aplicacao = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = CategoriaPdde
        fields = ['nome', 'total_valor_custeio', 'total_valor_capital', 'total_valor_livre_aplicacao', 'total']

    def get_total_valor_custeio(self, obj):
        return obj.acaopdde_set.aggregate(
            total=Sum('saldo_valor_custeio') + Sum('previsao_valor_custeio')
        )['total'] or 0

    def get_total_valor_capital(self, obj):
        return obj.acaopdde_set.aggregate(
            total=Sum('saldo_valor_capital') + Sum('previsao_valor_capital')
        )['total'] or 0

    def get_total_valor_livre_aplicacao(self, obj):
        return obj.acaopdde_set.aggregate(
            total=Sum('saldo_valor_livre_aplicacao') + Sum('previsao_valor_livre_aplicacao')
        )['total'] or 0

    def get_total(self, obj):
        total_custeio = self.get_total_valor_custeio(obj)
        total_capital = self.get_total_valor_capital(obj)
        total_livre = self.get_total_valor_livre_aplicacao(obj)
        return total_custeio + total_capital + total_livre


class TotalGeralSerializer(serializers.Serializer):
    total_valor_custeio = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_valor_capital = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_valor_livre_aplicacao = serializers.DecimalField(max_digits=20, decimal_places=2)
    total = serializers.DecimalField(max_digits=20, decimal_places=2)


class CategoriasPddeSomatorioTotalSerializer(serializers.Serializer):
    categorias = CategoriaPddeComTotaisSerializer(many=True, read_only=True)
    total = TotalGeralSerializer(read_only=True)

    def to_representation(self, instance):
        categorias = CategoriaPdde.objects.prefetch_related('acaopdde_set').all()
        categorias_data = CategoriaPddeComTotaisSerializer(categorias, many=True).data

        total_custeio = sum(cat['total_valor_custeio'] for cat in categorias_data)
        total_capital = sum(cat['total_valor_capital'] for cat in categorias_data)
        total_livre_aplicacao = sum(cat['total_valor_livre_aplicacao'] for cat in categorias_data)
        total_geral = total_custeio + total_capital + total_livre_aplicacao

        return {
            "categorias": categorias_data,
            "total": {
                "total_valor_custeio": total_custeio,
                "total_valor_capital": total_capital,
                "total_valor_livre_aplicacao": total_livre_aplicacao,
                "total": total_geral
            }
        }