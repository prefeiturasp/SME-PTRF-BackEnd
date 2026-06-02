from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import TipoContaSerializer, UnidadeSerializer
from sme_ptrf_apps.core.api.serializers.recurso_serializer import RecursoSerializer
from .detalhe_tipo_receita_serializer import DetalheTipoReceitaSerializer
from sme_ptrf_apps.receitas.models import TipoReceita, DetalheTipoReceita
from sme_ptrf_apps.core.models import TipoConta, Recurso


class TipoReceitaSerializer(serializers.ModelSerializer):
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    class Meta:
        model = TipoReceita
        fields = (
            'id',
            'nome',
            'e_repasse',
            'aceita_capital',
            'aceita_custeio',
            'aceita_livre',
            'e_devolucao',
            'e_recursos_proprios',
            'recurso'
        )


class TipoReceitaEDetalhesSerializer(serializers.ModelSerializer):
    detalhes_tipo_receita = DetalheTipoReceitaSerializer(many=True)
    tipos_conta = TipoContaSerializer(many=True)

    class Meta:
        model = TipoReceita
        fields = (
            'id',
            'nome',
            'aceita_capital',
            'aceita_custeio',
            'aceita_livre',
            'detalhes_tipo_receita',
            'e_repasse',
            'e_devolucao',
            'e_recursos_proprios',
            'e_estorno',
            'e_rendimento',
            'mensagem_usuario',
            'possui_detalhamento',
            'tipos_conta',
        )


class TipoReceitaLookUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoReceita
        fields = ('id', 'nome')


class TipoReceitaListaSerializer(serializers.ModelSerializer):
    uso_associacao = serializers.CharField(read_only=True)
    detalhes_tipo_receita = DetalheTipoReceitaSerializer(many=True)
    tipos_conta = TipoContaSerializer(many=True)
    unidades = UnidadeSerializer(many=True)
    todas_unidades_selecionadas = serializers.SerializerMethodField()

    recurso = RecursoSerializer(
        read_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = TipoReceita
        fields = (
            'id',
            'uuid',
            'nome',
            'aceita_capital',
            'aceita_custeio',
            'aceita_livre',
            'e_rendimento',
            'e_repasse',
            'e_devolucao',
            'e_recursos_proprios',
            'e_estorno',
            'mensagem_usuario',
            'possui_detalhamento',
            'detalhes_tipo_receita',
            'tipos_conta',
            'unidades',
            'todas_unidades_selecionadas',
            'uso_associacao',
            'recurso'
        )

    def get_todas_unidades_selecionadas(self, obj):
        return obj.unidades.count() == 0


class TipoReceitaCreateSerializer(serializers.ModelSerializer):
    detalhes = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    tipos_conta = serializers.SlugRelatedField(many=True, queryset=TipoConta.objects.all(), slug_field='uuid')
    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all()
    )

    class Meta:
        model = TipoReceita
        fields = (
            'id',
            'uuid',
            'nome',
            'aceita_capital',
            'aceita_custeio',
            'aceita_livre',
            'e_repasse',
            'e_devolucao',
            'e_recursos_proprios',
            'e_estorno',
            'e_rendimento',
            'mensagem_usuario',
            'detalhes',
            'possui_detalhamento',
            'tipos_conta',
            'recurso'
        )

    def create(self, validated_data):
        nome = validated_data.get('nome')
        recurso = validated_data.get('recurso')
        detalhes_data = validated_data.pop("detalhes", [])

        # Normaliza o nome: remove espaços em branco extras
        if nome:
            nome = ' '.join(nome.split())
            validated_data['nome'] = nome

        if TipoReceita.objects.filter(nome__iexact=nome, recurso=recurso).exists():
            raise serializers.ValidationError({'non_field_errors': 'Este Tipo de Receita já existe para esse recurso.'})

        instance = super().create(validated_data)

        if self.context["request"].data.get("selecionar_todas"):
            instance.unidades.clear()

        detalhes_list = []

        for item in detalhes_data:
            try:
                detalhe = DetalheTipoReceita.objects.get(id=item)
            except Exception:
                detalhe = DetalheTipoReceita.objects.create(nome=item, tipo_receita=instance)

            detalhes_list.append(detalhe)

        instance.detalhes_tipo_receita.set(detalhes_list)

        return instance

    def update(self, instance, validated_data):
        nome = validated_data.get('nome')
        detalhes_data = validated_data.pop("detalhes", [])
        recurso = validated_data.get('recurso')

        # Normaliza o nome: remove espaços em branco extras
        if nome:
            nome = ' '.join(nome.split())
            validated_data['nome'] = nome

        if TipoReceita.objects.filter(nome__iexact=nome, recurso=recurso).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({'non_field_errors': 'Este Tipo de Receita já existe para esse recurso.'})

        instance = super().update(instance, validated_data)

        if self.context["request"].data.get("selecionar_todas"):
            instance.unidades.clear()

        detalhes_list = []

        for item in detalhes_data:
            try:
                detalhe = DetalheTipoReceita.objects.get(id=item)
            except Exception:
                detalhe = DetalheTipoReceita.objects.create(nome=item, tipo_receita=instance)

            detalhes_list.append(detalhe)

        detalhes_a_remover = DetalheTipoReceita.objects.exclude(
            id__in=[d.id for d in detalhes_list]
        ).filter(tipo_receita=instance)

        detalhes_em_uso = detalhes_a_remover.filter(
            receitas__isnull=False
        ).values_list('nome', flat=True).distinct()

        if detalhes_em_uso.exists():
            nomes = ', '.join(detalhes_em_uso)
            raise serializers.ValidationError({
                'non_field_errors': (
                    f'Não é possível remover os seguintes detalhamentos pois já foram utilizados em receitas: {nomes}.'
                )
            })

        detalhes_a_remover.delete()

        instance.detalhes_tipo_receita.set(detalhes_list)

        return instance
