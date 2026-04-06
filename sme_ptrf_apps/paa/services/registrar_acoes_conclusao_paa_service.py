import logging

from sme_ptrf_apps.paa.services.acoes_paa_service import AcoesPaaService

logger = logging.getLogger(__name__)


class RegistrarAcoesPtrfConclusaoPaaService:
    @classmethod
    def registrar(cls, paa):
        """
        Registra todas as ações do tipo PTRF (core_acao) com exibir_paa=True
        que estavam disponíveis no momento da conclusão do PAA.

        Args:
            paa: Instância do modelo Paa

        Returns:
            int: Quantidade de ações registradas
        """
        acoes_associacoes = AcoesPaaService(paa).obter_ptrf()
        acoes_ids = acoes_associacoes.values_list('acao_id', flat=True)

        paa.acoes_conclusao.add(*acoes_ids)

        quantidade_registrada = len(acoes_ids)
        logger.info(f'Registradas {quantidade_registrada} ações PTRF disponíveis na conclusão do PAA {paa.uuid}')

        return quantidade_registrada


class RegistrarAcoesPddeConclusaoPaaService:
    @classmethod
    def registrar(cls, paa):
        """
        Registra todas as ações PDDE com status ATIVA
        que estavam disponíveis no momento da conclusão do PAA.

        Args:
            paa: Instância do modelo Paa

        Returns:
            int: Quantidade de ações registradas
        """
        acoes_pdde_ativas = AcoesPaaService(paa).obter_pdde()

        paa.acoes_pdde_conclusao.add(*acoes_pdde_ativas)

        quantidade_registrada = acoes_pdde_ativas.count()
        logger.info(f'Registradas {quantidade_registrada} ações PDDE disponíveis na conclusão do PAA {paa.uuid}')

        return quantidade_registrada


class RegistrarAcoesOutrosRecursosConclusaoPaaService:
    @classmethod
    def registrar(cls, paa):
        """
        Registra todas as ações de outros recursos vinculados à unidade e período do PAA
        que estavam disponíveis no momento da conclusão do PAA.

        Args:
            paa: Instância do modelo Paa

        Returns:
            int: Quantidade de ações registradas
        """
        outros_recursos_disponiveis = AcoesPaaService(paa).obter_outros_recursos_periodo()

        paa.outros_recursos_periodo_conclusao.add(*outros_recursos_disponiveis)

        quantidade_registrada = outros_recursos_disponiveis.count()
        logger.info((
            f'Registradas {quantidade_registrada} ações de outros recursos '
            f'disponíveis na conclusão do PAA {paa.uuid}'))

        return quantidade_registrada
