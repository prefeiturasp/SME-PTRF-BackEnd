import pytest

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate

from ...api.views.motivos_pagamento_antecipado_viewset import MotivosPagamentoAntecipadoViewSet
from ...models.motivo_pagamento_antecipado import MotivoPagamentoAntecipado
pytestmark = pytest.mark.django_db


def test_view_set(motivo_pagamento_adiantado_01, usuario_permissao_despesa):
    request = APIRequestFactory().get("")
    detalhe = MotivosPagamentoAntecipadoViewSet.as_view({"get": "retrieve"})
    force_authenticate(request, user=usuario_permissao_despesa)
    response = detalhe(request, uuid=motivo_pagamento_adiantado_01.uuid)

    assert response.status_code == status.HTTP_200_OK


def test_filtra_motivo_pagamento_antecipado_por_nome(jwt_authenticated_client, motivo_pagamento_antecipado):
    url = "/api/motivos-pagamento-antecipado/?motivo=MotivoT"
    response = jwt_authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['motivo'] == "MotivoTeste"


@pytest.mark.django_db
def test_excluir_motivo_pagamento_antecipado_sem_despesa(jwt_authenticated_client, motivo_pagamento_antecipado):
    url = f"/api/motivos-pagamento-antecipado/{motivo_pagamento_antecipado.uuid}/"
    response = jwt_authenticated_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_excluir_motivo_pagamento_antecipado_com_despesa(jwt_authenticated_client,
                                                         despesa_com_motivo_pgto_antecipado,
                                                         motivo_pagamento_antecipado):

    url = f"/api/motivos-pagamento-antecipado/{motivo_pagamento_antecipado.uuid}/"
    response = jwt_authenticated_client.delete(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'ProtectedError'
    assert response.data['mensagem'] == (
        'Essa operação não pode ser realizada. Há lançamentos cadastrados com esse motivo de pagamento antecipado.'
    )
    assert MotivoPagamentoAntecipado.objects.filter(uuid=motivo_pagamento_antecipado.uuid).exists()
