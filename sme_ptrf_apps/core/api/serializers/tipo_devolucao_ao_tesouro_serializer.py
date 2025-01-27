from rest_framework import serializers
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict
from ...models import TipoDevolucaoAoTesouro


class TipoDevolucaoAoTesouroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDevolucaoAoTesouro
        fields = ('id', 'nome', 'uuid')

    def create(self, validated_data):
        nome = validated_data['nome']
        nome_ja_cadastrado = TipoDevolucaoAoTesouro.objects.filter(nome__iexact=nome).exists()
        if nome_ja_cadastrado:
            raise serializers.ValidationError(
                {'non_field_errors': 'Este motivo de devolução ao tesouro já existe.'})

        motivo_devolucao_criado = TipoDevolucaoAoTesouro.objects.create(**validated_data)
        return motivo_devolucao_criado

    def update(self, instance, validated_data):
        nome = validated_data.get('nome')
        if nome and instance.nome != nome:
            nome_ja_cadastrado = TipoDevolucaoAoTesouro.objects.filter(nome__iexact=nome).exists()

            if nome_ja_cadastrado:
                raise serializers.ValidationError(
                    {"non_field_errors": "Este motivo de devolução ao tesouro já existe."})
        update_instance_from_dict(instance, validated_data, save=True)
        return instance
