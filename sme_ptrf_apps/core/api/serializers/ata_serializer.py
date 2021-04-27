from rest_framework import serializers

from ...api.serializers import AssociacaoInfoAtaSerializer
from ...api.serializers.periodo_serializer import PeriodoLookUpSerializer
from ...models import Ata, PrestacaoConta


class AtaLookUpSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_ata')
    alterado_em = serializers.SerializerMethodField('get_alterado_em')

    def get_nome_ata(self, obj):
        return obj.nome

    def get_alterado_em(self, obj):
        return obj.preenchida_em

    class Meta:
        model = Ata
        fields = ('uuid', 'nome', 'alterado_em')


class AtaSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_ata')
    associacao = AssociacaoInfoAtaSerializer(many=False)
    periodo = PeriodoLookUpSerializer(many=False)
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    def get_nome_ata(self, obj):
        return obj.nome

    class Meta:
        model = Ata
        fields = (
            'uuid',
            'arquivo_pdf',
            'status_geracao_pdf',
            'prestacao_conta',
            'nome',
            'periodo',
            'associacao',
            'tipo_ata',
            'tipo_reuniao',
            'convocacao',
            'data_reuniao',
            'local_reuniao',
            'presidente_reuniao',
            'cargo_presidente_reuniao',
            'secretario_reuniao',
            'cargo_secretaria_reuniao',
            'comentarios',
            'parecer_conselho',
            'retificacoes'
        )
