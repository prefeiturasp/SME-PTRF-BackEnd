from rest_framework import serializers

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.dre.api.serializers.comissao_serializer import ComissaoSerializer
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict

from ...models import MembroComissao


class MembroComissaoListSerializer(serializers.ModelSerializer):
    dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.dres.all()
    )
    comissoes = ComissaoSerializer(many=True)

    class Meta:
        model = MembroComissao
        fields = ('uuid', 'rf', 'nome', 'email', 'qtd_comissoes', 'dre', 'comissoes')


class MembroComissaoCreateSerializer(serializers.ModelSerializer):
    dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.dres.all()
    )

    def create(self, validated_data):
        rf = validated_data['rf']
        dre = validated_data['dre']

        rf_ja_cadastrado = MembroComissao.objects.filter(rf=rf).filter(dre=dre).all()

        if rf_ja_cadastrado:
            raise serializers.ValidationError(
                {"detail": "Já existe um membro de comissão com esse Registro Funcional."}
            )

        try:
            comissoes = validated_data.pop("comissoes")
        except KeyError:
            comissoes = []

        membro_comissao_criado = MembroComissao.objects.create(**validated_data)

        if not comissoes:
            raise serializers.ValidationError({
                "detail": "Para salvar um membro de comissão, é necessário informar pelo menos uma comissão"
            })

        membro_comissao_criado.adiciona_comissoes(comissoes)

        return membro_comissao_criado

    def update(self, instance, validated_data):
        rf = validated_data.get("rf", None)
        dre = validated_data.get("dre", None)

        if rf and instance.rf != rf:
            if dre:
                rf_ja_cadastrado = MembroComissao.objects.filter(rf=rf).filter(dre=dre).all()

                if rf_ja_cadastrado:
                    raise serializers.ValidationError(
                        {"detail": "Já existe um membro de comissão com esse Registro Funcional."}
                    )

        possui_comissoes = validated_data.get("comissoes", None)
        if possui_comissoes:
            comissoes = validated_data.pop("comissoes")
            instance.adiciona_comissoes(comissoes)

        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    class Meta:
        model = MembroComissao
        fields = ('uuid', 'rf', 'nome', 'email', 'qtd_comissoes', 'dre', 'comissoes')


class MembroComissaoRetrieveSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.core.api.serializers.unidade_serializer import UnidadeLookUpSerializer
    dre = UnidadeLookUpSerializer()
    comissoes = ComissaoSerializer(many=True)

    class Meta:
        model = MembroComissao
        fields = ('uuid', 'rf', 'nome', 'email', 'qtd_comissoes', 'dre', 'comissoes')
