from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from freezegun import freeze_time

from sme_ptrf_apps.core.services.lauda_pdf_service import (
    _montar_titulos_publicacao_lauda,
    _rodape_lauda_sem_identificacao_pessoal,
    _titulo_coluna_saldo,
    gerar_arquivo_lauda_pdf_consolidado_dre,
)


def test_titulo_coluna_saldo_com_data():
    result = _titulo_coluna_saldo("inicial", "01/01/2024")

    assert result == "Saldo reprogramado<br>inicial em 01/01/2024"


def test_titulo_coluna_saldo_sem_data():
    result = _titulo_coluna_saldo("final")

    assert result == "Saldo reprogramado<br>final"


@freeze_time("2024-03-10 14:30:00")
def test_rodape_lauda_sem_identificacao_pessoal():
    path = 'sme_ptrf_apps.core.services.lauda_pdf_service.formata_nome_dre'
    with patch(path, return_value='TESTE'):
        result = _rodape_lauda_sem_identificacao_pessoal(dre=SimpleNamespace(nome='DRE TESTE'))

    assert result == "DRE TESTE — Lauda gerada via SIG-Escola, em 10/03/2024 às 14:30:00"


def _lauda_para_titulos(eh_retificacao, consolidado_retificado=None, habilita_exibicao_de_lauda=True):
    return SimpleNamespace(
        consolidado_dre=SimpleNamespace(
            eh_retificacao=eh_retificacao,
            consolidado_retificado=consolidado_retificado,
        ),
        periodo=SimpleNamespace(
            recurso=SimpleNamespace(habilita_exibicao_de_lauda=habilita_exibicao_de_lauda),
        ),
    )


def test_montar_titulos_publicacao_lauda_parcial():
    lauda = _lauda_para_titulos(eh_retificacao=False)
    parcial = {"parcial": True, "sequencia_de_publicacao_atual": 5}

    result = _montar_titulos_publicacao_lauda(lauda, parcial)

    assert result["titulo_sequencia_publicacao"] == "Lauda referente à Publicação Parcial #5"
    assert result["titulo_retificacao"] is None
    assert result["subtitulo_retificacao"] is None


def test_montar_titulos_publicacao_lauda_final():
    lauda = _lauda_para_titulos(eh_retificacao=False)
    parcial = {"parcial": False, "sequencia_de_publicacao_atual": None}

    result = _montar_titulos_publicacao_lauda(lauda, parcial)

    assert result["titulo_sequencia_publicacao"] == "Lauda final"
    assert result["titulo_retificacao"] is None
    assert result["subtitulo_retificacao"] is None


def test_montar_titulos_publicacao_lauda_retificacao_com_sequencia():
    cons_ret = SimpleNamespace(
        sequencia_de_publicacao=7,
        pagina_publicacao='12',
        data_publicacao=date(2024, 3, 1),
    )
    lauda = _lauda_para_titulos(eh_retificacao=True, consolidado_retificado=cons_ret)
    parcial = {"parcial": False, "sequencia_de_publicacao_atual": None}

    result = _montar_titulos_publicacao_lauda(lauda, parcial)

    assert result["titulo_sequencia_publicacao"] == "Lauda referente à Parcial #7"
    assert "PÁGINA 12" in result["titulo_retificacao"]
    assert "RETIFICAÇÃO" in result["titulo_retificacao"]
    assert result["subtitulo_retificacao"] == (
        "Para a(s) associação(ões) listada(s) a seguir, leia-se como segue e não como constou:"
    )


def test_montar_titulos_publicacao_lauda_retificacao_sem_consolidado_retificado():
    lauda = _lauda_para_titulos(eh_retificacao=True, consolidado_retificado=None)
    parcial = {"parcial": False, "sequencia_de_publicacao_atual": None}

    result = _montar_titulos_publicacao_lauda(lauda, parcial)

    assert result["titulo_sequencia_publicacao"] == "Lauda referente à retificação da publicação"
    assert result["titulo_retificacao"] is None
    assert result["subtitulo_retificacao"] is None


def test_montar_titulos_publicacao_lauda_retificacao_sem_pagina():
    cons_ret = SimpleNamespace(
        sequencia_de_publicacao=None,
        pagina_publicacao=None,
        data_publicacao=None,
    )
    lauda = _lauda_para_titulos(eh_retificacao=True, consolidado_retificado=cons_ret)
    parcial = {"parcial": False, "sequencia_de_publicacao_atual": None}

    result = _montar_titulos_publicacao_lauda(lauda, parcial)

    assert result["titulo_sequencia_publicacao"] == "Lauda referente à retificação da publicação"
    assert "PÁGINA -" in result["titulo_retificacao"]
    assert result["subtitulo_retificacao"] == (
        "Para a(s) associação(ões) listada(s) a seguir, leia-se como segue e não como constou:"
    )


# gerar_arquivo_lauda_pdf_consolidado_dre

MODULE = 'sme_ptrf_apps.core.services.lauda_pdf_service'


def _make_args(**overrides):
    args = dict(
        lauda=MagicMock(),
        dre=SimpleNamespace(nome='DIRETORIA REGIONAL DE EDUCACAO TESTE'),
        periodo=SimpleNamespace(
            data_inicio_realizacao_despesas=date(2024, 1, 1),
            data_fim_realizacao_despesas=date(2024, 6, 30),
            referencia='2024.1',
        ),
        ata=SimpleNamespace(
            numero_ata='123',
            data_reuniao=date(2024, 7, 1),
            periodo=SimpleNamespace(referencia='2024.1'),
        ),
        nome_dre='dre-teste',
        parcial={"parcial": False, "sequencia_de_publicacao_atual": None},
    )
    args.update(overrides)
    return args


def test_gerar_arquivo_lauda_pdf_chama_gerar_dados_agregados():
    args = _make_args()

    with patch(f'{MODULE}.gerar_dados_lauda_agregados_por_unidade', return_value=[]) as mock_dados, \
            patch(f'{MODULE}._montar_titulos_publicacao_lauda', return_value={
                "titulo_sequencia_publicacao": "Lauda final",
                "titulo_retificacao": None,
                "subtitulo_retificacao": None,
            }), \
            patch(f'{MODULE}.get_template') as mock_get_template, \
            patch(f'{MODULE}.HTML') as mock_html, \
            patch(f'{MODULE}.CSS'), \
            patch(f'{MODULE}.staticfiles_storage') as mock_storage:
        mock_storage.location = '/fake/static'
        mock_get_template.return_value.render.return_value = '<html></html>'
        mock_html.return_value.write_pdf.return_value = b'PDF_BYTES'

        gerar_arquivo_lauda_pdf_consolidado_dre(**args)

    mock_dados.assert_called_once_with(args['dre'], args['periodo'], False, args['lauda'])


def test_gerar_arquivo_lauda_pdf_apenas_nao_publicadas():
    args = _make_args(apenas_nao_publicadas=True)

    with patch(f'{MODULE}.gerar_dados_lauda_agregados_por_unidade', return_value=[]) as mock_dados, \
            patch(f'{MODULE}._montar_titulos_publicacao_lauda', return_value={
                "titulo_sequencia_publicacao": "Lauda final",
                "titulo_retificacao": None,
                "subtitulo_retificacao": None,
            }), \
            patch(f'{MODULE}.get_template') as mock_get_template, \
            patch(f'{MODULE}.HTML') as mock_html, \
            patch(f'{MODULE}.CSS'), \
            patch(f'{MODULE}.staticfiles_storage') as mock_storage:
        mock_storage.location = '/fake/static'
        mock_get_template.return_value.render.return_value = '<html></html>'
        mock_html.return_value.write_pdf.return_value = b'PDF_BYTES'

        gerar_arquivo_lauda_pdf_consolidado_dre(**args)

    mock_dados.assert_called_once_with(args['dre'], args['periodo'], True, args['lauda'])


def test_gerar_arquivo_lauda_pdf_renderiza_template_e_contexto():
    args = _make_args()

    with patch(f'{MODULE}.gerar_dados_lauda_agregados_por_unidade', return_value=[]), \
            patch(f'{MODULE}._montar_titulos_publicacao_lauda', return_value={
                "titulo_sequencia_publicacao": "Lauda final",
                "titulo_retificacao": "RETIFICACAO",
                "subtitulo_retificacao": "SUBTITULO",
            }), \
            patch(f'{MODULE}.get_template') as mock_get_template, \
            patch(f'{MODULE}.HTML') as mock_html, \
            patch(f'{MODULE}.CSS'), \
            patch(f'{MODULE}.staticfiles_storage') as mock_storage:
        mock_storage.location = '/fake/static'
        mock_get_template.return_value.render.return_value = '<html></html>'
        mock_html.return_value.write_pdf.return_value = b'PDF_BYTES'

        gerar_arquivo_lauda_pdf_consolidado_dre(**args)

    mock_get_template.assert_called_once_with('pdf/lauda/pdf.html')

    render_kwargs = mock_get_template.return_value.render.call_args[0][0]
    assert render_kwargs['base_static_url'] == '/fake/static'

    contexto = render_kwargs['dados']
    assert contexto['titulo_retificacao'] == "RETIFICACAO"
    assert contexto['subtitulo_retificacao'] == "SUBTITULO"
    assert contexto['periodo_datas'] == "01/01/2024 a 30/06/2024"
    assert contexto['cabecalho']['periodo_referencia'] == '2024.1'
    assert contexto['cabecalho']['periodo_data_inicio'] == "01/01/2024"
    assert contexto['cabecalho']['periodo_data_fim'] == "30/06/2024"
    assert "DIRETORIA REGIONAL DE EDUCAÇÃO - TESTE" in contexto['titulo_corpo']['dre_maiusculo']


def test_gerar_arquivo_lauda_pdf_periodo_sem_datas():
    args = _make_args(periodo=SimpleNamespace(
        data_inicio_realizacao_despesas=None,
        data_fim_realizacao_despesas=None,
        referencia='',
    ))

    with patch(f'{MODULE}.gerar_dados_lauda_agregados_por_unidade', return_value=[]), \
            patch(f'{MODULE}._montar_titulos_publicacao_lauda', return_value={
                "titulo_sequencia_publicacao": "Lauda final",
                "titulo_retificacao": None,
                "subtitulo_retificacao": None,
            }), \
            patch(f'{MODULE}.get_template') as mock_get_template, \
            patch(f'{MODULE}.HTML') as mock_html, \
            patch(f'{MODULE}.CSS'), \
            patch(f'{MODULE}.staticfiles_storage') as mock_storage:
        mock_storage.location = '/fake/static'
        mock_get_template.return_value.render.return_value = '<html></html>'
        mock_html.return_value.write_pdf.return_value = b'PDF_BYTES'

        gerar_arquivo_lauda_pdf_consolidado_dre(**args)

    render_kwargs = mock_get_template.return_value.render.call_args[0][0]
    contexto = render_kwargs['dados']
    assert contexto['periodo_datas'] == ""
    assert contexto['cabecalho']['periodo_data_inicio'] == ""
    assert contexto['cabecalho']['periodo_data_fim'] == ""


def test_gerar_arquivo_lauda_pdf_gera_pdf_com_weasyprint():
    args = _make_args()

    with patch(f'{MODULE}.gerar_dados_lauda_agregados_por_unidade', return_value=[]), \
            patch(f'{MODULE}._montar_titulos_publicacao_lauda', return_value={
                "titulo_sequencia_publicacao": "Lauda final",
                "titulo_retificacao": None,
                "subtitulo_retificacao": None,
            }), \
            patch(f'{MODULE}.get_template') as mock_get_template, \
            patch(f'{MODULE}.HTML') as mock_html, \
            patch(f'{MODULE}.CSS') as mock_css, \
            patch(f'{MODULE}.staticfiles_storage') as mock_storage:
        mock_storage.location = '/fake/static'
        mock_get_template.return_value.render.return_value = '<html>conteudo</html>'
        mock_html.return_value.write_pdf.return_value = b'PDF_BYTES'

        gerar_arquivo_lauda_pdf_consolidado_dre(**args)

    mock_html.assert_called_once_with(string='<html>conteudo</html>', base_url='/fake/static')
    mock_css.assert_called_once_with('/fake/static/css/lauda-pdf.css')
    mock_html.return_value.write_pdf.assert_called_once_with(stylesheets=[mock_css.return_value])


def test_gerar_arquivo_lauda_pdf_salva_arquivo():
    args = _make_args(nome_dre='dre-sul')

    with patch(f'{MODULE}.gerar_dados_lauda_agregados_por_unidade', return_value=[]), \
            patch(f'{MODULE}._montar_titulos_publicacao_lauda', return_value={
                "titulo_sequencia_publicacao": "Lauda final",
                "titulo_retificacao": None,
                "subtitulo_retificacao": None,
            }), \
            patch(f'{MODULE}.get_template') as mock_get_template, \
            patch(f'{MODULE}.HTML') as mock_html, \
            patch(f'{MODULE}.CSS'), \
            patch(f'{MODULE}.staticfiles_storage') as mock_storage:
        mock_storage.location = '/fake/static'
        mock_get_template.return_value.render.return_value = '<html></html>'
        mock_html.return_value.write_pdf.return_value = b'PDF_BYTES'

        gerar_arquivo_lauda_pdf_consolidado_dre(**args)

    args['lauda'].arquivo_lauda_pdf.save.assert_called_once()
    call_kwargs = args['lauda'].arquivo_lauda_pdf.save.call_args.kwargs
    assert call_kwargs['name'] == 'Lauda_dre-sul.pdf'
