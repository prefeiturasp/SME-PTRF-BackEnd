from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ...models import FiqueDeOlho, Recurso, TipoTextoFiqueDeOlhoChoices
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict


class FiqueDeOlhoSerializer(serializers.ModelSerializer):
    short_texto = serializers.SerializerMethodField(read_only=True, source='get_short_texto')
    tipo_texto_display = serializers.SerializerMethodField(read_only=True, source='get_tipo_texto_display')

    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Recurso.objects.all()
    )

    tipo_texto = serializers.ChoiceField(
        choices=TipoTextoFiqueDeOlhoChoices.choices,
        required=True,
        error_messages={
            "invalid_choice": "O tipo de texto informado é inválido."
        }
    )

    def get_short_texto(self, obj):
        return obj.get_short_texto()

    def get_tipo_texto_display(self, obj):
        return obj.get_tipo_texto_display()

    def update(self, instance, validated_data):
        tipo_texto = validated_data.get('tipo_texto', instance.tipo_texto)
        recurso = validated_data.get('recurso', instance.recurso)

        if tipo_texto not in TipoTextoFiqueDeOlhoChoices.values:
            raise serializers.ValidationError(
                {"detail": "O campo tipo_texto deve ser um valor válidos."}
            )

        ja_cadastrado = FiqueDeOlho.get_first_with_recurso_and_tipo_texto(recurso, tipo_texto)

        if ja_cadastrado and ja_cadastrado.id != instance.id:
            raise serializers.ValidationError(
                {"detail": "Já existe um texto de fique de olho para o tipo de texto e recurso selecionado."}
            )

        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    class Meta:
        model = FiqueDeOlho
        fields = ('id', 'uuid', 'texto', 'tipo_texto', 'recurso', 'short_texto', 'tipo_texto_display')
        validators = [
            UniqueTogetherValidator(
                queryset=FiqueDeOlho.objects.all(),
                fields=["tipo_texto", "recurso"],
                message="Já existe um registro para este tipo de texto e recurso."
            )
        ]
