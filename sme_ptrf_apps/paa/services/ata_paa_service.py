import logging
from django.db import transaction

from sme_ptrf_apps.paa.models import AtaPaa, LogReplicaPaa
from sme_ptrf_apps.paa.models.documento_paa import obter_documento_final_por_retificacao
from sme_ptrf_apps.paa.services.ata_paa_dados_service import gerar_dados_ata_paa
from sme_ptrf_apps.paa.services.ata_paa_pdf_service import gerar_arquivo_ata_paa_pdf
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.core.models import Parametros
from sme_ptrf_apps.paa.services.paa_service import PaaService

LOGGER = logging.getLogger(__name__)


def _salvar_log_replica(paa, replica) -> LogReplicaPaa:
    """
    Registra snapshot da réplica no log ao concluir a retificação com êxito.

    Args:
        paa: Instância do Paa.
        replica: Instância de ReplicaPaa associada ao PAA.

    Returns:
        LogReplicaPaa criado.
    """
    historico = replica.historico or {}
    # versao_documento no historico é a versão do documento que foi retificado (Rn-1).
    # O log deve registrar a versão que está sendo concluída agora (Rn = Rn-1 + 1).
    # None indica que não havia retificação anterior (R1 concluindo), portanto Rn = 1.
    versao_anterior = (
        historico
        .get('documento_retificado', {})
        .get('versao_documento')
    )
    versao_documento = (versao_anterior or 0) + 1
    log = LogReplicaPaa.objects.create(
        paa=paa,
        origem=LogReplicaPaa.CONCLUSAO,
        replica=historico,
        numero_versao_documento=versao_documento,
    )
    LOGGER.info(
        f'Log da réplica salvo (CONCLUSAO) versão={versao_documento} para PAA {paa.id}'
    )
    return log


def _remover_replica(replica) -> None:
    """
    Remove a réplica do PAA após o log de réplica ter sido salvo com êxito.

    Args:
        replica: Instância de ReplicaPaa a ser removida.
    """
    replica_id = replica.id
    replica.delete()
    LOGGER.info(f'Réplica removida id={replica_id}')


def _apagar_atas_retificacao_anteriores(ata_paa: AtaPaa) -> None:
    """
    Remove atas de retificação de ciclos anteriores ao concluir o ciclo atual.

    Mantém apenas o registro corrente (ata_paa.pk) e apaga todos os demais
    registros ATA_RETIFICACAO do mesmo PAA, espelhando o comportamento de
    DocumentoPaaService.apagar_documento_anteriores para documentos.
    """
    deleted_count, _ = (
        AtaPaa.objects
        .filter(paa=ata_paa.paa, tipo_ata=AtaPaa.ATA_RETIFICACAO)
        .exclude(pk=ata_paa.pk)
        .delete()
    )
    if deleted_count:
        LOGGER.info(
            f'Atas de retificação anteriores removidas (count={deleted_count}) '
            f'ao concluir ata {ata_paa.uuid} do PAA {ata_paa.paa_id}'
        )


def gerar_arquivo_ata_paa_retificacao(ata_paa: AtaPaa, usuario=None) -> AtaPaa | None:
    """
    Gera o arquivo PDF da ata PAA de Retificação.

    Comportamentos garantidos:
    - Permite regerar mesmo que já exista um PDF anterior (única versão mantida).
    - Em caso de falha na geração do PDF, restaura a referência ao arquivo anterior
      para não perder o último PDF válido.
    - ``arquivo_pdf_concluir()`` é chamado fora da transação para que o arquivo
      físico seja marcado como válido independentemente do bloco seguinte. Se a
      transação falhar, o bloco ``except`` reseta o status para NAO_GERADO via
      ``arquivo_pdf_nao_gerado()``, permitindo nova tentativa.
    - Ao concluir com êxito: apaga atas de retificação de ciclos anteriores,
      salva log de réplica com origem CONCLUSAO, remove a réplica do PAA e
      atualiza o status do PAA para GERADO atomicamente.

    Args:
        ata_paa: Instância de AtaPaa do tipo RETIFICACAO.
        usuario: Usuário que disparou a geração (opcional).

    Returns:
        AtaPaa atualizada em caso de sucesso, ou None em caso de falha.
    """
    LOGGER.info(f"Gerando arquivo da Ata PAA de Retificação {ata_paa.uuid}")

    old_arquivo_pdf_name = ata_paa.arquivo_pdf.name if ata_paa.arquivo_pdf else None

    ata_paa.arquivo_pdf_iniciar()

    try:
        dados_ata = gerar_dados_ata_paa(ata_paa=ata_paa, usuario=usuario)
        gerar_arquivo_ata_paa_pdf(dados_ata=dados_ata, ata_paa=ata_paa)

        # Marca o PDF como concluído antes da transação. Se o bloco transacional
        # falhar, o except reseta o status via arquivo_pdf_nao_gerado().
        ata_paa.arquivo_pdf_concluir()

        paa = ata_paa.paa
        replica = getattr(paa, 'replica', None)

        with transaction.atomic():
            if replica:
                _salvar_log_replica(paa=paa, replica=replica)
                _remover_replica(replica=replica)
            _apagar_atas_retificacao_anteriores(ata_paa)
            PaaService.concluir_paa(paa)

        LOGGER.info(f'Arquivo ata PAA de retificação {ata_paa.uuid} gerado com sucesso.')
        return ata_paa

    except Exception as e:
        LOGGER.exception(f'FALHA AO GERAR O ARQUIVO DA ATA PAA DE RETIFICAÇÃO {ata_paa.uuid}: {str(e)}')
        # Restaura referência ao arquivo anterior apenas quando o PDF novo não foi
        # confirmado — documento_gerado False indica que o arquivo físico válido
        # ainda é o anterior.
        if not ata_paa.documento_gerado and old_arquivo_pdf_name:
            ata_paa.arquivo_pdf = old_arquivo_pdf_name
        ata_paa.arquivo_pdf_nao_gerado()
        return None


def gerar_arquivo_ata_paa(ata_paa: AtaPaa, usuario=None):
    """
    Gera o arquivo PDF da ata PAA final
    """
    LOGGER.info(f"Gerando arquivo da Ata PAA {ata_paa.uuid}")

    ata_paa.arquivo_pdf_iniciar()

    try:
        dados_ata = gerar_dados_ata_paa(ata_paa=ata_paa, usuario=usuario)
        gerar_arquivo_ata_paa_pdf(dados_ata=dados_ata, ata_paa=ata_paa)
        LOGGER.info('Arquivo ata PAA em PDF gerado com sucesso')

        ata_paa.arquivo_pdf_concluir()

        PaaService.concluir_paa(ata_paa.paa)

        return ata_paa
    except Exception as e:
        LOGGER.exception(f'FALHA AO GERAR O ARQUIVO DA ATA PAA: {str(e)}')
        ata_paa.arquivo_pdf_nao_gerado()
        return None


def validar_geracao_ata_paa(ata_paa: AtaPaa) -> dict:
    """
    Valida se a ata PAA pode ser gerada
    """
    errors = []

    if not ata_paa.completa:
        errors.append("Todos os dados da edição da ata devem estar preenchidos")

    paa = ata_paa.paa
    if paa.status_em_retificacao:
        from sme_ptrf_apps.paa.services.ciclo_retificacao_service import CicloRetificacaoService
        tem_doc_final = CicloRetificacaoService(paa).tem_documento_final_concluido
    else:
        documento_final = obter_documento_final_por_retificacao(paa, ata_paa.tipo_retificacao)
        tem_doc_final = bool(documento_final and documento_final.concluido)

    if not tem_doc_final:
        errors.append("O documento Plano Anual deve estar gerado")

    if ata_paa.tipo_apresentacao and ata_paa.documento_gerado:
        errors.append("A ata já foi gerada anteriormente")

    if ata_paa.documento_em_processamento:
        errors.append("A ata já está sendo gerada")

    if errors:
        msg = '\n'.join(errors)
        LOGGER.error('Validação não permite gerar Ata do PA: %s' % msg)
        return {
            'is_valid': False,
            'mensagem': msg
        }

    return {'is_valid': True}


def unidade_precisa_professor_gremio(tipo_unidade: str) -> bool:
    """
    Verifica se o tipo de unidade precisa do campo professor do grêmio na ata.

    Args:
        tipo_unidade: String com o tipo de unidade (ex: 'EMEF', 'EMEI', etc.)

    Returns:
        bool: True se o tipo de unidade precisa de professor do grêmio, False caso contrário
    """
    parametros = Parametros.objects.first()
    if not parametros or not parametros.tipos_unidades_professor_gremio:
        return False
    return tipo_unidade in parametros.tipos_unidades_professor_gremio


def verifica_precisa_professor_gremio(ata_paa: AtaPaa) -> bool:
    """
    Verifica se a unidade da associação precisa do campo professor do grêmio.

    A regra é:
    1. O tipo de unidade deve estar na lista configurada em parametros.tipos_unidades_professor_gremio
    2. Deve haver despesas completas com rateio de ação "Orçamento Grêmio Estudantil"
       no período do PAA

    Args:
        ata_paa: Instância de AtaPaa

    Returns:
        bool: True se precisa de professor do grêmio, False caso contrário
    """
    if not ata_paa.paa or not ata_paa.paa.associacao or not ata_paa.paa.associacao.unidade:
        return False

    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    if not unidade_precisa_professor_gremio(tipo_unidade):
        return False

    if not ata_paa.paa.periodo_paa:
        return False

    periodo_paa = ata_paa.paa.periodo_paa
    associacao = ata_paa.paa.associacao

    acao_gremio = associacao.acoes.filter(
        acao__nome__icontains='Orçamento Grêmio Estudantil',
        status='ATIVA'
    ).first()

    if not acao_gremio:
        return False

    rateios_query = RateioDespesa.completos.filter(
        acao_associacao=acao_gremio,
        associacao=associacao
    ).filter(
        despesa__data_transacao__gte=periodo_paa.data_inicial
    )

    if periodo_paa.data_final:
        rateios_query = rateios_query.filter(
            despesa__data_transacao__lte=periodo_paa.data_final
        )

    return rateios_query.exists()
