from unittest.mock import patch, MagicMock

from sme_ptrf_apps.paa.services.ata_paa_dados_service import calcular_numeros_blocos, gerar_dados_ata_paa


def test_calcular_numeros_blocos_com_todos_blocos():
    prioridades = [
        {'titulo': 'Prioridades PTRF', 'items': [{'id': 1}]},
        {'titulo': 'Prioridades PDDE', 'items': [{'id': 2}]},
        {'titulo': 'Prioridades Recursos próprios', 'items': [{'id': 3}]},
    ]
    atividades_estatutarias = [{'id': 1}]
    
    resultado = calcular_numeros_blocos(prioridades, atividades_estatutarias)
    
    assert resultado['ptrf'] == 3
    assert resultado['pdde'] == 4
    assert resultado['recursos_proprios'] == 5
    assert resultado['atividades_estatutarias'] == 6
    assert resultado['manifestacoes'] == 7
    assert resultado['lista_presenca'] == 8


def test_calcular_numeros_blocos_sem_ptrf():
    prioridades = [
        {'titulo': 'Prioridades PDDE', 'items': [{'id': 1}]},
    ]
    atividades_estatutarias = []
    
    resultado = calcular_numeros_blocos(prioridades, atividades_estatutarias)
    
    assert 'ptrf' not in resultado
    assert resultado['pdde'] == 3
    assert resultado['manifestacoes'] == 4
    assert resultado['lista_presenca'] == 5


def test_calcular_numeros_blocos_sem_prioridades():
    prioridades = []
    atividades_estatutarias = [{'id': 1}]
    
    resultado = calcular_numeros_blocos(prioridades, atividades_estatutarias)
    
    assert 'ptrf' not in resultado
    assert 'pdde' not in resultado
    assert 'recursos_proprios' not in resultado
    assert resultado['atividades_estatutarias'] == 3
    assert resultado['manifestacoes'] == 4
    assert resultado['lista_presenca'] == 5


def test_calcular_numeros_blocos_prioridades_vazias():
    prioridades = [
        {'titulo': 'Prioridades PTRF', 'items': []},
        {'titulo': 'Prioridades PDDE', 'items': []},
    ]
    atividades_estatutarias = []
    
    resultado = calcular_numeros_blocos(prioridades, atividades_estatutarias)
    
    assert 'ptrf' not in resultado
    assert 'pdde' not in resultado
    assert resultado['manifestacoes'] == 3
    assert resultado['lista_presenca'] == 4


def test_calcular_numeros_blocos_apenas_fixos():
    prioridades = []
    atividades_estatutarias = []
    
    resultado = calcular_numeros_blocos(prioridades, atividades_estatutarias)
    
    assert resultado['manifestacoes'] == 3
    assert resultado['lista_presenca'] == 4


@patch("sme_ptrf_apps.paa.services.ata_paa_dados_service.dados_texto_ata_paa", autospec=True)
@patch("sme_ptrf_apps.paa.services.ata_paa_dados_service.criar_atividades_estatutarias", autospec=True)
@patch("sme_ptrf_apps.paa.services.ata_paa_dados_service.criar_grupos_prioridades", autospec=True)
@patch("sme_ptrf_apps.paa.services.ata_paa_dados_service.presentes_ata_paa", autospec=True)
@patch("sme_ptrf_apps.paa.services.ata_paa_dados_service.criar_identificacao_associacao_ata", autospec=True)
@patch("sme_ptrf_apps.paa.services.ata_paa_dados_service.cria_cabecalho", autospec=True)
def test_gerar_dados_ata_paa_inclui_numeros_blocos(
    mock_cabecalho,
    mock_identificacao,
    mock_presentes,
    mock_grupos,
    mock_atividades,
    mock_dados_texto
):
    ata_paa = MagicMock()
    usuario = MagicMock()
    
    mock_cabecalho.return_value = {"titulo": "Teste"}
    mock_identificacao.return_value = {"nome": "Teste"}
    mock_presentes.return_value = {"presentes": []}
    mock_grupos.return_value = [{'titulo': 'Prioridades PTRF', 'items': [{'id': 1}]}]
    mock_atividades.return_value = [{'id': 1}]
    mock_dados_texto.return_value = {"texto": "Teste"}
    
    resultado = gerar_dados_ata_paa(ata_paa, usuario)
    
    assert 'numeros_blocos' in resultado
    assert resultado['numeros_blocos']['ptrf'] == 3
    assert resultado['numeros_blocos']['manifestacoes'] == 5

