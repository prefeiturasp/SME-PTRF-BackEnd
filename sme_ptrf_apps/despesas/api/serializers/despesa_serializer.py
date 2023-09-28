import logging

from rest_framework import serializers

from .rateio_despesa_serializer import RateioDespesaSerializer, RateioDespesaTabelaGastosEscolaSerializer
from .tipo_documento_serializer import TipoDocumentoSerializer, TipoDocumentoListSerializer
from .tipo_transacao_serializer import TipoTransacaoSerializer
from .motivo_pagamento_antecipado_serializer import MotivoPagamentoAntecipadoSerializer
from ..serializers.rateio_despesa_serializer import RateioDespesaCreateSerializer
from ...models import Despesa, RateioDespesa, TipoDocumento, TipoTransacao
from ....core.api.serializers.associacao_serializer import AssociacaoSerializer
from ....core.models import Associacao
from django.core.exceptions import ValidationError

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
    despesa_geradora_do_imposto = serializers.SerializerMethodField(method_name="get_despesa_de_imposto", required=False, allow_null=True)
    motivos_pagamento_antecipado = MotivoPagamentoAntecipadoSerializer(many=True)

    def get_despesa_de_imposto(self, despesa):
        despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
        return DespesaImpostoSerializer(despesa_geradora_do_imposto, many=False).data if despesa_geradora_do_imposto else None

    class Meta:
        model = Despesa
        fields = '__all__'


class DespesaCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )
    rateios = RateioDespesaCreateSerializer(many=True, required=False)
    despesas_impostos = DespesaImpostoSerializer(many=True, required=False, allow_null=True)

    def validate(self, data):
        rateios = data['rateios'] if 'rateios' in data else []
        despesas_impostos = data['despesas_impostos'] if 'despesas_impostos' in data else []

        for rateio in rateios:
            data_transacao = data['data_transacao']
            conta_associacao = rateio['conta_associacao']
            if conta_associacao and (conta_associacao.data_inicio > data_transacao):
                raise serializers.ValidationError({"mensagem": "Um ou mais rateios possuem conta com data de início posterior a data de transação."})

        for imposto in despesas_impostos:
            data_transacao = imposto['data_transacao']

            if data_transacao:
                for rateio in imposto['rateios']:
                    conta_associacao = rateio['conta_associacao']
                    if conta_associacao and (conta_associacao.data_inicio > data_transacao):
                        raise serializers.ValidationError({"mensagem": "Um ou mais rateios de imposto possuem conta com data de início posterior a data de transação."})

        return data

    def create(self, validated_data):

        data_de_encerramento = validated_data['associacao'].data_de_encerramento \
            if validated_data['associacao'] and validated_data['associacao'].data_de_encerramento else None

        # Validando data de encerramento data_documento
        data_documento = validated_data['data_documento'] if validated_data['data_documento'] else None

        if data_documento and data_de_encerramento and data_documento > data_de_encerramento:
            data_de_encerramento = data_de_encerramento.strftime("%d/%m/%Y")
            erro = {
                "erro_data_de_encerramento": True,
                "data_de_encerramento": f"{data_de_encerramento}",
                "mensagem": f"A data de documento e/ou data do pagamento não pode ser posterior à "
                            f"{data_de_encerramento}, data de encerramento da associação."
            }
            raise ValidationError(erro)

        # Validando data de encerramento data_pagamento
        data_transacao = validated_data['data_transacao'] if validated_data['data_transacao'] else None

        if data_transacao and data_de_encerramento and data_transacao > data_de_encerramento:
            data_de_encerramento = data_de_encerramento.strftime("%d/%m/%Y")
            erro = {
                "erro_data_de_encerramento": True,
                "data_de_encerramento": f"{data_de_encerramento}",
                "mensagem": f"A data de documento e/ou data do pagamento não pode ser posterior à "
                            f"{data_de_encerramento}, data de encerramento da associação."
            }
            raise ValidationError(erro)

        rateios = validated_data.pop('rateios')

        despesas_impostos = validated_data.pop('despesas_impostos') if validated_data.get('despesas_impostos') else None

        motivos_pagamento_antecipado = validated_data.pop('motivos_pagamento_antecipado')
        outros_motivos_pagamento_antecipado = validated_data['outros_motivos_pagamento_antecipado']

        data_transacao = validated_data['data_transacao']
        data_documento = validated_data['data_documento']

        if data_transacao and data_documento:
            if data_transacao < data_documento and not motivos_pagamento_antecipado and not outros_motivos_pagamento_antecipado:
                raise serializers.ValidationError({
                                                      "detail": "Quando a Data da transação for menor que a Data do Documento é necessário enviar os motivos do pagamento antecipado"})
            elif data_transacao >= data_documento:
                motivos_pagamento_antecipado = []
                outros_motivos_pagamento_antecipado = ""

        despesa = Despesa.objects.create(**validated_data)
        despesa.verifica_data_documento_vazio()
        log.info("Criando despesa com uuid: {}".format(despesa.uuid))

        rateios_lista = []
        for rateio in rateios:
            rateio["eh_despesa_sem_comprovacao_fiscal"] = despesa.eh_despesa_sem_comprovacao_fiscal
            rateio_object = RateioDespesaCreateSerializer().create(rateio)
            rateios_lista.append(rateio_object)

        motivos_list = []
        for motivo in motivos_pagamento_antecipado:
            motivos_list.append(motivo.id)

        despesa.rateios.set(rateios_lista)
        despesa.motivos_pagamento_antecipado.set(motivos_list)
        despesa.outros_motivos_pagamento_antecipado = outros_motivos_pagamento_antecipado
        despesa.atualiza_status()
        log.info("Despesa {}, Rateios: {}".format(despesa.uuid, rateios_lista))

        log.info("Criação de despesa finalizada!")

        # Despesa de Impostos
        if despesa.retem_imposto and despesas_impostos:
            log.info("Criando despesas de impostos gerados pela despesa")
            despesas_impostos_lista = []
            for despesa_imposto in despesas_impostos:
                rateios_imposto = despesa_imposto.pop('rateios') if despesa_imposto else None
                # Remove despesas imposto e motivos pagamento antecipado não utilizados no caso de despesas do imposto
                if "despesas_impostos" in despesa_imposto.keys():
                    despesa_imposto.pop('despesas_impostos') if despesa_imposto else None

                if "motivos_pagamento_antecipado" in despesa_imposto.keys():
                    despesa_imposto.pop('motivos_pagamento_antecipado') if despesa_imposto else None

                despesa_do_imposto = Despesa.objects.create(**despesa_imposto)
                log.info(f"Criando despesa de imposto com uuid: {despesa_do_imposto.uuid}")

                rateios_do_imposto_lista = []
                for rateio in rateios_imposto:
                    rateio["eh_despesa_sem_comprovacao_fiscal"] = despesa_do_imposto.eh_despesa_sem_comprovacao_fiscal
                    rateio_object = RateioDespesaCreateSerializer().create(rateio)
                    rateios_do_imposto_lista.append(rateio_object)

                despesa_do_imposto.rateios.set(rateios_do_imposto_lista)

                despesa_do_imposto.verifica_data_documento_vazio()
                despesa_do_imposto.atualiza_status()

                despesas_impostos_lista.append(despesa_do_imposto)

                log.info(
                    f"Despesa do imposto {despesa_do_imposto.uuid}, Rateios do imposto: {rateios_do_imposto_lista}"
                )

            despesa.despesas_impostos.set(despesas_impostos_lista)

            # necessário repassar pelas despesas impostos para atualizar o status
            # pois só a partir desse ponto existe o vinculo entre despesa geradora e despesa imposto
            for despesa_imposto in despesa.despesas_impostos.all():
                despesa_imposto.verifica_data_documento_vazio()
                despesa_imposto.atualiza_status()

            log.info("Criação de despesa de imposto finalizada!")

        return despesa

    def update(self, instance, validated_data):
        data_de_encerramento = validated_data['associacao'].data_de_encerramento \
            if validated_data['associacao'] and validated_data['associacao'].data_de_encerramento else None

        # Validando data de encerramento data_documento
        data_documento = instance.data_documento if instance and instance.data_documento else None

        if data_documento and data_de_encerramento and data_documento > data_de_encerramento:
            data_de_encerramento = validated_data['associacao'].data_de_encerramento.strftime("%d/%m/%Y")
            erro = {
                "erro_data_de_encerramento": True,
                "data_de_encerramento": f"{data_de_encerramento}",
                "mensagem": f"A data de documento e/ou data do pagamento não pode ser posterior à "
                            f"{data_de_encerramento}, data de encerramento da associação."
            }
            raise ValidationError(erro)

        # Validando data de encerramento data_pagamento
        data_transacao = instance.data_transacao if instance and instance.data_transacao else None

        if data_transacao and data_de_encerramento and data_transacao > data_de_encerramento:
            data_de_encerramento = validated_data['associacao'].data_de_encerramento.strftime("%d/%m/%Y")
            erro = {
                "erro_data_de_encerramento": True,
                "data_de_encerramento": f"{data_de_encerramento}",
                "mensagem": f"A data de documento e/ou data do pagamento não pode ser posterior à "
                            f"{data_de_encerramento}, data de encerramento da associação."
            }
            raise ValidationError(erro)

        rateios = validated_data.pop('rateios')

        despesas_impostos = validated_data.pop('despesas_impostos') if 'despesas_impostos' in validated_data else []

        motivos_pagamento_antecipado = validated_data.pop('motivos_pagamento_antecipado')
        outros_motivos_pagamento_antecipado = validated_data['outros_motivos_pagamento_antecipado']

        data_transacao = validated_data['data_transacao']
        data_documento = validated_data['data_documento']

        if data_transacao and data_documento:
            if data_transacao < data_documento and not motivos_pagamento_antecipado and not outros_motivos_pagamento_antecipado:
                raise serializers.ValidationError({"detail": "Quando a Data da transação for menor que a Data do Documento é necessário enviar os motivos do pagamento antecipado"})
            elif data_transacao >= data_documento:
                motivos_pagamento_antecipado = []
                outros_motivos_pagamento_antecipado = ""

        # Atualiza campos da despesa
        Despesa.objects.filter(uuid=instance.uuid).update(**validated_data)
        despesa_updated_somente_validade_data = Despesa.objects.get(uuid=instance.uuid)

        # Atualiza os rateios
        log.info(f"Atualizando rateios da despesa {instance.uuid}")
        keep_rateios = []  # rateios que serão mantidos. Qualquer um que não estiver na lista será apagado.
        for rateio in rateios:
            if "uuid" in rateio.keys():
                log.info(
                    f"Encontrada chave uuid no rateio {rateio['uuid']} R${rateio['valor_rateio']}. Será atualizado.")
                if RateioDespesa.objects.filter(uuid=rateio["uuid"]).exists():
                    log.info(f"Rateio encontrado {rateio['uuid']} R${rateio['valor_rateio']}")
                    rateio["eh_despesa_sem_comprovacao_fiscal"] = despesa_updated_somente_validade_data.eh_despesa_sem_comprovacao_fiscal
                    RateioDespesa.objects.filter(uuid=rateio["uuid"]).update(**rateio)
                    rateio_updated = RateioDespesa.objects.get(uuid=rateio["uuid"])

                    # Necessário para forçar a verificação se o rateio está completo
                    rateio_updated.save()

                    keep_rateios.append(rateio_updated.uuid)
                else:
                    log.info(f"Rateio NÃO encontrado {rateio['uuid']} R${rateio['valor_rateio']}")
                    continue
            else:
                log.info(f"Não encontrada chave uuid de rateio R${rateio['valor_rateio']}. Será criado.")
                rateio["eh_despesa_sem_comprovacao_fiscal"] = despesa_updated_somente_validade_data.eh_despesa_sem_comprovacao_fiscal
                rateio_updated = RateioDespesa.objects.create(**rateio, despesa=instance)
                keep_rateios.append(rateio_updated.uuid)

        # Apaga rateios da despesa que não estão na lista de rateios a serem mantidos
        for rateio in instance.rateios.all():
            if rateio.uuid not in keep_rateios:
                log.info(f"Rateio apagado {rateio.uuid} R${rateio.valor_rateio}")
                rateio.delete()

        motivos_list = []
        for motivo in motivos_pagamento_antecipado:
            motivos_list.append(motivo.id)

        # Atualiza as Despesas de Impostos
        if validated_data.get('retem_imposto') and despesas_impostos:
            # Atualiza despesas de impostos
            log.info(f"Atualizando despesas de impostos da despesa geradora {instance.uuid}")
            keep_impostos = []  # impostos que serão mantidos. Qualquer um que não estiver na lista será apagado.
            despesas_impostos_lista = []
            for despesa_imposto in despesas_impostos:
                rateios_imposto = despesa_imposto.pop('rateios') if despesa_imposto else None
                # Remove despesas imposto e motivos pagamento antecipado não utilizados no caso de despesas do imposto
                despesa_imposto.pop('despesas_impostos') if despesa_imposto else None
                despesa_imposto.pop('motivos_pagamento_antecipado') if despesa_imposto else None
                if "uuid" in despesa_imposto.keys():
                    log.info(
                        f"Encontrada chave uuid na despesa imposto {despesa_imposto['uuid']}. Será atualizada.")
                    if Despesa.objects.filter(uuid=despesa_imposto["uuid"]).exists():
                        log.info(f"Despesa Imposto encontrada {despesa_imposto['uuid']}")
                        Despesa.objects.filter(uuid=despesa_imposto["uuid"]).update(**despesa_imposto)
                        despesa_imposto_updated = Despesa.by_uuid(despesa_imposto["uuid"])
                        despesa_imposto_updated.verifica_data_documento_vazio()
                        keep_impostos.append(despesa_imposto["uuid"])
                        despesas_impostos_lista.append(despesa_imposto_updated)

                        # Atualiza os rateios da despesa imposto
                        rateios_do_imposto_lista = []
                        uuid_rateios_do_imposto_lista = []
                        for rateio in rateios_imposto:
                            if "uuid" in rateio.keys():
                                if RateioDespesa.objects.filter(uuid=rateio["uuid"]).exists():
                                    rateio[
                                        "eh_despesa_sem_comprovacao_fiscal"] = despesa_updated_somente_validade_data.eh_despesa_sem_comprovacao_fiscal
                                    RateioDespesa.objects.filter(uuid=rateio["uuid"]).update(**rateio)
                                    rateio_updated = RateioDespesa.objects.get(uuid=rateio["uuid"])
                                    rateio_updated.save()
                                    rateios_do_imposto_lista.append(rateio_updated)
                                    uuid_rateios_do_imposto_lista.append(rateio_updated.uuid)
                                else:
                                    log.info(f"Rateio NÃO encontrado {rateio['uuid']} R${rateio['valor_rateio']}")
                                    continue
                            else:
                                log.info(f"Não encontrada chave uuid de rateio R${rateio['valor_rateio']}. Será criado.")
                                rateio_object = RateioDespesaCreateSerializer().create(rateio)
                                rateios_do_imposto_lista.append(rateio_object)
                                uuid_rateios_do_imposto_lista.append(rateio_object.uuid)

                        # Apaga rateios da despesa de imposto que não estão na lista de rateios a serem mantidos
                        if despesa_imposto_updated and despesa_imposto_updated.rateios.exists():
                            for rateio in despesa_imposto_updated.rateios.all():
                                if rateio.uuid not in uuid_rateios_do_imposto_lista:
                                    log.info(f"Rateio de imposto será apagado {rateio.uuid}")
                                    rateio.delete()
                                    log.info(f"Apagado o rateio de imposto")
                    else:
                        log.info(f"Despesa Imposto NÃO encontrada {despesa_imposto['uuid']}")
                        continue
                else:
                    log.info(f"Não encontrada chave uuid de despesa imposto. Será criado.")
                    despesa_imposto_updated = Despesa.objects.create(**despesa_imposto)
                    despesa_imposto_updated.verifica_data_documento_vazio()
                    rateios_do_imposto_lista = []
                    for rateio in rateios_imposto:
                        rateio[
                            "eh_despesa_sem_comprovacao_fiscal"] = despesa_updated_somente_validade_data.eh_despesa_sem_comprovacao_fiscal
                        rateio_object = RateioDespesaCreateSerializer().create(rateio)
                        rateios_do_imposto_lista.append(rateio_object)

                    despesa_imposto_updated.rateios.set(rateios_do_imposto_lista)

                    keep_impostos.append(despesa_imposto_updated.uuid)
                    despesas_impostos_lista.append(despesa_imposto_updated)

            # Apaga os impostos da despesa que não estão na lista de impostos a manter
            for despesa_imposto in instance.despesas_impostos.all():
                if despesa_imposto.uuid not in keep_impostos:
                    log.info(f"Despesa imposto apagada {despesa_imposto.uuid}")
                    despesa_imposto.delete()

            instance.despesas_impostos.set(despesas_impostos_lista)

        elif not validated_data.get('retem_imposto'):
            if instance and instance.despesas_impostos.exists():
                for despesa_imposto in instance.despesas_impostos.all():
                    despesa_imposto.delete()

        # Retorna a despesa atualizada
        despesa_updated = Despesa.objects.get(uuid=instance.uuid)

        despesa_updated.motivos_pagamento_antecipado.set(motivos_list)
        despesa_updated.outros_motivos_pagamento_antecipado = outros_motivos_pagamento_antecipado
        despesa_updated.atualiza_status()
        despesa_updated.save()

        # necessário repassar pelas despesas impostos para atualizar o status
        # pois só a partir desse ponto existe o vinculo entre despesa geradora e despesa imposto
        for despesa_imposto in despesa_updated.despesas_impostos.all():
            despesa_imposto.verifica_data_documento_vazio()
            despesa_imposto.atualiza_status()

        return despesa_updated

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

    def get_despesa_de_imposto(self, despesa):
        despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
        return DespesaImpostoSerializer(despesa_geradora_do_imposto, many=False).data if despesa_geradora_do_imposto else None

    def get_recurso_externo(self, despesa):
        return despesa.receitas_saida_do_recurso.first().uuid if despesa.receitas_saida_do_recurso.exists() else None

    def get_informacoes(self, despesa):
        return despesa.tags_de_informacao
    class Meta:
        model = Despesa
        fields = (
        'uuid', 'associacao', 'numero_documento', 'status', 'tipo_documento', 'data_documento', 'cpf_cnpj_fornecedor',
        'nome_fornecedor', 'valor_total', 'valor_ptrf', 'data_transacao', 'tipo_transacao', 'documento_transacao',
        'rateios', 'receitas_saida_do_recurso', 'despesa_geradora_do_imposto', 'despesas_impostos', 'informacoes')


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
