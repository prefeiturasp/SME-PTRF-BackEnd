import logging
from django.db import transaction
from django.db.models import Count
from rest_framework import serializers
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO
from sme_ptrf_apps.despesas.models import Despesa, RateioDespesa
from sme_ptrf_apps.despesas.api.serializers.rateio_despesa_serializer import RateioDespesaCreateSerializer

logger = logging.getLogger(__name__)


def ordena_despesas_por_imposto(qs, lista_argumentos_ordenacao=None):

    if lista_argumentos_ordenacao is None:
        lista_argumentos_ordenacao = []

    qs = qs.annotate(c=Count('despesas_impostos'), c2=Count('despesa_geradora')).order_by('-c', '-c2', *lista_argumentos_ordenacao)
    despesas_ordenadas = []
    for despesa in qs:
        despesa_geradora_do_imposto = despesa.despesa_geradora_do_imposto.first()
        despesas_impostos = despesa.despesas_impostos.all()

        if not despesa_geradora_do_imposto:
            despesas_ordenadas.append(despesa)

        if despesas_impostos:
            for despesa_imposto in despesas_impostos:
                despesas_ordenadas.append(despesa_imposto)

    return despesas_ordenadas


def migra_despesas_periodos_anteriores():
    """
    Percorre todas as despesas com data de transação anterior ao período inicial de sua associação e atualiza os campos
    despesa_anterior_ao_uso_do_sistema e despesa_anterior_ao_uso_do_sistema_pc_concluida.

    O período inicial de uma associação é o período do seu saldo de implantação
    """
    logger.info('Obtendo lista de todas as associações ativas..')
    associacoes = Associacao.ativas.all()

    for associacao in associacoes:
        if associacao.periodo_inicial is None:
            logger.info(f'Associação {associacao} não possui período inicial.')
            continue

        logger.info(f'Migrando despesas anteriores a {associacao.periodo_inicial.referencia} da associação {associacao}..')

        despesas_anteriores = associacao.despesas.filter(data_transacao__lte=associacao.periodo_inicial.data_fim_realizacao_despesas)

        for despesa in despesas_anteriores:
            logger.info(f'Migrando despesa {despesa}..')
            despesa.despesa_anterior_ao_uso_do_sistema = True
            despesa.despesa_anterior_ao_uso_do_sistema_pc_concluida = associacao.prestacoes_de_conta_da_associacao.exists()
            despesa.save()


class DespesaService:

    # =====================================================
    # Criar Despesa
    # =====================================================

    @classmethod
    @transaction.atomic
    def create(cls, validated_data, limpar_prioridades_callback=None):
        logger.info("Iniciando criação de despesa")

        confirmar_limpeza = validated_data.pop("confirmar_limpeza_prioridades_paa", False)

        rateios = validated_data.pop("rateios")
        despesas_impostos = validated_data.pop("despesas_impostos", None)

        cls._validar_datas(validated_data)
        motivos, outros = cls._processar_pagamento_antecipado(validated_data)

        despesa = Despesa.objects.create(**validated_data)

        logger.info(f"Despesa criada com uuid={despesa.uuid}")

        despesa.verifica_data_documento_vazio()

        cls._criar_rateios(despesa, rateios)
        cls._aplicar_motivos(despesa, motivos, outros)

        cls._processar_impostos(despesa, despesas_impostos)

        cls._finalizar_despesa(despesa, rateios, confirmar_limpeza, limpar_prioridades_callback)

        logger.info(f"Criação da despesa {despesa.uuid} finalizada com sucesso")

        return despesa

    # =====================================================
    # Atualizar Despesa
    # =====================================================
    @classmethod
    @transaction.atomic
    def update(cls, instance: Despesa, validated_data, limpar_prioridades_callback=None):
        logger.info("Iniciando atualização de despesa")

        confirmar_limpeza = validated_data.pop("confirmar_limpeza_prioridades_paa", False)

        rateios = validated_data.pop("rateios")
        despesas_impostos = validated_data.pop("despesas_impostos", [])

        cls._validar_datas_update(instance, validated_data)
        motivos, outros = cls._processar_pagamento_antecipado(validated_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        cls._atualizar_rateios(instance, rateios)
        cls._aplicar_motivos(instance, motivos, outros)

        cls._processar_impostos_update(instance, despesas_impostos)

        cls._finalizar_despesa(instance, rateios, confirmar_limpeza, limpar_prioridades_callback)

        return instance

    # =====================================================
    # VALIDAÇÕES
    # =====================================================

    @staticmethod
    def _validar_datas(validated_data):
        associacao = validated_data.get("associacao")
        data_encerramento = associacao.data_de_encerramento if associacao else None

        for campo in ("data_documento", "data_transacao"):
            data = validated_data.get(campo)
            if data and data_encerramento and data > data_encerramento:
                dt_encerramento_formatada = data_encerramento.strftime("%d/%m/%Y")

                raise serializers.ValidationError({
                    "erro_data_de_encerramento": True,
                    "data_de_encerramento": dt_encerramento_formatada,
                    "mensagem": (
                        "A data de documento e/ou data do pagamento não pode ser posterior "
                        f"à {dt_encerramento_formatada}, data de encerramento da associação."
                    )
                })

    @classmethod
    def _validar_datas_update(cls, instance, validated_data):
        validated_data.setdefault("associacao", instance.associacao)
        validated_data.setdefault("data_documento", instance.data_documento)
        validated_data.setdefault("data_transacao", instance.data_transacao)
        cls._validar_datas(validated_data)

    # =====================================================
    # PAGAMENTO ANTECIPADO
    # =====================================================

    @staticmethod
    def _processar_pagamento_antecipado(validated_data):
        motivos = validated_data.pop("motivos_pagamento_antecipado", [])
        outros = validated_data.get("outros_motivos_pagamento_antecipado")

        dt = validated_data.get("data_transacao")
        dd = validated_data.get("data_documento")

        if dt and dd:
            if dt < dd and not motivos and not outros:
                raise serializers.ValidationError({
                    "detail": (
                        "Quando a Data da transação for menor que a Data do Documento "
                        "é necessário informar os motivos do pagamento antecipado."
                    )
                })
            elif dt >= dd:
                motivos = []
                outros = ""

        return motivos, outros

    # =====================================================
    # RATEIOS
    # =====================================================

    @staticmethod
    def _criar_rateios(despesa: Despesa, rateios):
        rateios_lista = []

        for rateio in rateios:
            rateio["eh_despesa_sem_comprovacao_fiscal"] = despesa.eh_despesa_sem_comprovacao_fiscal
            rateio["associacao"] = despesa.associacao
            rateio_obj = RateioDespesaCreateSerializer().create(rateio)
            rateios_lista.append(rateio_obj)

        despesa.rateios.set(rateios_lista)

    @staticmethod
    def _atualizar_rateios(despesa: Despesa, rateios):
        keep = []

        for rateio in rateios:

            rateio["eh_despesa_sem_comprovacao_fiscal"] = despesa.eh_despesa_sem_comprovacao_fiscal
            rateio["associacao"] = despesa.associacao

            if "uuid" in rateio:
                logger.info(
                    f"Encontrada chave uuid no rateio {rateio['uuid']} R${rateio['valor_rateio']}. Será atualizado."
                )

                rateio_para_atualizar = RateioDespesa.objects.filter(
                    uuid=rateio["uuid"]
                ).first()

                if rateio_para_atualizar:

                    aplicacao_anterior = rateio_para_atualizar.aplicacao_recurso
                    nova_aplicacao = rateio.get("aplicacao_recurso")

                    # CAPITAL -> CUSTEIO
                    if aplicacao_anterior == APLICACAO_CAPITAL and nova_aplicacao == APLICACAO_CUSTEIO:
                        logger.info(
                            f"Resetando campos de CAPITAL → CUSTEIO "
                            f"no rateio {rateio['uuid']}"
                        )
                        rateio.update({
                            "numero_processo_incorporacao_capital": "",
                            "especificacao_material_servico": None,
                            "quantidade_itens_capital": 0,
                            "nao_exibir_em_rel_bens": False,
                            "valor_item_capital": 0,
                        })

                    # CUSTEIO -> CAPITAL
                    if aplicacao_anterior == APLICACAO_CUSTEIO and nova_aplicacao == APLICACAO_CAPITAL:
                        logger.info(
                            f"Resetando campos de CUSTEIO → CAPITAL "
                            f"no rateio {rateio['uuid']}"
                        )
                        rateio.update({
                            "tipo_custeio": None,
                        })
                    
                    RateioDespesa.objects.filter(uuid=rateio["uuid"]).update(**rateio)
                    obj = RateioDespesa.objects.get(uuid=rateio["uuid"])
                    keep.append(obj.uuid)
                else:
                    logger.info(f"Rateio NÃO encontrado {rateio['uuid']} R${rateio['valor_rateio']}")
                    continue
           
            else:
                logger.info(f"Não encontrada chave uuid de rateio R${rateio['valor_rateio']}. Será criado.")
                obj = RateioDespesa.objects.create(**rateio, despesa=despesa)
                keep.append(obj.uuid)

            obj.save()

        RateioDespesa.objects.filter(despesa=despesa).exclude(uuid__in=keep).delete()

    # =====================================================
    # IMPOSTOS
    # =====================================================

    @classmethod
    def _processar_impostos(cls, despesa: Despesa, despesas_impostos):
        if not despesa.retem_imposto or not despesas_impostos:
            return

        lista = []

        for imposto in despesas_impostos:
            rateios = imposto.pop("rateios", [])

            if not rateios:
                raise serializers.ValidationError({
                    "mensagem": "A despesa de imposto precisa ter rateio associado"
                })

            imposto.pop("despesas_impostos", None)
            imposto.pop("motivos_pagamento_antecipado", None)
            imposto["recurso"] = despesa.recurso

            desp = Despesa.objects.create(**imposto)
            cls._criar_rateios(desp, rateios)
            desp.verifica_data_documento_vazio()
            desp.atualiza_status()
            lista.append(desp)

        despesa.despesas_impostos.set(lista)

        for despesa_imposto in despesa.despesas_impostos.all():
            despesa_imposto.verifica_data_documento_vazio()
            despesa_imposto.atualiza_status()

    @classmethod
    def _processar_impostos_update(cls, despesa, despesas_impostos):
        if despesa.retem_imposto and despesas_impostos:
            logger.info(
                f"Atualizando despesas de impostos da despesa geradora {despesa.uuid}"
            )

            keep = []
            lista = []

            for imposto in despesas_impostos:
                rateios = imposto.pop("rateios", [])

                if not rateios:
                    raise serializers.ValidationError({
                        "mensagem": "A despesa de imposto precisa ter rateio associado"
                    })
            
                imposto.pop("despesas_impostos", None)
                imposto.pop("motivos_pagamento_antecipado", None)

                if "uuid" in imposto:
                    desp = Despesa.by_uuid(imposto["uuid"])
                    for attr, value in imposto.items():
                        setattr(desp, attr, value)
                    desp.save()
                    logger.info(f"Despesa imposto atualizada uuid={desp.uuid}")
                else:
                    imposto["recurso"] = despesa.recurso
                    desp = Despesa.objects.create(**imposto)
                    logger.info(f"Despesa imposto criada uuid={desp.uuid}")

                cls._atualizar_rateios(desp, rateios)

                desp.verifica_data_documento_vazio()
                desp.atualiza_status()

                keep.append(desp.uuid)
                lista.append(desp)                

            despesa.despesas_impostos.exclude(uuid__in=keep).delete()
            despesa.despesas_impostos.set(lista)

        elif not despesa.retem_imposto:
            if despesa.despesas_impostos.exists():
                logger.info(
                    f"Removendo todas as despesas de imposto da despesa {despesa.uuid}"
                )
                despesa.despesas_impostos.all().delete()

        # Atualiza status dos impostos após vínculo
        for despesa_imposto in despesa.despesas_impostos.all():
            despesa_imposto.verifica_data_documento_vazio()
            despesa_imposto.atualiza_status()

    # =====================================================
    # FINALIZAÇÃO
    # =====================================================

    @staticmethod
    def _aplicar_motivos(despesa: Despesa, motivos, outros):
        despesa.motivos_pagamento_antecipado.set([m.id for m in motivos])
        despesa.outros_motivos_pagamento_antecipado = outros

    @staticmethod
    def _finalizar_despesa(despesa: Despesa, rateios, confirmar_limpeza, limpar_callback):
        despesa.atualiza_status()
        despesa.save()

        if despesa.data_transacao:
            despesa.set_despesa_anterior_ao_uso_do_sistema()

        if despesa.status == STATUS_COMPLETO and confirmar_limpeza and limpar_callback:
            limpar_callback(rateios, despesa)