from rest_framework import serializers

from ...models import TipoAcertoLancamento
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict


class TipoAcertoLancamentoSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        nome = validated_data['nome']

        nome_ja_cadastrado = TipoAcertoLancamento.objects.filter(nome=nome).all()

        if nome_ja_cadastrado:
            raise serializers.ValidationError(
                {"detail": "Já existe um tipo de acerto de lançamento com esse nome."}
            )

        tipo_lancamento_criado = TipoAcertoLancamento.objects.create(**validated_data)

        return tipo_lancamento_criado

    def update(self, instance, validated_data):
        nome = validated_data.get("nome", None)

        if nome and instance.nome != nome:
            nome_ja_cadastrado = TipoAcertoLancamento.objects.filter(nome=nome).all()

            if nome_ja_cadastrado:
                raise serializers.ValidationError(
                    {"detail": "Já existe um tipo de acerto de lançamento com esse nome."}
                )

        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    class Meta:
        model = TipoAcertoLancamento
        fields = ('id', 'nome', 'categoria', 'ativo', 'uuid')
