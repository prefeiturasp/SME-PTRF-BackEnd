import logging

from sme_ptrf_apps.paa.models import AtaPaa, Paa
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.services.ata_paa_dados_service import gerar_dados_ata_paa
from sme_ptrf_apps.paa.services.ata_paa_pdf_service import gerar_arquivo_ata_paa_pdf
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.core.models import Parametros

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


def unidade_precisa_professor_gremio(tipo_unidade: str) -> bool:
    """
    Verifica se o tipo de unidade precisa do campo professor do grêmio na ata do PAA.
    
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

