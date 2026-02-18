import pytest
from datetime import date
from decimal import Decimal
from model_bakery import baker
from django.http import HttpResponse
from unittest.mock import patch, MagicMock

from sme_ptrf_apps.paa.services.paa_service import PaaService
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models import PrioridadePaa


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


@pytest.mark.django_db
class TestPodeElaborarNovoPaa:
    """Testes para o método pode_elaborar_novo_paa"""

    def test_pode_elaborar_novo_paa_mes_permitido(self):
        """Testa quando mês atual é maior ou igual ao mês de elaboração"""
        baker.make(
            'ParametroPaa',
            mes_elaboracao_paa=3
        )

        with patch('sme_ptrf_apps.paa.services.paa_service.date') as mock_date:
            mock_date.today.return_value = date(2024, 4, 15)  # Abril

            # Não deve lançar exceção
            PaaService.pode_elaborar_novo_paa()

    def test_pode_elaborar_novo_paa_mes_exato(self):
        """Testa quando mês atual é exatamente o mês de elaboração"""
        baker.make(
            'ParametroPaa',
            mes_elaboracao_paa=5
        )

        with patch('sme_ptrf_apps.paa.services.paa_service.date') as mock_date:
            mock_date.today.return_value = date(2024, 5, 15)  # Maio

            # Não deve lançar exceção
            PaaService.pode_elaborar_novo_paa()

    def test_pode_elaborar_novo_paa_mes_nao_permitido(self):
        """Testa quando mês atual é menor que o mês de elaboração"""
        baker.make(
            'ParametroPaa',
            mes_elaboracao_paa=6
        )

        with patch('sme_ptrf_apps.paa.services.paa_service.date') as mock_date:
            mock_date.today.return_value = date(2024, 3, 15)  # Março

            with pytest.raises(AssertionError) as exc_info:
                PaaService.pode_elaborar_novo_paa()

            assert "Mês não liberado para Elaboração de novo PAA" in str(exc_info.value)

    def test_pode_elaborar_novo_paa_sem_parametro_mes(self):
        """Testa quando não há parâmetro de mês definido"""
        baker.make(
            'ParametroPaa',
            mes_elaboracao_paa=None
        )

        with pytest.raises(AssertionError) as exc_info:
            PaaService.pode_elaborar_novo_paa()

        assert "Nenhum parâmetro de mês para Elaboração de Novo PAA foi definido" in str(exc_info.value)


@pytest.mark.django_db
class TestGerarArquivoPdfLevantamentoPrioridades:
    """Testes para o método gerar_arquivo_pdf_levantamento_prioridades_paa"""

    @patch('sme_ptrf_apps.paa.services.paa_service.HTML')
    @patch('sme_ptrf_apps.paa.services.paa_service.CSS')
    @patch('sme_ptrf_apps.paa.services.paa_service.get_template')
    @patch('sme_ptrf_apps.paa.services.paa_service.staticfiles_storage')
    def test_gerar_pdf_retorna_http_response(
        self,
        mock_storage,
        mock_get_template,
        mock_css,
        mock_html
    ):
        """Testa se retorna HttpResponse"""
        mock_storage.location = '/fake/static'
        mock_template = MagicMock()
        mock_template.render.return_value = '<html></html>'
        mock_get_template.return_value = mock_template

        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b'PDF_CONTENT'
        mock_html.return_value = mock_html_instance

        dados = {'teste': 'dados'}
        response = PaaService.gerar_arquivo_pdf_levantamento_prioridades_paa(dados)

        assert isinstance(response, HttpResponse)
        assert response['Content-Type'] == 'application/pdf'


@pytest.mark.django_db
class TestSomatorioTotaisPorProgramaPdde:
    """Testes para o método somatorio_totais_por_programa_pdde"""

    def test_somatorio_estrutura_retorno(self, paa):
        """Testa estrutura do retorno"""
        resultado = PaaService.somatorio_totais_por_programa_pdde(str(paa.uuid))

        assert isinstance(resultado, dict)
        assert 'programas' in resultado
        assert 'total' in resultado
        assert isinstance(resultado['programas'], list)
        assert isinstance(resultado['total'], dict)

    def test_somatorio_sem_programas(self, paa):
        """Testa quando não há programas PDDE"""
        resultado = PaaService.somatorio_totais_por_programa_pdde(str(paa.uuid))

        assert resultado['programas'] == []
        assert resultado['total']['total_valor_custeio'] == 0
        assert resultado['total']['total_valor_capital'] == 0
        assert resultado['total']['total_valor_livre_aplicacao'] == 0
        assert resultado['total']['total'] == 0

    def test_somatorio_com_receitas_previstas(self, paa):
        """Testa com receitas previstas"""
        programa = baker.make('ProgramaPdde', nome='PDDE Estrutura')
        acao_pdde = baker.make('AcaoPdde', programa=programa)

        baker.make(
            'ReceitaPrevistaPdde',
            paa=paa,
            acao_pdde=acao_pdde,
            saldo_custeio=Decimal('100'),
            previsao_valor_custeio=Decimal('200'),
            saldo_capital=Decimal('50'),
            previsao_valor_capital=Decimal('150'),
            saldo_livre=Decimal('30'),
            previsao_valor_livre=Decimal('70')
        )

        resultado = PaaService.somatorio_totais_por_programa_pdde(str(paa.uuid))

        programa_resultado = resultado['programas'][0]
        assert programa_resultado['total_valor_custeio'] == Decimal('300')  # 100 + 200
        assert programa_resultado['total_valor_capital'] == Decimal('200')  # 50 + 150
        assert programa_resultado['total_valor_livre_aplicacao'] == Decimal('100')  # 30 + 70
        assert programa_resultado['total'] == Decimal('600')

    def test_somatorio_totais_gerais(self, paa):
        """Testa cálculo dos totais gerais"""
        programa = baker.make('ProgramaPdde', nome='PDDE Total')
        acao = baker.make('AcaoPdde', programa=programa)

        baker.make(
            'ReceitaPrevistaPdde',
            paa=paa,
            acao_pdde=acao,
            saldo_custeio=Decimal('500'),
            previsao_valor_custeio=Decimal('500'),
            saldo_capital=Decimal('300'),
            previsao_valor_capital=Decimal('200'),
            saldo_livre=Decimal('100'),
            previsao_valor_livre=Decimal('100')
        )

        resultado = PaaService.somatorio_totais_por_programa_pdde(str(paa.uuid))

        assert resultado['total']['total_valor_custeio'] == Decimal('1000')
        assert resultado['total']['total_valor_capital'] == Decimal('500')
        assert resultado['total']['total_valor_livre_aplicacao'] == Decimal('200')
        assert resultado['total']['total'] == Decimal('1700')


@pytest.fixture
def paa_anterior(associacao, periodo_paa):
    """Fixture para PAA anterior"""
    periodo_anterior = baker.make(
        'PeriodoPaa',
        referencia='2023',
        data_inicial=date(2023, 1, 1),
        data_final=date(2023, 12, 31)
    )
    return baker.make(
        'Paa',
        associacao=associacao,
        periodo_paa=periodo_anterior
    )


@pytest.fixture
def paa_atual(associacao, periodo_paa):
    """Fixture para PAA atual"""
    return baker.make(
        'Paa',
        associacao=associacao,
        periodo_paa=periodo_paa
    )


@pytest.fixture
def acao_associacao_ativa(associacao, acao):
    """Fixture para AcaoAssociacao ativa"""
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao,
        status='ATIVA'
    )


@pytest.fixture
def tipo_despesa_custeio():
    """Fixture para TipoCusteio ativa"""
    return baker.make(
        'TipoCusteio',
    )


@pytest.fixture
def especificacao_material():
    """Fixture para EspecificacaoMaterial ativa"""
    return baker.make(
        'EspecificacaoMaterialServico',
    )


@pytest.mark.django_db
class TestImportarPrioridadesPaaAnterior:
    """Testes para o método importar_prioridades_paa_anterior"""

    def test_importar_sem_prioridades_lanca_excecao(
        self,
        paa_atual,
        paa_anterior
    ):
        """Testa erro quando não há prioridades para importar"""
        with pytest.raises(Exception) as exc_info:
            PaaService.importar_prioridades_paa_anterior(paa_atual, paa_anterior)

        assert "Nenhuma prioridade encontrada para importação" in str(exc_info.value)

    def test_importar_prioridades_sucesso(
        self,
        paa_atual,
        paa_anterior,
        acao_associacao_ativa,
        tipo_despesa_custeio,
        especificacao_material
    ):
        """Testa importação bem-sucedida de prioridades"""
        baker.make(
            'PrioridadePaa',
            paa=paa_anterior,
            prioridade=True,
            acao_associacao=acao_associacao_ativa,
            tipo_aplicacao='CUSTEIO',
            tipo_despesa_custeio=tipo_despesa_custeio,
            especificacao_material=especificacao_material,
            valor_total=Decimal('1000')
        )

        resultado = PaaService.importar_prioridades_paa_anterior(paa_atual, paa_anterior)

        assert len(resultado) == 1
        assert PrioridadePaa.objects.filter(paa=paa_atual).count() == 1

    def test_importar_prioridades_nao_importa_nao_prioridades(
        self,
        paa_atual,
        paa_anterior,
        acao_associacao_ativa
    ):
        """Testa que não importa itens com prioridade=False"""
        baker.make(
            'PrioridadePaa',
            paa=paa_anterior,
            prioridade=False,  # Não é prioridade
            acao_associacao=acao_associacao_ativa
        )

        with pytest.raises(Exception) as exc_info:
            PaaService.importar_prioridades_paa_anterior(paa_atual, paa_anterior)

        assert "Nenhuma prioridade encontrada" in str(exc_info.value)

    def test_importar_prioridades_zera_valor_total(
        self,
        paa_atual,
        paa_anterior,
        acao_associacao_ativa,
        tipo_despesa_custeio,
        especificacao_material
    ):
        """Testa que valor_total é zerado na importação"""
        baker.make(
            'PrioridadePaa',
            paa=paa_anterior,
            prioridade=True,
            acao_associacao=acao_associacao_ativa,
            tipo_aplicacao='CUSTEIO',
            tipo_despesa_custeio=tipo_despesa_custeio,
            especificacao_material=especificacao_material,
            valor_total=Decimal('5000')
        )

        PaaService.importar_prioridades_paa_anterior(paa_atual, paa_anterior)

        prioridade_importada = PrioridadePaa.objects.get(paa=paa_atual)
        assert prioridade_importada.valor_total is None


@pytest.mark.django_db
class TestPodeGerarDocumentoFinal:
    """Testes para o método pode_gerar_documento_final"""

    def test_pode_gerar_documento_ja_gerado(self, paa):
        """Testa quando documento final já foi gerado"""
        baker.make(
            'DocumentoPaa',
            paa=paa,
            status_geracao='CONCLUIDO'
        )

        erros = PaaService.pode_gerar_documento_final(paa)

        assert len(erros) == 1
        assert "O documento final já foi gerado" in erros[0]

    def test_pode_gerar_prioridades_incompletas(
        self,
        paa,
        acao_associacao_ativa,
        especificacao_material
    ):
        """Testa erro quando há prioridades sem valor total"""
        baker.make(
            'PrioridadePaa',
            paa=paa,
            acao_associacao=acao_associacao_ativa,
            especificacao_material=especificacao_material,
            valor_total=None  # Incompleta
        )

        paa.texto_introducao = '<p>Introdução</p>'
        paa.texto_conclusao = '<p>Conclusão</p>'
        paa.save()

        baker.make('ObjetivoPaa', paa=paa)

        erros = PaaService.pode_gerar_documento_final(paa)

        assert "Prioridades sem ação e/ou valor total." in erros

    def test_pode_gerar_texto_introducao_vazio(self, paa):
        """Testa erro quando texto de introdução está vazio (apenas tags HTML)"""
        paa.texto_introducao = '<p></p>'
        paa.texto_conclusao = '<p>Conclusão</p>'
        paa.save()

        baker.make('ObjetivoPaa', paa=paa)

        erros = PaaService.pode_gerar_documento_final(paa)

        assert "É necessário inserir o texto de introdução" in erros

    def test_pode_gerar_texto_introducao_apenas_espacos(self, paa):
        """Testa erro quando texto de introdução tem apenas espaços"""
        paa.texto_introducao = '<p>&nbsp;&nbsp;</p>'
        paa.texto_conclusao = '<p>Conclusão</p>'
        paa.save()

        baker.make('ObjetivoPaa', paa=paa)

        erros = PaaService.pode_gerar_documento_final(paa)

        assert "É necessário inserir o texto de introdução" in erros

    def test_pode_gerar_sem_objetivos(self, paa):
        """Testa erro quando não há objetivos"""
        paa.texto_introducao = '<p>Introdução</p>'
        paa.texto_conclusao = '<p>Conclusão</p>'
        paa.save()

        erros = PaaService.pode_gerar_documento_final(paa)

        assert "É necessário indicar pelo menos um objetivo no PAA" in erros

    def test_pode_gerar_sem_texto_conclusao(self, paa):
        """Testa erro quando não há texto de conclusão"""
        paa.texto_introducao = '<p>Introdução</p>'
        paa.texto_conclusao = None
        paa.save()

        baker.make('ObjetivoPaa', paa=paa)

        erros = PaaService.pode_gerar_documento_final(paa)

        assert "É necessário inserir o texto de conclusão" in erros

    def test_pode_gerar_sucesso(
        self,
        paa,
        acao_associacao_ativa,
        especificacao_material,
        tipo_despesa_custeio
    ):
        """Testa quando pode gerar documento (sem erros)"""
        paa.texto_introducao = '<p>Este é o texto de introdução.</p>'
        paa.texto_conclusao = '<p>Este é o texto de conclusão.</p>'
        paa.save()

        objetivo = baker.make('ObjetivoPaa', paa=paa, nome='Objetivo 1', status=True)
        paa.objetivos.set([objetivo])

        baker.make(
            'PrioridadePaa',
            paa=paa,
            prioridade=True,
            recurso='PTRF',
            acao_associacao=acao_associacao_ativa,
            tipo_aplicacao='CUSTEIO',
            tipo_despesa_custeio=tipo_despesa_custeio,
            especificacao_material=especificacao_material,
            valor_total=Decimal('1000')
        )

        erros = PaaService.pode_gerar_documento_final(paa)

        assert erros == []
