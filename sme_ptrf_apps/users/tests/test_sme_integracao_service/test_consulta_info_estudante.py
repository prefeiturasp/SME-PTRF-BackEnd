import json
from unittest.mock import patch

import pytest

from rest_framework import status

from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


@override_flag('historico-de-membros', active=True)
def test_consulta_informacao_estudante(jwt_authenticated_client_sme):
    path = 'sme_ptrf_apps.mandatos.api.views.ocupantes_cargos_viewset.SmeIntegracaoService.get_informacao_aluno'
    with patch(path) as mock_get:
        data = {
            "codigoAluno": 5722148,
            "tipoTurno": 0,
            "anoLetivo": 2023,
            "nomeAluno": "BIANCA SILVA MEDEIROS",
            "nomeSocialAluno": None,
            "codigoSituacaoMatricula": 14,
            "situacaoMatricula": "Remanejado Saída",
            "dataSituacao": "2023-01-30T14:05:23.16",
            "dataNascimento": "2009-03-10T00:00:00",
            "numeroAlunoChamada": "0",
            "codigoTurma": 2506420,
            "nomeResponsavel": "MARIA MARCIA SILVA DOS SANTOS",
            "tipoResponsavel": "1",
            "celularResponsavel": "11964365099",
            "dataAtualizacaoContato": "2021-10-19T16:21:12.513",
            "codigoTipoTurma": 1,
            "turmaNome": None,
            "etapaEnsino": None,
            "cicloEnsino": None,
            "descEtapaEnsino": None,
            "descCicloEnsino": None
        }

        mock_get.return_value = data

        response = jwt_authenticated_client_sme.get(f'/api/ocupantes-cargos/codigo-identificacao/?codigo-eol={5722148}')
        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == data
