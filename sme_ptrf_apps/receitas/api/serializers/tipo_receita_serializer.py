from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import TipoContaSerializer, UnidadeSerializer
from .detalhe_tipo_receita_serializer import DetalheTipoReceitaSerializer
from sme_ptrf_apps.receitas.models import TipoReceita, DetalheTipoReceita
from sme_ptrf_apps.core.models import TipoConta, Unidade


class TipoReceitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoReceita
        fields = ('id', 'nome', 'e_repasse', 'aceita_capital', 'aceita_custeio', 'aceita_livre', 'e_devolucao', 'e_recursos_proprios')


class TipoReceitaEDetalhesSerializer(serializers.ModelSerializer):
    detalhes_tipo_receita = DetalheTipoReceitaSerializer(many=True)
    tipos_conta = TipoContaSerializer(many=True)

    class Meta:
        model = TipoReceita
        fields = ('id',
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
    detalhes = DetalheTipoReceitaSerializer(many=True)
    tipos_conta = TipoContaSerializer(many=True)
    unidades = UnidadeSerializer(many=True)
    todas_unidades_selecionadas = serializers.SerializerMethodField()

    class Meta:
        model = TipoReceita
        fields = ('id',
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
                  'detalhes',
                  'tipos_conta',
                  'unidades',
                  'todas_unidades_selecionadas'
                )

    def get_todas_unidades_selecionadas(self, obj):
        return obj.unidades.count() == 0

class TipoReceitaCreateSerializer(serializers.ModelSerializer):
    detalhes = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    tipos_conta = serializers.SlugRelatedField(many=True, queryset=TipoConta.objects.all(), slug_field='uuid')

    class Meta:
        model = TipoReceita
        fields = ('id',
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
                )

    def create(self, validated_data):
        nome = validated_data.get('nome')
        detalhes_data = validated_data.pop("detalhes", [])

        if TipoReceita.objects.filter(nome=nome).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este Tipo de Receita já existe.'
                })

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

        instance.detalhes.set(detalhes_list)

        return instance

    def update(self, instance, validated_data):
        nome = validated_data.get('nome')
        detalhes_data = validated_data.pop("detalhes", [])

        if TipoReceita.objects.filter(nome=nome).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este Tipo de Receita já existe.'
                })

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

        instance.detalhes.set(detalhes_list)

        return instance