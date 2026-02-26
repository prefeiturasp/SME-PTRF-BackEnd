import logging
from rest_framework import serializers

from .rateio_despesa_serializer import RateioDespesaSerializer, RateioDespesaTabelaGastosEscolaSerializer
from .tipo_documento_serializer import TipoDocumentoSerializer, TipoDocumentoListSerializer
from .tipo_transacao_serializer import TipoTransacaoSerializer
from .motivo_pagamento_antecipado_serializer import MotivoPagamentoAntecipadoSerializer
from ..serializers.rateio_despesa_serializer import RateioDespesaCreateSerializer
from ...models import Despesa, TipoDocumento, TipoTransacao
from ....core.api.serializers.associacao_serializer import AssociacaoSerializer
from ....core.models import Associacao, Periodo
from sme_ptrf_apps.despesas.services.validacao_despesa_service import ValidacaoDespesaService


log = logging.getLogger(__name__)


class DespesaImpostoSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)

    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = serializers.SlugRelatedField(
        slug_field='id',
        required=False,
        queryset=TipoDocumento.objects.all(),
        allow_null=True
    )

    tipo_transacao = serializers.SlugRelatedField(
        slug_field='id',
        required=False,
        queryset=TipoTransacao.objects.all(),
        allow_null=True
    )

    rateios = RateioDespesaCreateSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Despesa
        fields = '__all__'


class DespesaSerializer(serializers.ModelSerializer):
    associacao = AssociacaoSerializer()
    tipo_documento = TipoDocumentoSerializer()
    tipo_transacao = TipoTransacaoSerializer()
    rateios = RateioDespesaSerializer(many=True)
    despesas_impostos = DespesaImpostoSerializer(many=True, required=False, allow_null=True)
    despesa_geradora_do_imposto = serializers.SerializerMethodField(
        method_name="get_despesa_de_imposto", required=False, allow_null=True)
    motivos_pagamento_antecipado = MotivoPagamentoAntecipadoSerializer(many=True)
    despesa_anterior_ao_uso_do_sistema_editavel = serializers.SerializerMethodField(
        method_name="get_despesa_anterior_ao_uso_do_sistema_editavel", required=False, allow_null=True)

    def get_despesa_anterior_ao_uso_do_sistema_editavel(self, despesa):
        associacao = despesa.associacao
        pcs_da_associacao = associacao.prestacoes_de_conta_da_associacao.all().exists()
        editavel = True

        if not pcs_da_associacao:
            editavel = True
        elif (despesa.despesa_anterior_ao_uso_do_sistema and
              despesa.despesa_anterior_ao_uso_do_sistema_pc_concluida and
              pcs_da_associacao):
            editavel = False

        return editavel

    def get_despesa_de_imposto(self, despesa):
        despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
        return DespesaImpostoSerializer(
            despesa_geradora_do_imposto, many=False).data if despesa_geradora_do_imposto else None

    class Meta:
        model = Despesa
        fields = '__all__'


class DespesaCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        allow_null=False,
        queryset=Associacao.objects.all()
    )
    rateios = RateioDespesaCreateSerializer(many=True, required=True, allow_null=False)
    despesas_impostos = DespesaImpostoSerializer(many=True, required=False, allow_null=True)
    confirmar_limpeza_prioridades_paa = serializers.BooleanField(
        required=False,
        default=False,
        write_only=True,
        help_text='Se True, confirma a limpeza do valor das prioridades do PAA impactadas.'
    )

    valor_total = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=True,
        allow_null=False
    )

    def validate_rateios(self, value):
        ValidacaoDespesaService.validar_rateios_serializer(
            raw_rateios=self.initial_data.get("rateios", []),
            valor_total=self.initial_data.get("valor_total"),
            retem_imposto=self.initial_data.get("retem_imposto", False),
            raw_despesas_impostos=self.initial_data.get("despesas_impostos", []),
            valor_recursos_proprios=self.initial_data.get(
                "valor_recursos_proprios", 0
            )
        )
        return value

    def validate(self, data):

        ValidacaoDespesaService.validar_periodo_e_contas(
            instance=self.instance,
            data_transacao=data.get("data_transacao"),
            rateios=data.get("rateios", []),
            despesas_impostos=data.get("despesas_impostos", [])
        )

        recurso = self.context.get("recurso")

        if not recurso:
            raise serializers.ValidationError(
                "Recurso da despesa é obrigatório"
            )

        # Verifica prioridades do PAA impactadas
        # self._verificar_prioridades_paa_impactadas(data, self.instance)

        return data

    def _verificar_prioridades_paa_impactadas(self, data, instance_despesa) -> list:
        """
        Verifica se há prioridades do PAA que serão impactadas pelos
        rateios da despesa.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasDespesaRateioService

        confirmar_limpeza = data.get('confirmar_limpeza_prioridades_paa', False)

        rateios = data.get('rateios', [])
        prioridades_impactadas = []

        for rateio in rateios:
            service = PrioridadesPaaImpactadasDespesaRateioService(rateio, instance_despesa)
            prioridades = service.verificar_prioridades_impactadas()
            prioridades_impactadas.extend(prioridades)

        if prioridades_impactadas and not confirmar_limpeza:
            raise serializers.ValidationError({
                "confirmar": (
                    "Existem prioridades cadastradas que utilizam o valor da receita prevista. "
                    "Será necessário revisar as prioridades para atualizar o valor total.")
            })

    def _limpar_prioridades_paa(self, rateios, instance_despesa):
        """
        Limpa o valor_total das prioridades do PAA impactadas pelos rateios da despesa.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasDespesaRateioService

        for rateio in rateios:
            service = PrioridadesPaaImpactadasDespesaRateioService(rateio, instance_despesa)
            service.limpar_valor_prioridades_impactadas()

    def create(self, validated_data):
        from sme_ptrf_apps.despesas.services.despesa_service import DespesaService

        validated_data["recurso"] = self.context["recurso"]

        return DespesaService.create(
            validated_data,
            limpar_prioridades_callback=self._limpar_prioridades_paa
        )

    def update(self, instance, validated_data):
        from sme_ptrf_apps.despesas.services.despesa_service import DespesaService

        return DespesaService.update(
            instance,
            validated_data,
            limpar_prioridades_callback=self._limpar_prioridades_paa
        )

    class Meta:
        model = Despesa
        exclude = ('id',)


class DespesaListSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = TipoDocumentoListSerializer()
    tipo_transacao = TipoTransacaoSerializer()

    class Meta:
        model = Despesa
        fields = ('uuid', 'associacao', 'numero_documento', 'tipo_documento', 'data_documento', 'cpf_cnpj_fornecedor',
                  'nome_fornecedor', 'valor_total', 'valor_ptrf', 'data_transacao', 'tipo_transacao',
                  'documento_transacao')


class DespesaListComRateiosSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = TipoDocumentoListSerializer()
    tipo_transacao = TipoTransacaoSerializer()
    rateios = RateioDespesaTabelaGastosEscolaSerializer(many=True)

    receitas_saida_do_recurso = serializers.SerializerMethodField('get_recurso_externo')
    despesas_impostos = DespesaImpostoSerializer(many=True, required=False)
    despesa_geradora_do_imposto = serializers.SerializerMethodField(method_name="get_despesa_de_imposto",
                                                                    required=False)

    informacoes = serializers.SerializerMethodField(method_name='get_informacoes', required=False)

    periodo_referencia = serializers.SerializerMethodField(
        method_name="get_periodo_referencia", required=False, allow_null=True)

    def get_despesa_de_imposto(self, despesa):
        despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
        return DespesaImpostoSerializer(
            despesa_geradora_do_imposto, many=False).data if despesa_geradora_do_imposto else None

    def get_recurso_externo(self, despesa):
        return despesa.receitas_saida_do_recurso.first().uuid if despesa.receitas_saida_do_recurso.exists() else None

    def get_informacoes(self, despesa):
        return despesa.tags_de_informacao

    def get_periodo_referencia(self, despesa):
        if not despesa.data_documento:
            return None

        periodo = Periodo.da_data(despesa.data_documento)
        return periodo.referencia if periodo else None

    class Meta:
        model = Despesa
        fields = (
            'uuid', 'associacao', 'numero_documento', 'status', 'tipo_documento', 'data_documento',
            'cpf_cnpj_fornecedor', 'nome_fornecedor', 'valor_total', 'valor_ptrf', 'data_transacao', 'tipo_transacao',
            'documento_transacao', 'rateios', 'receitas_saida_do_recurso', 'despesa_geradora_do_imposto',
            'despesas_impostos', 'informacoes', 'periodo_referencia')


class DespesaConciliacaoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = TipoDocumentoListSerializer()
    tipo_transacao = TipoTransacaoSerializer()

    class Meta:
        model = Despesa
        fields = (
            'associacao',
            'numero_documento',
            'tipo_documento',
            'tipo_transacao',
            'documento_transacao',
            'data_documento',
            'data_transacao',
            'cpf_cnpj_fornecedor',
            'nome_fornecedor',
            'valor_ptrf',
            'valor_total',
            'status',
            'conferido',
            'uuid',
        )


class DespesaDocumentoMestreSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    tipo_documento = TipoDocumentoListSerializer()
    tipo_transacao = TipoTransacaoSerializer()

    receitas_saida_do_recurso = serializers.SerializerMethodField('get_recurso_externo')
    mensagem_inativa = serializers.SerializerMethodField('get_mensagem_despesa_inativa')

    def get_recurso_externo(self, despesa):
        return despesa.receitas_saida_do_recurso.first().uuid if despesa.receitas_saida_do_recurso.exists() else None

    def get_mensagem_despesa_inativa(self, despesa):
        return despesa.mensagem_inativacao

    class Meta:
        model = Despesa
        fields = (
            'associacao',
            'numero_documento',
            'tipo_documento',
            'tipo_transacao',
            'documento_transacao',
            'data_documento',
            'data_transacao',
            'cpf_cnpj_fornecedor',
            'nome_fornecedor',
            'valor_ptrf',
            'valor_total',
            'status',
            'conferido',
            'uuid',
            'receitas_saida_do_recurso',
            'data_e_hora_de_inativacao',
            'mensagem_inativa',
        )
