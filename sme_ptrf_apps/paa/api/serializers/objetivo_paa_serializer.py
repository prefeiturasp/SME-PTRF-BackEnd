from rest_framework import serializers
from sme_ptrf_apps.paa.models import Paa, ObjetivoPaa
from sme_ptrf_apps.paa.models.objetivo_paa import StatusChoices


class ObjetivoPaaUpdateSerializer(serializers.Serializer):
    objetivo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ObjetivoPaa.objects.all()
    )
    nome = serializers.CharField(required=False)
    _destroy = serializers.BooleanField(required=False, default=False)


class ObjetivoPaaSerializer(serializers.ModelSerializer):
    ERROR_MSG_NOME_JA_CADASTRADO = {"mensagem": "Já existe um objetivo cadastrado com este nome."}

    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Paa.objects.all())

    status = serializers.ChoiceField(
        choices=StatusChoices.choices,
        error_messages={
            'invalid_choice': 'Valor inválido para status de Objetivos do PAA.',
            'blank': 'Status não foi informado.',
            'null': 'Status não foi informado.',
        },
        required=False
    )

    nome = serializers.CharField(
        error_messages={
            'null': 'Nome do objetivo não foi informado.',
            'blank': 'Nome do objetivo não foi informado.',
            'required': 'Nome do objetivo é obrigatório.',
        },
        required=True
    )

    class Meta:
        model = ObjetivoPaa
        fields = ('uuid', 'id', 'nome', 'status', 'paa')
        read_only_fields = ('uuid', 'id')

    def create(self, validated_data):
        nome = validated_data['nome']
        nome_ja_cadastrado = ObjetivoPaa.objects.filter(nome__iexact=nome).all()

        if nome_ja_cadastrado:
            raise serializers.ValidationError(self.ERROR_MSG_NOME_JA_CADASTRADO)
        return ObjetivoPaa.objects.create(**validated_data)

    def update(self, instance, validated_data):
        nome = validated_data.get("nome", None)

        if nome and instance.nome != nome:
            nome_ja_cadastrado = ObjetivoPaa.objects.filter(nome__iexact=nome).exists()

            if nome_ja_cadastrado:
                raise serializers.ValidationError(self.ERROR_MSG_NOME_JA_CADASTRADO)
        return super().update(instance, validated_data)

    def get_status_objeto(self, obj):
        return list(filter(lambda x: x.get('key') == obj.status, StatusChoices.to_dict()))[0]
