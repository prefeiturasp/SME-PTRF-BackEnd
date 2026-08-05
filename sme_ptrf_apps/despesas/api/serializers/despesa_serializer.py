import logging
from rest_framework import serializers
from waffle import get_waffle_flag_model

from .rateio_despesa_serializer import RateioDespesaSerializer, RateioDespesaTabelaGastosEscolaSerializer
from .tipo_documento_serializer import TipoDocumentoSerializer, TipoDocumentoListSerializer
from .tipo_transacao_serializer import TipoTransacaoSerializer
from .motivo_pagamento_antecipado_serializer import MotivoPagamentoAntecipadoSerializer
from ..serializers.rateio_despesa_serializer import RateioDespesaCreateSerializer
from ...models import Despesa, TipoDocumento, TipoTransacao
from ....core.api.serializers.associacao_serializer import AssociacaoSerializer
from ....core.models import Associacao
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
        exclude = ("recurso",)


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
        return despesa.checa_despesa_anterior_ao_uso_do_sistema_editavel()

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
    valor_total = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=True,
        allow_null=False
    )

    def validate_rateios(self, value):
        flags = get_waffle_flag_model()
        existe_flag_pipeline = flags.objects.filter(name='despesas-pipeline', everyone=True).exists()
        if existe_flag_pipeline:
            # bypass validate_rateios(R01, REG-003, REG-004, R05, REG-006), executa pela pipeline
            return value

        # [PIPELINE] As validações abaixo (R01, REG-003, REG-004, R05, REG-006) serão absorvidas
        # pela pipeline quando substituída. Validators correspondentes:
        #   RateiosObrigatoriosValidator  → REG-002
        #   SomaValorRateioValidator      → REG-003 (valor_rateio)
        #   SomaValorOriginalValidator     → REG-004 (valor_original)
        #   RateiosCapitalValidator       → REG-005, REG-006
        # Ponto de acionamento futuro: validate() — onde o contexto completo já está disponível.
        ValidacaoDespesaService.validar_rateios_serializer(
            raw_rateios=self.initial_data.get("rateios", []),
            valor_total=self.initial_data.get("valor_total"),
            valor_original=self.initial_data.get("valor_original"),
            retem_imposto=self.initial_data.get("retem_imposto", False),
            raw_despesas_impostos=self.initial_data.get("despesas_impostos", []),
            valor_recursos_proprios=self.initial_data.get(
                "valor_recursos_proprios", 0
            )
        )
        return value

    def executa_pipeline(self, data):
        # [PIPELINE] Execução paralela ao legado quando a flag 'despesas-pipeline' está ativa.
        # Validators ativos crescem à medida que cada regra é verificada quanto à paridade.
        # Quando todos os validators estiverem migrados, o legado acima será removido.
        from sme_ptrf_apps.despesas.validators import (
            DespesaContextBuilder,
            DespesaValidationError,
            CREATE_PIPELINE,
            UPDATE_PIPELINE,
            CREATE_ACERTO_PIPELINE,
            UPDATE_ACERTO_PIPELINE,
        )

        uuid_acerto = self.context.get("uuid_solicitacao_acerto")
        recurso = self.context.get("recurso")
        if self.instance is None:
            pipeline = CREATE_ACERTO_PIPELINE if uuid_acerto else CREATE_PIPELINE
        else:
            pipeline = UPDATE_ACERTO_PIPELINE if uuid_acerto else UPDATE_PIPELINE

        ctx = DespesaContextBuilder.build(
            validated_data=data,
            instance=self.instance,
            recurso=recurso,
            initial_data=self.initial_data,
            uuid_solicitacao_acerto=uuid_acerto,
        )

        try:
            ctx = pipeline.run(ctx)
        except DespesaValidationError as exc:
            raise serializers.ValidationError(exc.detail)

        # Sincroniza mutações do apply() de volta ao data.
        # ctx.rateios / ctx.despesas_impostos apontam para as listas do data —
        # mutações em dicts individuais propagam automaticamente.
        # Campos escalares do ctx precisam de sync explícito.
        data["motivos_pagamento_antecipado"] = ctx.motivos_pagamento_antecipado
        data["outros_motivos_pagamento_antecipado"] = ctx.outros_motivos or ""
        data["data_documento"] = ctx.data_documento
        data["numero_documento"] = ctx.numero_documento
        data["cpf_cnpj_fornecedor"] = ctx.cpf_cnpj_fornecedor

        return data

    def validate(self, data):
        recurso = self.context.get("recurso")

        flags = get_waffle_flag_model()
        existe_flag_pipeline = flags.objects.filter(name='despesas-pipeline', everyone=True).exists()
        if not existe_flag_pipeline:
            if not self.instance:

                if not recurso:
                    raise serializers.ValidationError(
                        "Recurso da despesa é obrigatório"
                    )

        # ainda não coberto
        ValidacaoDespesaService.validar_periodo_e_contas(
            instance=self.instance,
            data_transacao=data.get("data_transacao"),
            rateios=data.get("rateios", []),
            despesas_impostos=data.get("despesas_impostos", []),
            recurso=self.instance.recurso if self.instance else recurso
        )

        # Retorno de dados validados e mutados da pipeline
        if existe_flag_pipeline:
            data = self.executa_pipeline(data)

        return data

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
        from waffle import get_waffle_flag_model

        validated_data["recurso"] = self.context["recurso"]

        despesa = DespesaService.create(
            validated_data,
            limpar_prioridades_callback=self._limpar_prioridades_paa
        )

        # REG-029 — vincular gasto incluído (só pipeline + uuid de acerto no context)
        flags = get_waffle_flag_model()
        pipeline_ativa = flags.objects.filter(name='despesas-pipeline', everyone=True).exists()
        uuid_acerto = self.context.get("uuid_solicitacao_acerto")
        if pipeline_ativa and uuid_acerto:
            from sme_ptrf_apps.core.services.solicitacao_acerto_documento_service import (
                SolicitacaoAcertoDocumentoService,
            )
            SolicitacaoAcertoDocumentoService.marcar_como_gasto_incluido(
                uuid_solicitacao_acerto=uuid_acerto,
                uuid_gasto_incluido=str(despesa.uuid),
            )

        return despesa

    def update(self, instance, validated_data):
        from sme_ptrf_apps.despesas.services.despesa_service import DespesaService

        from django.db import DatabaseError
        from copy import deepcopy
        import time

        # [PIPELINE — Fluxo 4] REG-031: DespesaService.update já chama
        # _marcar_lancamento_como_atualizado (PC devolvida + solicitação pendente).
        # REG-033: herança de conciliação de impostos também fica no service.
        # REG-032: ConciliacaoAcertoValidator.apply nos rateios novos (pipeline acerto).

        max_retries = 3
        retry_count = 0

        payload_original = deepcopy(validated_data)

        while retry_count < max_retries:
            try:
                if retry_count > 0:
                    instance.refresh_from_db()

                return DespesaService.update(
                    instance,
                    deepcopy(payload_original),
                    limpar_prioridades_callback=self._limpar_prioridades_paa
                )
            except DatabaseError as e:
                if "timeout" in str(e).lower() or "closed" in str(e).lower():
                    retry_count += 1
                    if retry_count < max_retries:
                        log.warning(
                            f"Timeout detectado ao atualizar despesa #{instance.id},"
                            f" tentando novamente ({retry_count}/{max_retries})"
                        )
                        time.sleep(2 ** retry_count)
                        continue
                raise

    class Meta:
        model = Despesa
        exclude = ('id', 'recurso', )


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
        return despesa.periodo_da_despesa.referencia if despesa.periodo_da_despesa else None

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
