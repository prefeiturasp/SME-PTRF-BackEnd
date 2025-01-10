from rest_framework import serializers
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict
from ...models import TipoDocumento


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = (
            'uuid',
            'id',
            'nome',
            'apenas_digitos',
            'numero_documento_digitado',
            'pode_reter_imposto',
            'eh_documento_de_retencao_de_imposto',
            'documento_comprobatorio_de_despesa')

    def create(self, validated_data):
        nome = validated_data['nome']
        nome_ja_cadastrado = TipoDocumento.objects.filter(nome__iexact=nome).exists()
        if nome_ja_cadastrado:
            raise serializers.ValidationError({
                'non_field_errors': 'Este tipo de documento já existe.'
                })

        tipo_documento_criado = TipoDocumento.objects.create(**validated_data)
        return tipo_documento_criado

    def update(self, instance, validated_data):
        nome = validated_data.get("nome", None)

        if nome and instance.nome != nome:
            nome_ja_cadastrado = TipoDocumento.objects.filter(nome__iexact=nome).exists()

            if nome_ja_cadastrado:
                raise serializers.ValidationError(
                    {"non_field_errors": "Este tipo de documento já existe."}
                )

        update_instance_from_dict(instance, validated_data, save=True)

        return instance


class TipoDocumentoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ('id', 'nome')
