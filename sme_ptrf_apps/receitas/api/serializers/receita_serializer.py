import datetime
import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import ContaAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.periodo_serializer import PeriodoLookUpSerializer
from sme_ptrf_apps.core.models import AcaoAssociacao, Associacao, ContaAssociacao, Periodo

from sme_ptrf_apps.despesas.api.serializers.despesa_serializer import DespesaListSerializer
from sme_ptrf_apps.despesas.api.serializers.rateio_despesa_serializer import RateioDespesaEstornoLookupSerializer
from sme_ptrf_apps.despesas.models import RateioDespesa

from sme_ptrf_apps.receitas.models import Receita, Repasse

from ...services import atualiza_repasse_para_pendente, atualiza_repasse_para_realizado
from .detalhe_tipo_receita_serializer import DetalheTipoReceitaSerializer
from .tipo_receita_serializer import TipoReceitaSerializer, TipoReceitaLookUpSerializer
from .repasse_serializer import RepasseSerializer
from .motivo_estorno_serializer import MotivoEstornoSerializer

logger = logging.getLogger(__name__)


class ReceitaCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    repasse = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Repasse.objects.all()
    )

    conta_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ContaAssociacao.objects.all()
    )

    acao_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AcaoAssociacao.objects.all()
    )

    referencia_devolucao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all()
    )

    rateio_estornado = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        allow_empty=True,
        allow_null=True,
        queryset=RateioDespesa.objects.all()
    )

    def create(self, validated_data):

        # Validando data de encerramento
        data_da_receita = validated_data['data'] if validated_data['data'] else None

        data_de_encerramento = validated_data['associacao'].data_de_encerramento if validated_data['associacao'] and validated_data['associacao'].data_de_encerramento else None

        if data_da_receita and data_de_encerramento and data_da_receita > data_de_encerramento:
            data_de_encerramento = data_de_encerramento.strftime("%d/%m/%Y")
            erro = {
                "erro_data_de_encerramento":True,
                "data_de_encerramento": f"{data_de_encerramento}",
                "mensagem": f"A data do crédito não pode ser posterior à {data_de_encerramento}, data de encerramento da associação."
            }
            raise ValidationError(erro)

        if validated_data['conta_associacao'].tipo_conta.id not in [t.id for t in validated_data['tipo_receita'].tipos_conta.all()]:
            raise ValidationError(f"O tipo de receita {validated_data['tipo_receita'].nome} não permite salvar créditos com contas do tipo {validated_data['conta_associacao'].tipo_conta.nome}")

        if validated_data['tipo_receita'].e_repasse:
            atualiza_repasse_para_realizado(validated_data)

        # Retirando motivos estorno do validated_data
        try:
            motivos_estorno = validated_data.pop('motivos_estorno')
        except KeyError:
            motivos_estorno = []

        # Retirando outros motivos estorno do validated_data
        try:
            outros_motivos_estorno = validated_data.pop('outros_motivos_estorno')
        except KeyError:
            outros_motivos_estorno = ""

        # Cria receita
        receita = Receita.objects.create(**validated_data)

        # Caso seja estorno, será adicionado os motivos e outros motivos a receita
        if validated_data['tipo_receita'].e_estorno:
            if not motivos_estorno and not outros_motivos_estorno:
                raise ValidationError({
                    "detail": "Para salvar um crédito do tipo estorno, é necessário informar o campo 'motivos_estorno' ou 'outros_motivos_estorno'"
                })
            receita.adiciona_motivos_estorno(motivos_estorno, outros_motivos_estorno)

        return receita

    def update(self, instance, validated_data):

        # Validando data de encerramento
        if instance and instance.data and validated_data['associacao'] and validated_data['associacao'].data_de_encerramento and instance.data > validated_data['associacao'].data_de_encerramento:
            data_de_encerramento = validated_data['associacao'].data_de_encerramento.strftime("%d/%m/%Y")
            erro = {
                "erro_data_de_encerramento":True,
                "data_de_encerramento": f"{data_de_encerramento}",
                "mensagem": f"A data do crédito não pode ser posterior à {data_de_encerramento}, data de encerramento da associação."
            }
            raise ValidationError(erro)

        if validated_data['conta_associacao'].tipo_conta.id not in [t.id for t in validated_data['tipo_receita'].tipos_conta.all()]:
            raise ValidationError(f"O tipo de receita {validated_data['tipo_receita'].nome} não permite salvar créditos com contas do tipo {validated_data['conta_associacao'].tipo_conta.nome}")

        if instance.repasse:
            atualiza_repasse_para_pendente(instance)

        if validated_data['tipo_receita'].e_repasse:
            atualiza_repasse_para_realizado(validated_data)

        # Retirando motivos estorno do validated_data
        try:
            motivos_estorno = validated_data.pop('motivos_estorno')
        except KeyError:
            motivos_estorno = []

        # Retirando outros motivos estorno do validated_data
        try:
            outros_motivos_estorno = validated_data.pop('outros_motivos_estorno')
        except KeyError:
            outros_motivos_estorno = ""

        receita_atualizada = super().update(instance, validated_data)

        # Caso seja estorno, será adicionado os motivos e outros motivos a receita
        if validated_data['tipo_receita'].e_estorno:
            if not motivos_estorno and not outros_motivos_estorno:
                raise ValidationError({
                    "detail": "Para salvar um crédito do tipo estorno, é necessário informar o campo 'motivos_estorno' ou 'outros_motivos_estorno'"
                })

            receita_atualizada.adiciona_motivos_estorno(motivos_estorno, outros_motivos_estorno)

        return receita_atualizada

    class Meta:
        model = Receita
        exclude = ('id',)


class ReceitaListaSerializer(serializers.ModelSerializer):

    tipo_receita = TipoReceitaSerializer()
    acao_associacao = AcaoAssociacaoLookUpSerializer()
    conta_associacao = ContaAssociacaoLookUpSerializer()
    detalhe_tipo_receita = DetalheTipoReceitaSerializer()
    referencia_devolucao = PeriodoLookUpSerializer()
    repasse = RepasseSerializer()
    saida_do_recurso = DespesaListSerializer()
    rateio_estornado = RateioDespesaEstornoLookupSerializer()
    motivos_estorno = MotivoEstornoSerializer(many=True, required=False, allow_null=True)

    data_e_hora_de_inativacao = serializers.SerializerMethodField(
        method_name="get_data_e_hora_de_inativacao",
        required=False,
        allow_null=True
    )

    def get_data_e_hora_de_inativacao(self, receita):
        if receita.data_e_hora_de_inativacao:
            return f"Este crédito foi excluído em: " \
                   f"{receita.data_e_hora_de_inativacao.strftime('%d/%m/%Y %H:%M:%S')}"

    class Meta:
        model = Receita
        fields = (
            'uuid',
            'data',
            'valor',
            'tipo_receita',
            'acao_associacao',
            'conta_associacao',
            'conferido',
            'categoria_receita',
            'detalhe_tipo_receita',
            'detalhe_outros',
            'referencia_devolucao',
            'notificar_dias_nao_conferido',
            'repasse',
            'saida_do_recurso',
            'rateio_estornado',
            'motivos_estorno',
            'outros_motivos_estorno',
            'status',
            'data_e_hora_de_inativacao',
        )


class ReceitaConciliacaoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )
    tipo_receita = TipoReceitaLookUpSerializer()
    acao_associacao = AcaoAssociacaoLookUpSerializer()
    rateio_estornado = RateioDespesaEstornoLookupSerializer()
    mensagem_inativa = serializers.SerializerMethodField('get_mensagem_receita_inativa')

    def get_mensagem_receita_inativa(self, receita):
        return receita.mensagem_inativacao

    class Meta:
        model = Receita
        fields = (
            'associacao',
            'data',
            'valor',
            'tipo_receita',
            'acao_associacao',
            'categoria_receita',
            'detalhamento',
            'notificar_dias_nao_conferido',
            'conferido',
            'uuid',
            'rateio_estornado',
            'status',
            'data_e_hora_de_inativacao',
            'mensagem_inativa'
        )


class ReceitaLookUpSerializer(serializers.ModelSerializer):

    tipo_receita = TipoReceitaSerializer()

    class Meta:
        model = Receita
        fields = (
            'uuid',
            'data',
            'valor',
            'tipo_receita',
            'categoria_receita',
            'detalhe_tipo_receita',
            'detalhe_outros',
        )
