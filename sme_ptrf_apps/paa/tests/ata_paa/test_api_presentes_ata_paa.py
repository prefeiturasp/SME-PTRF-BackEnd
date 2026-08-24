import json
from unittest.mock import patch

import pytest
from requests import ReadTimeout, ConnectTimeout
from rest_framework import status
from sme_ptrf_apps.core.services import TerceirizadasException, SmeIntegracaoApiException

pytestmark = pytest.mark.django_db


def test_get_presentes_ata_paa(
    jwt_authenticated_client_sme,
    flag_paa,
    presente_ata_paa_membro,
    presente_ata_paa_nao_membro
):
    response = jwt_authenticated_client_sme.get(
        f'/api/presentes-ata-paa/?ata_paa__uuid={presente_ata_paa_membro.ata_paa.uuid}',
        content_type='application/json'
    )
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2


def test_create_presente_ata_paa(jwt_authenticated_client_sme, flag_paa, ata_paa):
    payload = {
        "ata_paa": str(ata_paa.uuid),
        "identificacao": "1234567",
        "nome": "Participante Teste",
        "cargo": "Cargo Teste",
        "membro": False,
        "presente": True,
        "professor_gremio": False
    }

    response = jwt_authenticated_client_sme.post(
        '/api/presentes-ata-paa/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_201_CREATED
    result = json.loads(response.content)
    assert result['nome'] == "Participante Teste"
    assert result['identificacao'] == "1234567"


def test_create_presente_ata_paa_professor_gremio(jwt_authenticated_client_sme, flag_paa, ata_paa):
    payload = {
        "ata_paa": str(ata_paa.uuid),
        "identificacao": "1234567",
        "nome": "Professor Grêmio",
        "cargo": "Professor",
        "membro": False,
        "presente": True,
        "professor_gremio": True,
        "presidente_da_reuniao": False,
        "secretario_da_reuniao": False
    }

    response = jwt_authenticated_client_sme.post(
        '/api/presentes-ata-paa/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_201_CREATED
    result = json.loads(response.content)
    assert result['professor_gremio'] is True


def test_create_presente_ata_paa_professor_gremio_pode_ser_presidente(
    jwt_authenticated_client_sme,
    flag_paa,
    ata_paa
):
    payload = {
        "ata_paa": str(ata_paa.uuid),
        "identificacao": "1234567",
        "nome": "Professor Grêmio",
        "cargo": "Professor",
        "membro": False,
        "presente": True,
        "professor_gremio": True,
        "presidente_da_reuniao": True,
        "secretario_da_reuniao": False
    }

    response = jwt_authenticated_client_sme.post(
        '/api/presentes-ata-paa/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_201_CREATED
    result = json.loads(response.content)
    assert result['professor_gremio'] is True
    ata_paa.refresh_from_db()
    assert str(ata_paa.presidente_da_reuniao.uuid) == result['uuid']


def test_create_presente_ata_paa_professor_gremio_pode_ser_secretario(
    jwt_authenticated_client_sme,
    flag_paa,
    ata_paa
):
    payload = {
        "ata_paa": str(ata_paa.uuid),
        "identificacao": "1234567",
        "nome": "Professor Grêmio",
        "cargo": "Professor",
        "membro": False,
        "presente": True,
        "professor_gremio": True,
        "presidente_da_reuniao": False,
        "secretario_da_reuniao": True
    }

    response = jwt_authenticated_client_sme.post(
        '/api/presentes-ata-paa/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_201_CREATED
    result = json.loads(response.content)
    assert result['professor_gremio'] is True
    ata_paa.refresh_from_db()
    assert str(ata_paa.secretario_da_reuniao.uuid) == result['uuid']


@patch('sme_ptrf_apps.paa.api.views.presentes_ata_paa_viewset.TerceirizadasService.get_informacao_servidor')
def test_buscar_informacao_professor_gremio(mock_get_servidor, jwt_authenticated_client_sme, flag_paa):
    mock_get_servidor.return_value = [{
        "nm_pessoa": "João Silva",
        "cargo": "Professor"
    }]

    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/buscar-informacao-professor-gremio/?rf=1234567',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    result = json.loads(response.content)
    assert result['mensagem'] == "buscando-servidor-nao-membro"
    assert result['nome'] == "João Silva"
    assert result['cargo'] == "Professor"


def test_buscar_informacao_professor_gremio_sem_rf(jwt_authenticated_client_sme, flag_paa):
    """
    Testa que o endpoint retorna erro quando o parâmetro RF não é enviado.
    Não precisa de mock pois o endpoint retorna erro antes de chamar o serviço externo.
    """
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/buscar-informacao-professor-gremio/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    result = json.loads(response.content)
    assert result['erro'] == 'parametros_requeridos'


def test_get_participantes_ordenados_por_cargo(
    jwt_authenticated_client_sme,
    flag_paa,
    ata_paa,
    presente_ata_paa_membro,
    presente_ata_paa_nao_membro
):
    response = jwt_authenticated_client_sme.get(
        f'/api/presentes-ata-paa/get-participantes-ordenados-por-cargo/?ata_paa_uuid={ata_paa.uuid}',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    result = json.loads(response.content)
    assert len(result) == 2
    assert 'uuid' in result[0]
    assert 'nome' in result[0]
    assert 'cargo' in result[0]
    assert 'professor_gremio' in result[0]
    assert 'presidente_da_reuniao' in result[0]
    assert 'secretario_da_reuniao' in result[0]


def test_get_padrao_presentes(
    jwt_authenticated_client_sme,
    flag_paa,
    ata_paa,
    membro_associacao
):
    response = jwt_authenticated_client_sme.get(
        f'/api/presentes-ata-paa/padrao-de-presentes/?ata_paa_uuid={ata_paa.uuid}',
        content_type='application/json'
    )
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(result, list)
    # Verifica se retorna pelo menos um membro (se houver membros na associação)
    if len(result) > 0:
        assert 'ata_paa' in result[0]
        assert 'cargo' in result[0]
        assert 'identificacao' in result[0]
        assert 'nome' in result[0]
        assert 'editavel' in result[0]
        assert 'membro' in result[0]
        assert 'presente' in result[0]
        assert result[0]['membro'] is True
        assert result[0]['presente'] is True
        assert result[0]['editavel'] is False


# buscar_informacao_professor_gremio - cenários de erro/exceção

@patch('sme_ptrf_apps.paa.api.views.presentes_ata_paa_viewset.TerceirizadasService.get_informacao_servidor')
def test_buscar_informacao_professor_gremio_sem_resultado(mock_get, jwt_authenticated_client_sme, flag_paa):
    mock_get.return_value = None
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/buscar-informacao-professor-gremio/?rf=1234567',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    result = json.loads(response.content)
    assert result['mensagem'] == 'servidor-nao-encontrado'


@patch('sme_ptrf_apps.paa.api.views.presentes_ata_paa_viewset.TerceirizadasService.get_informacao_servidor')
def test_buscar_informacao_professor_gremio_sme_integracao_exception(mock_get, jwt_authenticated_client_sme, flag_paa):
    mock_get.side_effect = SmeIntegracaoApiException('erro de integração')
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/buscar-informacao-professor-gremio/?rf=1234567',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch('sme_ptrf_apps.paa.api.views.presentes_ata_paa_viewset.TerceirizadasService.get_informacao_servidor')
def test_buscar_informacao_professor_gremio_terceirizadas_exception(mock_get, jwt_authenticated_client_sme, flag_paa):
    mock_get.side_effect = TerceirizadasException('erro terceirizadas')
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/buscar-informacao-professor-gremio/?rf=1234567',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch('sme_ptrf_apps.paa.api.views.presentes_ata_paa_viewset.TerceirizadasService.get_informacao_servidor')
def test_buscar_informacao_professor_gremio_read_timeout(mock_get, jwt_authenticated_client_sme, flag_paa):
    mock_get.side_effect = ReadTimeout()
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/buscar-informacao-professor-gremio/?rf=1234567',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'EOL Timeout' in response.data.get('detail', '')


@patch('sme_ptrf_apps.paa.api.views.presentes_ata_paa_viewset.TerceirizadasService.get_informacao_servidor')
def test_buscar_informacao_professor_gremio_connect_timeout(mock_get, jwt_authenticated_client_sme, flag_paa):
    mock_get.side_effect = ConnectTimeout()
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/buscar-informacao-professor-gremio/?rf=1234567',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'EOL Timeout' in response.data.get('detail', '')


def test_buscar_informacao_professor_gremio_rf_menos_de_7_chars(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/buscar-informacao-professor-gremio/?rf=123',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK
    result = json.loads(response.content)
    assert result['mensagem'] == 'servidor-nao-encontrado'


# get_participantes_ordenados_por_cargo - casos de erro

def test_get_participantes_ordenados_sem_ata_paa_uuid(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/get-participantes-ordenados-por-cargo/',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'erro' in response.data


def test_get_participantes_ordenados_ata_nao_existe(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/get-participantes-ordenados-por-cargo/?ata_paa_uuid=%s' % (
            '00000000-0000-0000-0000-000000000000'
        ),
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'erro' in response.data


# padrao_presentes - sem ata_paa_uuid

def test_padrao_presentes_sem_ata_paa_uuid(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/padrao-de-presentes/',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    result = json.loads(response.content)
    assert result['erro'] == 'parametros_requeridos'


def test_padrao_presentes_uuid_invalido(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get(
        '/api/presentes-ata-paa/padrao-de-presentes/?ata_paa_uuid=uuid-invalido',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_nome_cargo_membro_associacao_sem_identificador(
    jwt_authenticated_client_sme, flag_paa
):
    """Testa o retorno de erro HTTP 400 quando o parâmetro identificador não é informado."""
    response = jwt_authenticated_client_sme.get(
        "/api/presentes-ata-paa/get-nome-cargo-membro-associacao/",
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    result = json.loads(response.content)
    assert result["erro"] == "parametros_requeridos"
    assert result["mensagem"] == "É necessário enviar o identificador."


@patch(
    "sme_ptrf_apps.paa.api.views.presentes_ata_paa_viewset.TerceirizadasService.get_informacao_servidor"
)
def test_get_nome_cargo_membro_associacao_sucesso(
    mock_get_servidor, jwt_authenticated_client_sme, flag_paa
):
    """Testa a busca com sucesso quando o identificador possui 7 caracteres e o servidor é encontrado."""
    mock_get_servidor.return_value = [
        {"nm_pessoa": "Maria Souza", "cargo": "Diretora"}
    ]

    response = jwt_authenticated_client_sme.get(
        "/api/presentes-ata-paa/get-nome-cargo-membro-associacao/?identificador=1234567",
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    result = json.loads(response.content)
    assert result["mensagem"] == "buscando-servidor-nao-membro"
    assert result["nome"] == "Maria Souza"
    assert result["cargo"] == "Diretora"


def test_get_nome_cargo_membro_associacao_tamanho_diferente_de_7(
    jwt_authenticated_client_sme, flag_paa
):
    """Testa que quando o identificador possui tamanho diferente de 7 caracteres, retorna 'servidor-nao-encontrado' sem chamar o serviço externo."""
    response = jwt_authenticated_client_sme.get(
        "/api/presentes-ata-paa/get-nome-cargo-membro-associacao/?identificador=123",
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    result = json.loads(response.content)
    assert result["mensagem"] == "servidor-nao-encontrado"
    assert result["nome"] == ""
    assert result["cargo"] == ""


@patch(
    "sme_ptrf_apps.paa.api.views.presentes_ata_paa_viewset.TerceirizadasService.get_informacao_servidor"
)
def test_get_nome_cargo_membro_associacao_servidor_nao_encontrado(
    mock_get_servidor, jwt_authenticated_client_sme, flag_paa
):
    """Testa o retorno quando o serviço externo não encontra nenhum servidor (retorna lista vazia ou None)."""
    mock_get_servidor.return_value = None

    response = jwt_authenticated_client_sme.get(
        "/api/presentes-ata-paa/get-nome-cargo-membro-associacao/?identificador=1234567",
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    result = json.loads(response.content)
    assert result["mensagem"] == "servidor-nao-encontrado"
    assert result["nome"] == ""
    assert result["cargo"] == ""


@pytest.mark.parametrize(
    "exception_type", [TerceirizadasException, ReadTimeout, ConnectTimeout]
)
@patch(
    "sme_ptrf_apps.paa.api.views.presentes_ata_paa_viewset.TerceirizadasService.get_informacao_servidor"
)
def test_get_nome_cargo_membro_associacao_excecoes_capturadas(
    mock_get_servidor, exception_type, jwt_authenticated_client_sme, flag_paa
):
    """Testa se a action captura as exceções e trata retornando o padrão 'servidor-nao-encontrado' com status 200."""
    mock_get_servidor.side_effect = exception_type

    response = jwt_authenticated_client_sme.get(
        "/api/presentes-ata-paa/get-nome-cargo-membro-associacao/?identificador=1234567",
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_200_OK
    result = json.loads(response.content)
    assert result["mensagem"] == "servidor-nao-encontrado"
    assert result["nome"] == ""
    assert result["cargo"] == ""
