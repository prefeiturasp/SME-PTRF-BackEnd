from rest_framework import serializers
from ...models import TipoCusteio


class TipoCusteioSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCusteio
        fields = ('uuid', 'nome')


class TipoCusteioSerializer(serializers.ModelSerializer):
    todas_unidades_selecionadas = serializers.SerializerMethodField()

    class Meta:
        model = TipoCusteio
        fields = ('nome', 'id', 'uuid', 'eh_tributos_e_tarifas', 'todas_unidades_selecionadas')

    def get_todas_unidades_selecionadas(self, obj):
        return obj.unidades.count() == 0


class TipoCusteioFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = TipoCusteio
        fields = "__all__"

    def update(self, instance, validated_data):
        selecionar_todas = self.context["request"].data.get("selecionar_todas")

        if selecionar_todas:
            instance.unidades.clear()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
