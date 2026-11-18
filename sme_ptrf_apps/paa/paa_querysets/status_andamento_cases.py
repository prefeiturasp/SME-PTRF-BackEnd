"""
Regras de cálculo do ``status_andamento`` do PAA.

Usadas por ``PaaQuerySet.annotate_status_geracao`` para montar as expressões
``Case/When`` de ``status_andamento`` e ``_debug_case``.
"""
from __future__ import annotations

from typing import NamedTuple

from django.db.models import Exists, Q

from sme_ptrf_apps.paa.enums import PaaStatusEnum, PaaStatusAndamentoEnum


class CaseDefinition(NamedTuple):
    """
    Regra usada para calcular o ``status_andamento`` do PAA.

    Attributes:
        condicao: Expressão (Q/Exists) avaliada no banco.
        status: Valor de PaaStatusAndamentoEnum atribuído quando a condição é satisfeita.
        label: Descrição da condição, exibida em ``_debug_case``.
    """
    condicao: Q | Exists
    status: str
    label: str


def get_case_definitions(
    *,
    doc_final_original: Exists,
    doc_final_retificacao: Exists,
    ata_apresentacao: Exists,
    ata_retificacao: Exists,
    ata_retificacao_iniciada: Exists,
) -> list[CaseDefinition]:
    """
    Retorna as regras de cálculo do ``status_andamento``.

    A ordem é relevante: o Case retorna a primeira condição satisfeita,
    por isso as regras de "Fora de Fluxo" devem vir antes das regras de fluxo normal.

    Args:
        doc_final_original: Existe documento final concluído do PAA original.
        doc_final_retificacao: Existe documento final concluído da retificação.
        ata_apresentacao: Existe ata de apresentação concluída.
        ata_retificacao: Existe ata de retificação concluída (PDF gerado).
        ata_retificacao_iniciada: Existe ata de retificação não gerada ou em processamento.
    """
    em_elaboracao = Q(status=PaaStatusEnum.EM_ELABORACAO.name)
    gerado = Q(status=PaaStatusEnum.GERADO.name)
    em_retificacao = Q(status=PaaStatusEnum.EM_RETIFICACAO.name)
    retificado = Q(status=PaaStatusEnum.RETIFICADO.name)
    com_replica = Q(replica__isnull=False)

    return [
        # Fora do Fluxo - Réplica existente no PAA em Elaboração
        CaseDefinition(
            em_elaboracao & com_replica,
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            """
                Em elaboração + com Réplica
                - Necessário remover a réplica
            """,
        ),
        # Fora do Fluxo - Em Elaboração com ata gerada
        CaseDefinition(
            em_elaboracao & ata_apresentacao,
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            """
                Em elaboração + com Ata gerada
                Necessário alterar os campos da ata:
                - Status Pdf: [Não gerado]
                - Documento gerado: [desmarcar]
            """,
        ),
        # Fora de Fluxo - Réplica existente quando gerado
        CaseDefinition(
            gerado & doc_final_original & ata_apresentacao & com_replica,
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            """
                Gerado + Doc Final + Ata + Réplica
                - Necessário remover a réplica
                Obs: Verificar se a réplica foi registrada no log de réplicas
            """,
        ),
        # Fora de Fluxo: é gerado, não tem documento
        CaseDefinition(
            gerado & ~doc_final_original,
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            """
                Gerado + sem Documento final
                Necessário alterar o seguinte campo no PAA e gerar o documento final:
                - status: [Em elaboração]
            """,
        ),
        # Fora de Fluxo: é gerado, não tem ata
        CaseDefinition(
            gerado & ~ata_apresentacao,
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            """
                Gerado + sem Ata
                Necessário regerar a ata, após alterar os seguinte campo no PAA:
                - status: [Em elaboração]
            """,
        ),
        # Fora de Fluxo - Retificação sem Ata iniciada
        CaseDefinition(
            em_retificacao & ~ata_retificacao_iniciada,
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            """
                Em retificação + sem Ata iniciada
                Recomendado cancelar a retificação e iniciá-la novamente
                Ou, criar uma nova ata de retificação via admin, com os seguintes campos:
                - Paa: [ referencia do PAA]
                - Tipo Ata: [Ata de Retificação]
                - justificativa da retificação: [informar a justificativa da retificação]
            """,
        ),
        # Fora de Fluxo - Retificação sem Réplica
        CaseDefinition(
            em_retificacao & ata_retificacao_iniciada & ~com_replica,
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            """
                Em retificação + sem Réplica
                Recomendado cancelar a retificação e iniciá-la novamente
                Obs: Sem réplica registrada não é possível registrar log ou realizar cancelamento seguro do
                que foi alterado no PAA
            """,
        ),

        # Fora de Fluxo - Gerado com Documento e Ata de retificação
        CaseDefinition(
            gerado & doc_final_retificacao & ata_retificacao,
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            """
                Gerado + Doc Final Retificação + Ata Retificação
                A retificação foi concluída, mas o status do PAA não foi atualizado.
                Necessário alterar o seguinte campo no PAA:
                - status: [Retificado]
            """,
        ),

        # Gerado completo - é gerado, tem documento e tem ata
        CaseDefinition(
            gerado & doc_final_original & ata_apresentacao,
            PaaStatusAndamentoEnum.GERADO.name,
            'Gerado + Doc Final + Ata',
        ),
        # Retificação com Réplica + Doc de retificação gerado
        CaseDefinition(
            em_retificacao & com_replica & doc_final_retificacao & ata_retificacao_iniciada,
            PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name,
            'Em retificação + com Réplica + Doc Retificação gerado + Ata iniciada',
        ),
        # Retificação correta quando há uma Réplica
        CaseDefinition(
            em_retificacao & com_replica & ata_retificacao_iniciada,
            PaaStatusAndamentoEnum.EM_RETIFICACAO.name,
            'Em retificação + com Réplica + Ata iniciada',
        ),
        # Fora de Fluxo: retificado sem documento final de retificação
        CaseDefinition(
            retificado & ~doc_final_retificacao,
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            'Retificado + sem Documento final de retificação',
        ),
        # Fora de Fluxo: retificado sem ata de retificação
        CaseDefinition(
            retificado & ~ata_retificacao,
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            'Retificado + sem Ata de retificação',
        ),
        # Retificado completo
        CaseDefinition(
            retificado & doc_final_retificacao & ata_retificacao,
            PaaStatusAndamentoEnum.GERADO.name,
            'Retificado + Doc Final Retificação + Ata Retificação',
        ),
        # Em Elaboração quando tem apenas documento final concluído
        CaseDefinition(
            em_elaboracao & doc_final_original,
            PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name,
            'Em elaboração + Doc Final',
        ),
        # Em elaboração
        CaseDefinition(
            em_elaboracao & ~doc_final_original & ~ata_apresentacao,
            PaaStatusAndamentoEnum.EM_ELABORACAO.name,
            'Em elaboração',
        ),
        # Fluxo não iniciado
        CaseDefinition(
            Q(status=PaaStatusEnum.NAO_INICIADO.name),
            PaaStatusAndamentoEnum.FORA_FLUXO.name,
            'PAA existente não pode ser "Não iniciado"',
        ),
    ]
