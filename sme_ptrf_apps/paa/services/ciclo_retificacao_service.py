from typing import Optional
from sme_ptrf_apps.paa.models import Paa, ReplicaPaa, DocumentoPaa, AtaPaa


class CicloRetificacaoService:
    """Representa o ciclo de retificação corrente de um PAA.

    Args:
        paa: Instância do PAA cujo ciclo de retificação será consultado.
    """

    def __init__(self, paa: Paa) -> None:
        """Inicializa o serviço com o PAA a ser consultado.

        Args:
            paa: Instância do PAA que pode possuir uma réplica de retificação.
        """
        self._paa: Paa = paa
        self._replica: Optional[ReplicaPaa] = self._carregar_replica()

    def _carregar_replica(self) -> Optional[ReplicaPaa]:
        """Obtém a réplica associada ao PAA, quando ela existe.

        Returns:
            A réplica associada ao PAA ou `None` quando não há réplica.
        """
        try:
            return self._paa.replica
        except ReplicaPaa.DoesNotExist:
            return None

    def _uuid_snapshot(self, chave: str) -> Optional[str]:
        """Obtém do histórico da réplica o UUID salvo para uma chave.

        Args:
            chave: Chave do artefato no histórico da réplica.

        Returns:
            UUID salvo no snapshot ou `None` quando não há réplica ou valor.
        """
        if not self._replica:
            return None
        return (self._replica.historico.get(chave) or {}).get('uuid')

    def _pertence_ao_ciclo_atual(self, uuid_artefato: Optional[str], uuid_snap: Optional[str]) -> bool:
        """Verifica se um artefato pertence ao ciclo de retificação atual.

        Args:
            uuid_artefato: UUID do artefato que será verificado.
            uuid_snap: UUID do mesmo artefato registrado no snapshot anterior.

        Returns:
            `True` quando há um artefato e ele é novo em relação ao snapshot;
            caso contrário, `False`.
        """
        if not uuid_artefato:
            return False
        return str(uuid_artefato) != str(uuid_snap) if uuid_snap else True

    @property
    def numero_versao(self) -> int:
        """Retorna o número da próxima versão de retificação do documento.
            1 para R1, 2 para R2, etc.
        """
        versao_anterior = (
            (self._replica.historico.get('documento_retificado') or {}).get('versao_documento')
            if self._replica else None
        )
        return (versao_anterior or 0) + 1

    @property
    def documento_atual(self) -> Optional[DocumentoPaa]:
        """Retorna o documento final de retificação do ciclo corrente.

        Returns:
            Documento final mais recente do ciclo ou `None` quando ele ainda
            não foi gerado ou pertence a um ciclo anterior.
        """
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
        """Indica se o documento final do ciclo corrente foi concluído.

        Returns:
            `True` quando existe documento final concluído pertencente ao ciclo
            corrente; caso contrário, `False`.
        """
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
        """Indica se a ata de retificação do ciclo corrente foi concluída.

        Returns:
            `True` quando existe ata concluída pertencente ao ciclo corrente;
            caso contrário, `False`.
        """
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
