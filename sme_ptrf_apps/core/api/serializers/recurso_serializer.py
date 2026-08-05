from rest_framework import serializers
from sme_ptrf_apps.core.models import Recurso


class TextosAtaSerializer(serializers.Serializer):
    introducao = serializers.SerializerMethodField('get_introducao')
    letra_a = serializers.SerializerMethodField('get_letra_a')
    letra_b = serializers.SerializerMethodField('get_letra_b')
    letra_c = serializers.SerializerMethodField('get_letra_c')
    letra_d = serializers.SerializerMethodField('get_letra_d')

    def get_introducao(self, obj):
        return obj.texto_ata_introducao

    def get_letra_a(self, obj):
        return obj.get_fixed_text_texto_letra("A")

    def get_letra_b(self, obj):
        return obj.get_fixed_text_texto_letra("B")

    def get_letra_c(self, obj):
        return obj.get_fixed_text_texto_letra("C")

    def get_letra_d(self, obj):
        return obj.get_fixed_text_texto_letra("D")


class RecursoSerializer(serializers.ModelSerializer):
    textos_ata = serializers.SerializerMethodField('get_textos_ata')

    class Meta:
        model = Recurso
        fields = (
            'id',
            'uuid',
            'nome',
            'nome_exibicao',
            'criado_em',
            'alterado_em',
            'cor',
            'icone',
            'ativo',
            'legado',
            'exibe_valores_reprogramados',
            'habilita_aprovacao_com_ressalvas',
            'habilita_exibicao_de_lauda',
            'textos_ata',
        )
        read_only_fields = (
            'id',
            'uuid',
            'nome',
            'nome_exibicao',
            'criado_em',
            'alterado_em',
            'cor',
            'icone',
            'ativo',
            'legado',
            'exibe_valores_reprogramados',
            'habilita_aprovacao_com_ressalvas',
            'habilita_exibicao_de_lauda',
            'textos_ata',
        )

    def get_textos_ata(self, obj):
        serializer = TextosAtaSerializer(obj)
        return serializer.data
