from typing import Optional
from sme_ptrf_apps.paa.models import Paa, ReplicaPaa, DocumentoPaa, AtaPaa


class CicloRetificacaoService:
    """Representa o ciclo de retificação corrente de um PAA.

    Argumentos:
        paa: Instância do PAA.
    """

    def __init__(self, paa: Paa) -> None:
        self._paa = paa
        self._replica: Optional[ReplicaPaa] = self._carregar_replica()

    def _carregar_replica(self) -> Optional[ReplicaPaa]:
        try:
            return self._paa.replica
        except ReplicaPaa.DoesNotExist:
            return None

    def _uuid_snapshot(self, chave: str) -> Optional[str]:
        if not self._replica:
            return None
        return (self._replica.historico.get(chave) or {}).get('uuid')

    def _pertence_ao_ciclo_atual(self, uuid_artefato: Optional[str], uuid_snap: Optional[str]) -> bool:
        if not uuid_artefato:
            return False
        return str(uuid_artefato) != str(uuid_snap) if uuid_snap else True

    @property
    def numero_versao(self) -> int:
        """1 para R1, 2 para R2, etc."""
        versao_anterior = (
            (self._replica.historico.get('documento_retificado') or {}).get('versao_documento')
            if self._replica else None
        )
        return (versao_anterior or 0) + 1

    @property
    def documento_atual(self) -> Optional[DocumentoPaa]:
        """Doc retificado do ciclo corrente; None se ainda não gerado."""
        doc = (
            self._paa.documentopaa_set
            .filter(
                retificacao=True,
                versao=DocumentoPaa.VersaoChoices.FINAL
            )
            .order_by('-pk')
            .first()
        )
        if not doc:
            return None
        return doc if self._pertence_ao_ciclo_atual(
            str(doc.uuid), self._uuid_snapshot('documento_retificado')) else None

    @property
    def tem_documento_final_concluido(self) -> bool:
        doc = (
            self._paa.documentopaa_set
            .filter(
                retificacao=True,
                versao=DocumentoPaa.VersaoChoices.FINAL,
                status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO
            )
            .order_by('-pk')
            .first()
        )
        return self._pertence_ao_ciclo_atual(str(doc.uuid) if doc else None,
                                             self._uuid_snapshot('documento_retificado'))

    @property
    def tem_ata_concluida(self) -> bool:
        ata = (
            self._paa.atas_da_paa
            .filter(
                tipo_ata=AtaPaa.ATA_RETIFICACAO,
                previa=False,
                status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
                pdf_gerado_previamente=True
            )
            .order_by('-pk')
            .first()
        )
        return self._pertence_ao_ciclo_atual(str(ata.uuid) if ata else None,
                                             self._uuid_snapshot('ata_retificada'))
