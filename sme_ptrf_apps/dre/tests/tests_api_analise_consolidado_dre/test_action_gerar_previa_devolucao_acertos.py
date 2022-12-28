import json

import pytest
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_gerar_previa_devolucao_acertos_sme_deve_passar(
    jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre,
    analise_consolidado_dre_01
):
    response = jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre.get(
        f'/api/analises-consolidados-dre/previa-relatorio-devolucao-acertos/?analise_consolidado_uuid={analise_consolidado_dre_01.uuid}'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result["mensagem"] == "Arquivo na fila para processamento."


def test_gerar_previa_devolucao_acertos_sme_sem_uuid_analise(
    jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre,
    analise_consolidado_dre_01
):
    response = jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre.get(
        f'/api/analises-consolidados-dre/previa-relatorio-devolucao-acertos/'
    )


    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_gerar_previa_devolucao_acertos_sme_uuid_errado(
    jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre,
    analise_consolidado_dre_01
):
    response = jwt_authenticated_client_sme_teste_analise_documento_consolidado_dre.get(
        f'/api/analises-consolidados-dre/previa-relatorio-devolucao-acertos/?analise_consolidado_uuid={analise_consolidado_dre_01.uuid}1'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


