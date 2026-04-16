from unittest.mock import patch, Mock
from sme_ptrf_apps.users.services.sme_integracao_service import SmeIntegracaoService


@patch("sme_ptrf_apps.users.services.sme_integracao_service.requests.get")
def test_usuario_core_sso_retorna_none_quando_nome_nulo(mock_get):

    login = "usuario_teste"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "nome": None,
        "email": "teste@email.com"
    }

    mock_get.return_value = mock_response
    result = SmeIntegracaoService.usuario_core_sso_or_none(login)

    assert result is None
    mock_get.assert_called_once()
