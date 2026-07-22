from rest_framework import serializers

from ...models import SolicitacaoAcertoLancamento, TipoAcertoLancamento, Recurso
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict


class TipoAcertoLancamentoSerializer(serializers.ModelSerializer):

    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Recurso.objects.all()
    )

    def create(self, validated_data):
        validated_data['nome'] = " ".join(validated_data['nome'].split())
        nome = validated_data['nome']
        categoria = validated_data.get('categoria', None)
        recurso = validated_data.get('recurso', None)

        nome_ja_cadastrado = TipoAcertoLancamento.objects.filter(
            nome__iexact=nome,
            categoria=categoria,
            recurso=recurso
        ).all()

        if nome_ja_cadastrado:
            raise serializers.ValidationError(
                {"detail": "Já existe um tipo de acerto de lançamento com esse nome e categoria para esse recurso."}
            )

        tipo_lancamento_criado = TipoAcertoLancamento.objects.create(**validated_data)

        return tipo_lancamento_criado

    def update(self, instance, validated_data):
        validated_data['nome'] = " ".join(validated_data.get("nome").split())
        nome = validated_data['nome']
        categoria = validated_data.get("categoria", instance.categoria)

        if nome and instance.nome != nome:
            recurso = validated_data.get("recurso", instance.recurso)
            nome_ja_cadastrado = TipoAcertoLancamento.objects.filter(nome=nome, categoria=categoria, recurso=recurso).all()

            if nome_ja_cadastrado:
                raise serializers.ValidationError(
                    {"detail": "Já existe um tipo de acerto de lançamento com esse nome e categoria para esse recurso."}
                )

        if categoria != instance.categoria and SolicitacaoAcertoLancamento.objects.filter(
            tipo_acerto=instance
        ).exists():
            raise serializers.ValidationError(
                {"non_field_errors": "Não é permitido alterar. Pois existem solicitações de acertos vinculadas."}
            )

        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    class Meta:
        model = TipoAcertoLancamento
        fields = ('id', 'nome', 'categoria', 'ativo', 'uuid', 'pode_alterar_saldo_conciliacao', 'recurso')
