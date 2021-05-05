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
    time.sleep(10)  # Aguardar a task rodar.
    assert Arquivo.objects.get(uuid=arquivo_carga_associacao.uuid).status == 'SUCESSO'


@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
def test_processar_arquivo_associacoes_erro_estrutura(jwt_authenticated_client_a, arquivo_carga_associacao_com_erro_estrutura, arquivo):

    assert Arquivo.objects.get(uuid=arquivo_carga_associacao_com_erro_estrutura.uuid).status == 'PENDENTE'
    response = jwt_authenticated_client_a.post(
                f'/api/arquivos/{arquivo_carga_associacao_com_erro_estrutura.uuid}/processar/')
    assert response.status_code == status.HTTP_200_OK
    import time
    time.sleep(5)  # Aguardar a task rodar.
    arquivo = Arquivo.objects.get(uuid=arquivo_carga_associacao_com_erro_estrutura.uuid)
    assert arquivo.status == 'ERRO'
    assert arquivo.log == ('\nLinha:0 Título da coluna 1 errado. Encontrado "Código EOL DRE". Deveria ser "Nome da associacao". '
                           'Confira o arquivo com o modelo.'
                           '\n0 linha(s) importada(s) com sucesso. 1 erro(s) reportado(s).')
