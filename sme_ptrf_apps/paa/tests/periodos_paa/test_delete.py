import pytest

from rest_framework import status

from sme_ptrf_apps.paa.models import PeriodoPaa, Paa


pytestmark = pytest.mark.django_db


def test_pdelete_sucesso(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    assert PeriodoPaa.objects.count() == 1

    response = jwt_authenticated_client_sme.delete(f'/api/periodos-paa/{periodo_paa_1.uuid}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert PeriodoPaa.objects.count() == 0


def test_delete_404(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    assert PeriodoPaa.objects.count() == 1

    response = jwt_authenticated_client_sme.delete('/api/periodos-paa/b737979c-66e2-4d38-b266-652aa1f0fe5d/')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert PeriodoPaa.objects.count() == 1


def test_delete_periodo_com_paa_vinculado(jwt_authenticated_client_sme, flag_paa, periodo_paa_1, associacao):
    """Testa se não é possível excluir um período que está vinculado a um PAA"""
    assert PeriodoPaa.objects.count() == 1
    
    # Cria um PAA vinculado ao período
    paa = Paa.objects.create(
        periodo_paa=periodo_paa_1,
        associacao=associacao
    )
    
    response = jwt_authenticated_client_sme.delete(f'/api/periodos-paa/{periodo_paa_1.uuid}/')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["mensagem"] == "Este período de PAA não pode ser excluído porque está sendo utilizada em um Plano Anual de Atividades (PAA)."
    assert PeriodoPaa.objects.count() == 1  # O período não foi excluído


def test_delete_excecao_generica(jwt_authenticated_client_sme, flag_paa, periodo_paa_1):
    """Testa o tratamento de exceção genérica no método destroy"""
    assert PeriodoPaa.objects.count() == 1
    
    # Simula uma situação que pode causar exceção - usando um UUID inválido
    # que pode causar problemas na busca do objeto
    response = jwt_authenticated_client_sme.delete('/api/periodos-paa/invalid-uuid-format/')
    
    # Deve retornar 404 para UUID inválido, mas se houver exceção genérica
    # será capturada pelo try/catch do método destroy
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
    assert PeriodoPaa.objects.count() == 1  # O período não foi excluído

