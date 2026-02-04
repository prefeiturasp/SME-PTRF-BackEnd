import logging

from sme_ptrf_apps.core.models import Acao
from sme_ptrf_apps.paa.models import AcaoPdde, OutroRecursoPeriodoPaa

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
        acoes_ptrf = Acao.objects.filter(exibir_paa=True)
        
        paa.acoes_conclusao.set(acoes_ptrf)
        
        quantidade_registrada = acoes_ptrf.count()
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
        acoes_pdde_ativas = AcaoPdde.objects.filter(status=AcaoPdde.STATUS_ATIVA)
        
        paa.acoes_pdde_conclusao.set(acoes_pdde_ativas)
        
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
        outros_recursos_disponiveis = OutroRecursoPeriodoPaa.objects.disponiveis_para_paa(paa)

        paa.outros_recursos_periodo_conclusao.set(outros_recursos_disponiveis)
        
        quantidade_registrada = outros_recursos_disponiveis.count()
        logger.info(f'Registradas {quantidade_registrada} ações de outros recursos disponíveis na conclusão do PAA {paa.uuid}')
        
        return quantidade_registrada
