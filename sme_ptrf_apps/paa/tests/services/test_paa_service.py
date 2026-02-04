import pytest
from unittest.mock import patch

from sme_ptrf_apps.paa.services.paa_service import PaaService
from sme_ptrf_apps.paa.enums import PaaStatusEnum


@pytest.mark.django_db
@patch('sme_ptrf_apps.paa.services.paa_service.SaldosPorAcaoPaaService.congelar_saldos')
@patch('sme_ptrf_apps.paa.services.paa_service.RegistrarAcoesOutrosRecursosConclusaoPaaService.registrar')
@patch('sme_ptrf_apps.paa.services.paa_service.RegistrarAcoesPddeConclusaoPaaService.registrar')
@patch('sme_ptrf_apps.paa.services.paa_service.RegistrarAcoesPtrfConclusaoPaaService.registrar')
def test_concluir_paa_atualiza_status_e_registra_acoes(
    mock_registrar_ptrf,
    mock_registrar_pdde,
    mock_registrar_outros_recursos,
    mock_congelar_saldos,
    paa_factory,
    periodo_paa_1
):
    """Testa que concluir_paa atualiza status para GERADO, registra ações e congela saldo"""
    paa = paa_factory.create(periodo_paa=periodo_paa_1, status=PaaStatusEnum.EM_ELABORACAO.name)
    
    resultado = PaaService.concluir_paa(paa)
    
    paa.refresh_from_db()
    assert paa.status == PaaStatusEnum.GERADO.name
    assert resultado == paa
    mock_registrar_ptrf.assert_called_once_with(paa)
    mock_registrar_pdde.assert_called_once_with(paa)
    mock_registrar_outros_recursos.assert_called_once_with(paa)
    mock_congelar_saldos.assert_called_once()
