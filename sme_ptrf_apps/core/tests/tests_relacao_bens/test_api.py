import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_relacoes_info_sem_bens_adquiridos(jwt_authenticated_client_a, periodo, conta_associacao):
    url = f"/api/relacao-bens/relacao-bens-info/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}"
    response = jwt_authenticated_client_a.get(url)
    result = response.json()

    assert result == "Não houve bem adquirido ou produzido no referido período."


def test_relacoes_info_documento_pendente_geracao(jwt_authenticated_client_a, periodo, conta_associacao, rateio_despesa_demonstrativo):
    url = f"/api/relacao-bens/relacao-bens-info/?conta-associacao={conta_associacao.uuid}&periodo={periodo.uuid}"
    response = jwt_authenticated_client_a.get(url)
    result = response.json()

    assert result == "Documento pendente de geração"
