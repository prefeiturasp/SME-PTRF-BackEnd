import pytest

from rest_framework import status

from sme_ptrf_apps.core.models import Arquivo

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
def test_processar_arquivo_associacoes(jwt_authenticated_client_a, arquivo_carga_associacao, arquivo):
    assert Arquivo.objects.get(uuid=arquivo_carga_associacao.uuid).status == 'PENDENTE'
    response = jwt_authenticated_client_a.post(
                f'/api/arquivos/{arquivo_carga_associacao.uuid}/processar/')
    assert response.status_code == status.HTTP_200_OK
    import time
    time.sleep(5)  # Aguardar a task rodar.
    assert Arquivo.objects.get(uuid=arquivo_carga_associacao.uuid).status == 'SUCESSO'
