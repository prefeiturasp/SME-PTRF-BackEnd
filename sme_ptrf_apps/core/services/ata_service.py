import logging
from django.forms.models import model_to_dict
from sme_ptrf_apps.core.models.ata import Ata
from sme_ptrf_apps.core.services.ata_dados_service import gerar_dados_ata
from sme_ptrf_apps.core.services.ata_pdf_service import gerar_arquivo_ata_pdf
from sme_ptrf_apps.core.services.associacoes_service import retorna_repasses_pendentes_periodos_ate_agora
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.core.models import Parametros

LOGGER = logging.getLogger(__name__)


def gerar_arquivo_ata(prestacao_de_contas=None, ata=None, usuario=None):
    LOGGER.info(f"Gerando Arquivo da Ata, prestacao de contas {prestacao_de_contas.uuid} e ata {ata.uuid}")

    ata.arquivo_pdf_iniciar()

    try:
        dados_ata = gerar_dados_ata(prestacao_de_contas=prestacao_de_contas, ata=ata, usuario=usuario)
        gerar_arquivo_ata_pdf(dados_ata=dados_ata, ata=ata)
        LOGGER.info(f'Gerando arquivo ata em PDF')
        ata.arquivo_pdf_concluir()
        return ata
    except Exception as e:
        LOGGER.info(f'FALHA AO GERAR O ARQUIVO DA ATA', e)
        ata.arquivo_pdf_nao_gerado()
        return None


def validar_campos_ata(ata: Ata = None) -> dict:
    campos_traduzidos = {
        'cargo_presidente_reuniao': 'Cargo Presidente',
        'cargo_secretaria_reuniao': 'Cargo Secretário',
        'data_reuniao': 'Data',
        'hora_reuniao': 'Hora',
        'justificativa_repasses_pendentes': 'Justificativa',
        'local_reuniao': 'Local da reunião',
        'presidente_reuniao': 'Presidente da reunião',
        'secretario_reuniao': 'Secretário da reunião',
    }
    campos_invalidos, campos_nao_required = list(), [
        'arquivo_pdf',
        'comentarios',
        'retificacoes',
        'justificativa_repasses_pendentes'
    ]
    repasse_pendentes = retorna_repasses_pendentes_periodos_ate_agora(
        ata.associacao,
        ata.periodo
    )

    for campo, valor in model_to_dict(ata).items():

        if valor in [None, ''] and campo not in campos_nao_required:
            campos_invalidos.append(campo)
    if repasse_pendentes and ata.justificativa_repasses_pendentes == '':
        campos_invalidos.append('justificativa_repasses_pendentes')

    presidente_presente = ata.presentes_na_ata.filter(
        nome=ata.presidente_reuniao
    ).exists()

    secretario_presente = ata.presentes_na_ata.filter(
        nome=ata.secretario_reuniao
    ).exists()

    campos_invalidos_traduzidos = list()
    for campo, valor in campos_traduzidos.items():
        if campo in campos_invalidos:
            campos_invalidos_traduzidos.append(valor)
    msg = ''
    if ata.presidente_reuniao and not presidente_presente:
        msg = 'informe um presidente presente'

    if ata.secretario_reuniao and not secretario_presente:
        msg = 'informe um secretario presente'

    if (ata.presidente_reuniao and ata.secretario_reuniao) and (not presidente_presente and not secretario_presente):
        msg = 'informe um presidente presente, informe um secretário presente'

    campos_invalidos_traduzidos.append({'msg_presente': msg}) if msg else None

    if campos_invalidos_traduzidos:
        return {'is_valid': False, 'campos': campos_invalidos_traduzidos}
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


def verifica_precisa_professor_gremio_ata(ata: Ata) -> bool:
    """
    Verifica se a unidade da associação precisa do campo professor do grêmio na ata.
    
    A regra é:
    1. O tipo de unidade deve estar na lista configurada em parametros.tipos_unidades_professor_gremio
    2. Deve haver despesas completas com rateio de ação "Orçamento Grêmio Estudantil" 
       no período da prestação de contas
    
    Args:
        ata: Instância de Ata
        
    Returns:
        bool: True se precisa de professor do grêmio, False caso contrário
    """
    if not ata.associacao or not ata.associacao.unidade:
        return False

    tipo_unidade = ata.associacao.unidade.tipo_unidade
    if not unidade_precisa_professor_gremio(tipo_unidade):
        return False

    if not ata.periodo:
        return False
    
    periodo = ata.periodo
    associacao = ata.associacao

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
        despesa__data_transacao__gte=periodo.data_inicio_realizacao_despesas
    )
    
    if periodo.data_fim_realizacao_despesas:
        rateios_query = rateios_query.filter(
            despesa__data_transacao__lte=periodo.data_fim_realizacao_despesas
        )
    
    return rateios_query.exists()
