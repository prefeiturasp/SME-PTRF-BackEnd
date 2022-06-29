import logging
from django.forms.models import model_to_dict
from sme_ptrf_apps.core.models.ata import Ata
from sme_ptrf_apps.core.services.ata_dados_service import gerar_dados_ata
from sme_ptrf_apps.core.services.ata_pdf_service import gerar_arquivo_ata_pdf
from sme_ptrf_apps.core.services.associacoes_service import retorna_repasses_pendentes_periodos_ate_agora

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

    msg = ''
    if ata.presidente_reuniao and not presidente_presente:
        msg = 'informe um presidente presente.'

    if ata.secretario_reuniao and not secretario_presente:
        msg = 'informe um secretario presente.'

    if (ata.presidente_reuniao and ata.secretario_reuniao) and (not presidente_presente and not secretario_presente):
        msg = 'informe um presidente presente, informe um secretário presente.'

    campos_invalidos.append({'msg_presente': msg}) if msg else None

    if campos_invalidos:
        return {'is_valid': False, 'campos': campos_invalidos}
    return {'is_valid': True}
