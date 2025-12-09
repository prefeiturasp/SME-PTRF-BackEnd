import logging

from sme_ptrf_apps.paa.models import AtaPaa, Paa
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.services.ata_paa_dados_service import gerar_dados_ata_paa
from sme_ptrf_apps.paa.services.ata_paa_pdf_service import gerar_arquivo_ata_paa_pdf

LOGGER = logging.getLogger(__name__)


def gerar_arquivo_ata_paa(ata_paa: AtaPaa, usuario=None):
    """
    Gera o arquivo PDF da ata PAA final
    """
    LOGGER.info(f"Gerando arquivo da Ata PAA {ata_paa.uuid}")
    
    ata_paa.arquivo_pdf_iniciar()
    
    try:
        dados_ata = gerar_dados_ata_paa(ata_paa=ata_paa, usuario=usuario)
        gerar_arquivo_ata_paa_pdf(dados_ata=dados_ata, ata_paa=ata_paa)
        LOGGER.info(f'Arquivo ata PAA em PDF gerado com sucesso')
        
        ata_paa.arquivo_pdf_concluir()
        
        # Atualiza o status do PAA para GERADO
        paa = ata_paa.paa
        paa.status = PaaStatusEnum.GERADO.name
        paa.save()
        LOGGER.info(f'Status do PAA {paa.uuid} atualizado para GERADO')
        
        return ata_paa
    except Exception as e:
        LOGGER.error(f'FALHA AO GERAR O ARQUIVO DA ATA PAA: {str(e)}', exc_info=True)
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
    documento_final = paa.documento_final
    
    if not documento_final or documento_final.status_geracao != 'CONCLUIDO':
        errors.append("O documento Plano Anual deve estar gerado")
    
    # Valida se já foi gerado anteriormente
    if ata_paa.documento_gerado:
        errors.append("A ata já foi gerada anteriormente")
    
    if errors:
        return {
            'is_valid': False,
            'mensagem': '\n'.join(errors)
        }
    
    return {'is_valid': True}

