from rest_framework import serializers

from sme_ptrf_apps.receitas.models import DetalheTipoReceita, TipoReceita


class DetalheTipoReceitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalheTipoReceita
        fields = ('id', 'nome')


class DetalheTipoReceitaParametrizacaoSerializer(serializers.ModelSerializer):
    tipo_receita_nome = serializers.SerializerMethodField(read_only=True)

    tipo_receita = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=TipoReceita.objects.all()
    )

    can_edit_tipo_receita = serializers.SerializerMethodField()

    def get_can_edit_tipo_receita(self, obj):
        if obj and obj.pk and obj.receitas.exists():
            return False
        return True

    def get_tipo_receita_nome(self, obj):
        return obj.tipo_receita.nome if obj.tipo_receita else None

    class Meta:
        model = DetalheTipoReceita
        fields = ('id', 'uuid', 'nome', 'tipo_receita', 'tipo_receita_nome', 'can_edit_tipo_receita')

    def create(self, validated_data):
        nome = validated_data.get('nome')
        tipo_receita = validated_data.get('tipo_receita')

        # Normaliza o nome: remove espaços em branco extras
        if nome:
            nome = ' '.join(nome.split())
            validated_data['nome'] = nome

        if not tipo_receita:
            raise serializers.ValidationError({'non_field_errors': 'O campo tipo de crédito é obrigatório.'})

        if DetalheTipoReceita.objects.filter(nome__iexact=nome, tipo_receita=tipo_receita).exists():
            raise serializers.ValidationError({'non_field_errors': 'Este detalhe já existe para esse tipo de crédito.'})

        if not tipo_receita.possui_detalhamento:
            raise serializers.ValidationError({'non_field_errors': 'Não é possível associar um detalhe a um tipo de crédito que não permite detalhamento.'})

        instance = super().create(validated_data)
        return instance


    def update(self, instance, validated_data):
        nome = validated_data.get('nome')
        tipo_receita = validated_data.get('tipo_receita')

        # Normaliza o nome: remove espaços em branco extras
        if nome:
            nome = ' '.join(nome.split())
            validated_data['nome'] = nome

        if DetalheTipoReceita.objects.filter(nome__iexact=nome, tipo_receita=tipo_receita).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este detalhe já existe para esse tipo de crédito.'
            })

        if tipo_receita and instance.tipo_receita and tipo_receita != instance.tipo_receita:
            if instance.receitas.exists():
                raise serializers.ValidationError({
                    'non_field_errors': 'Não é possível alterar o tipo de crédito, pois existem receitas associadas a este detalhe.'
                })

        if not tipo_receita.possui_detalhamento:
            raise serializers.ValidationError({'non_field_errors': 'Não é possível associar um detalhe a um tipo de crédito que não permite detalhamento.'})

        instance = super().update(instance, validated_data)
        return instance

