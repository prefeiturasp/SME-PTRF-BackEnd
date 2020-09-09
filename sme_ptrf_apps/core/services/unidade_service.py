import requests
import logging

from django.conf import settings
from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.dre.models import Atribuicao
from sme_ptrf_apps.dre.api.serializers.tecnico_dre_serializer import TecnicoDreLookUpSerializer

logger = logging.getLogger(__name__)


def monta_unidade_para_atribuicao(queryset, dre_uuid, periodo):
    list_unidades = []
    for unidade in queryset.filter(dre__uuid=dre_uuid).all():
        atribuicao = Atribuicao.objects.filter(unidade__uuid=unidade.uuid, periodo__uuid=periodo).first()
        d = {
            "uuid": str(unidade.uuid),
            "codigo_eol": unidade.codigo_eol,
            "nome": f'{unidade.tipo_unidade} {unidade.nome}',
            "atribuicao": {
                "id": atribuicao.id if atribuicao else "",
                "tecnico": TecnicoDreLookUpSerializer(atribuicao.tecnico).data if atribuicao else {}
            }
        }
        list_unidades.append(d)

    return list_unidades


def atualiza_dados_unidade(associacao) -> None:
    """
    Responsável por atualizar os dados da unidade vinculada a associação
    recebida como parâmetro.
    Os dados são consultados de duas APIs: API do eol e API do SGP.
    """
    unidade: Unidade = associacao.unidade
    logger.info("Atualizando dados da unidade %s", str(unidade))

    atualiza_dados_pessoais_unidade(unidade)
    atualiza_diretor_unidade(unidade)
    logger.info("Dados da unidade %s atualizados com sucesso.", str(unidade))


def atualiza_dados_pessoais_unidade(unidade: Unidade) -> None:
    """Consulta informações da unidade na API do eol"""
    headers_eol = {
        "Authorization": f"Token {settings.EOL_API_TERCEIRIZADAS_TOKEN}"
    }
    timeout = 10

    try:
        response = requests.get(f'{settings.EOL_API_TERCEIRIZADAS_URL}/escolas_terceirizadas/',
                                headers=headers_eol, timeout=timeout)
        results = response.json()['results']
        resultado = list(filter(lambda d: d['cd_unidade_educacao'] == unidade.codigo_eol, results))
        if resultado:
            unidade_retorno = resultado[0]
            unidade.nome = unidade_retorno['nm_unidade_educacao']
            unidade.email = unidade_retorno['email']
            unidade.telefone = unidade_retorno['tel1']
            unidade.numero = unidade_retorno['cd_nr_endereco']
            unidade.tipo_logradouro = unidade_retorno['dc_tp_logradouro']
            unidade.logradouro = unidade_retorno['nm_logradouro']
            unidade.bairro = unidade_retorno['nm_bairro']
            unidade.cep = f"{unidade_retorno['cd_cep']:0>8}"
            unidade.save()
    except Exception as err:
        logger.info("Erro ao Atualizar dados pessoais da unidade %s", err)


def atualiza_diretor_unidade(unidade: Unidade) -> None:
    """Consulta informação do diretor da unidade na API do sgp"""
    headers_sgp = {
        "x-api-eol-key": f"{settings.SME_INTEGRACAO_TOKEN}"
    }

    timeout = 10
    codigo_cargo = '3360'

    try:
        response = requests.get(f'{settings.SME_INTEGRACAO_URL}/api/escolas/{unidade.codigo_eol}/funcionarios/cargos/{codigo_cargo}',
                                headers=headers_sgp, timeout=timeout)
        resultado = response.json()
        if resultado:
            unidade.diretor_nome = resultado[0]['nomeServidor']
        logger.info(response.json())
    except Exception as err:
        logger.info("Erro ao atualizar diretor: %s", err)
