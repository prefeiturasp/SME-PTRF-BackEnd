from rest_framework import serializers

from ...models import TipoTransacao


class TipoTransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTransacao
        fields = ('id', 'nome', 'tem_documento')


class TipoTransacaoComUuidSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTransacao
        fields = ('id', 'uuid', 'nome', 'tem_documento')

    def create(self, validated_data):
        nome = validated_data.get('nome')

        if TipoTransacao.objects.filter(nome__iexact=nome).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este tipo de transação já existe.'
                })

        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        nome = validated_data.get('nome')

        if TipoTransacao.objects.filter(nome__iexact=nome).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este tipo de transação já existe.'
                })

        instance = super().update(instance, validated_data)
        return instance
