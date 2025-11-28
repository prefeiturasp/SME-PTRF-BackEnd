from unittest.mock import patch, MagicMock

from sme_ptrf_apps.paa.services.dados_documento_paa_service import gerar_dados_documento_paa


@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.cria_presidente_diretoria_executiva", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_receitas_previstas_pdde", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_receitas_previstas", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_recursos_proprios", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_atividades_estatutarias", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_grupos_prioridades", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.cria_data_geracao_documento", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.criar_identificacao_associacao", autospec=True)
@patch("sme_ptrf_apps.paa.services.dados_documento_paa_service.cria_cabecalho", autospec=True)
def test_gerar_dados_documento_paa(
    mock_cabecalho,
    mock_identificacao,
    mock_data,
    mock_grupos,
    mock_atividades,
    mock_recursos,
    mock_receitas,
    mock_receitas_pdde,
    mock_presidente
):
    paa = MagicMock()
    usuario = MagicMock()

    mock_cabecalho.return_value = "CAB"
    mock_identificacao.return_value = "ASSOC"
    mock_data.return_value = "DATA"
    mock_grupos.return_value = "GRUPOS"
    mock_atividades.return_value = "ATIV"
    mock_recursos.return_value = "REC"
    mock_receitas.return_value = "REC_PREV"
    mock_receitas_pdde.return_value = "REC_PDDE"
    mock_presidente.return_value = "PRES"

    paa.objetivos.all.return_value = ["OBJ1", "OBJ2"]
    paa.texto_introducao = "INTRO"
    paa.texto_conclusao = "CONC"

    result = gerar_dados_documento_paa(paa, usuario, previa=True)

    mock_cabecalho.assert_called_once_with(paa.periodo_paa)
    mock_identificacao.assert_called_once_with(paa)
    mock_data.assert_called_once_with(usuario, True)
    mock_grupos.assert_called_once_with(paa)
    mock_atividades.assert_called_once_with(paa)
    mock_recursos.assert_called_once_with(paa)
    mock_receitas.assert_called_once_with(paa)
    mock_receitas_pdde.assert_called_once_with(paa)
    mock_presidente.assert_called_once_with(paa.associacao)

    assert result == {
        "cabecalho": "CAB",
        "identificacao_associacao": "ASSOC",
        "data_geracao_documento": "DATA",
        "texto_introducao": "INTRO",
        "objetivos": ["OBJ1", "OBJ2"],
        "grupos_prioridades": "GRUPOS",
        "receitas_previstas": "REC_PREV",
        "receitas_previstas_pdde": "REC_PDDE",
        "atividades_estatutarias": "ATIV",
        "recursos_proprios": "REC",
        "texto_conclusao": "CONC",
        "presidente_diretoria_executiva": "PRES",
        "previa": True,
    }
