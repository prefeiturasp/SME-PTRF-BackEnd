import pytest
from sme_ptrf_apps.core.services.ata_service import validar_campos_ata


@pytest.mark.django_db(transaction=False)
def test_validar_campos_ata_completa(ata_2022_2_teste_valido, presente_ata_membro_arnaldo, presente_ata_membro_falcao):
    result = validar_campos_ata(ata_2022_2_teste_valido)
    expected_result = {'is_valid': True}
    assert result == expected_result

@pytest.mark.django_db(transaction=False)
def test_validar_campos_invalidos(ata_2022_test_campos_invalidos, presente_ata_membro_arnaldo, presente_ata_membro_falcao):
    ata_2022_test_campos_invalidos.justificativa_repasses_pendentes = ''
    ata_2022_test_campos_invalidos.data_reuniao = ''
    result = validar_campos_ata(ata_2022_test_campos_invalidos)
    expected_result = {
        'is_valid': False,
        'campos': [
            'Cargo Presidente',
            'Cargo Secretário',
            'Data',
            'Local da reunião',
            'Presidente da reunião',
            'Secretário da reunião'
        ]}
    assert result == expected_result


@pytest.mark.django_db(transaction=False)
def test_validar_campos_ata_sem_presidente_e_secretario(ata_2020_1_teste):
    result = validar_campos_ata(ata_2020_1_teste)
    expected_result = {
        'is_valid': False,
        'campos': [{'msg_presente': 'informe um presidente presente, informe um secretário presente'}]
        }
    assert result == expected_result
