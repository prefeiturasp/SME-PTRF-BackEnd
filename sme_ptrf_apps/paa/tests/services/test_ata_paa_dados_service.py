import pytest
from datetime import date, time, datetime
from model_bakery import baker
from sme_ptrf_apps.paa.services.ata_paa_dados_service import (
    presentes_ata_paa,
    dados_texto_ata_paa,
    cria_cabecalho,
    formata_data,
    formatar_hora_ata,
    criar_identificacao_associacao_ata,
)

from unittest.mock import patch, MagicMock

from sme_ptrf_apps.paa.services.ata_paa_dados_service import calcular_numeros_blocos, gerar_dados_ata_paa


@pytest.fixture
def ata_paa(paa):
    """Fixture para criar uma AtaPaa"""
    return baker.make(
        'AtaPaa',
        paa=paa,
        data_reuniao=date(2024, 3, 15),
        hora_reuniao=time(14, 30),
        local_reuniao='Sala de Reuniões',
        comentarios='Comentários da reunião',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
    )


@pytest.fixture
def participante_membro_presidente(ata_paa):
    """Participante membro com cargo de presidente"""
    return baker.make(
        'ParticipanteAtaPaa',
        ata_paa=ata_paa,
        nome='João Silva',
        cargo='Presidente',
        membro=True,
        conselho_fiscal=False,
        presente=True,
        professor_gremio=False,
    )


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


@pytest.mark.django_db
class TestPresentesAtaPaa:
    """Testes para a função presentes_ata_paa"""

    def test_presentes_ata_paa_estrutura_retorno(
        self,
        ata_paa,
        participante_membro_presidente
    ):
        """Testa se a função retorna a estrutura esperada"""
        resultado = presentes_ata_paa(ata_paa)

        assert isinstance(resultado, dict)
        assert 'presentes_ata_membros' in resultado
        assert 'presentes_ata_nao_membros' in resultado
        assert isinstance(resultado['presentes_ata_membros'], list)
        assert isinstance(resultado['presentes_ata_nao_membros'], list)


@pytest.fixture
def usuario():
    """Fixture para criar um usuário"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='usuario.teste',
        email='usuario@teste.com'
    )


@pytest.fixture
def ata_paa_completa(paa):
    """Fixture para AtaPaa com todos os campos preenchidos"""
    return baker.make(
        'AtaPaa',
        paa=paa,
        data_reuniao=date(2024, 3, 15),
        hora_reuniao=time(14, 30),
        local_reuniao='Sala de Reuniões da Escola',
        comentarios='Comentários importantes da reunião',
        parecer_conselho='APROVADO',
        justificativa='Justificativa para aprovação',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
    )


@pytest.mark.django_db
class TestDadosTextoAtaPaa:
    """Testes para a função dados_texto_ata_paa"""

    def test_dados_texto_ata_paa_estrutura_retorno(self, ata_paa_completa, usuario):
        """Testa se a função retorna a estrutura esperada"""
        resultado = dados_texto_ata_paa(ata_paa_completa, usuario)

        assert isinstance(resultado, dict)

        # Verifica se todas as chaves esperadas estão presentes
        chaves_esperadas = [
            'associacao_nome',
            'unidade_cod_eol',
            'unidade_tipo',
            'unidade_nome',
            'local_reuniao',
            'periodo_referencia',
            'presidente_reuniao',
            'cargo_presidente_reuniao',
            'secretario_reuniao',
            'cargo_secretaria_reuniao',
            'data_reuniao_por_extenso',
            'data_reuniao',
            'comentarios',
            'parecer_conselho',
            'justificativa',
            'usuario',
            'hora_reuniao',
            'hora_reuniao_formatada',
            'tipo_reuniao',
            'convocacao',
        ]

        for chave in chaves_esperadas:
            assert chave in resultado


@pytest.fixture
def periodo_paa_completo():
    """Fixture para PeriodoPaa com todos os campos"""
    return baker.make(
        'PeriodoPaa',
        referencia='2024',
        data_inicial=date(2024, 1, 1),
        data_final=date(2024, 12, 31)
    )


@pytest.fixture
def paa_com_periodo_completo(associacao, periodo_paa_completo):
    """Fixture para PAA com período completo"""
    return baker.make(
        'Paa',
        associacao=associacao,
        periodo_paa=periodo_paa_completo
    )


@pytest.fixture
def ata_paa_periodo_completo(paa_com_periodo_completo):
    """Fixture para AtaPaa com período completo"""
    return baker.make(
        'AtaPaa',
        paa=paa_com_periodo_completo
    )


@pytest.mark.django_db
class TestCriaCabecalho:
    """Testes para a função cria_cabecalho"""

    def test_cria_cabecalho_estrutura_retorno(self, ata_paa_periodo_completo):
        """Testa se retorna a estrutura esperada"""
        resultado = cria_cabecalho(ata_paa_periodo_completo)

        assert isinstance(resultado, dict)
        assert 'titulo' in resultado
        assert 'subtitulo' in resultado
        assert 'periodo_referencia' in resultado
        assert 'periodo_data_inicio' in resultado
        assert 'periodo_data_fim' in resultado
        assert len(resultado) == 5


class TestFormataData:
    """Testes para a função formata_data"""

    def test_formata_data_objeto_date(self):
        """Testa formatação com objeto date"""
        data = date(2024, 3, 15)
        resultado = formata_data(data)

        assert resultado == '15/03/2024'

    def test_formata_data_objeto_datetime(self):
        """Testa formatação com objeto datetime"""
        data = datetime(2024, 12, 31, 14, 30, 0)
        resultado = formata_data(data)

        assert resultado == '31/12/2024'

    def test_formata_data_string_valida(self):
        """Testa formatação com string no formato YYYY-MM-DD"""
        data = '2024-06-20'
        resultado = formata_data(data)

        assert resultado == '20/06/2024'

    def test_formata_data_string_invalida(self):
        """Testa tratamento de string em formato inválido"""
        data = 'data-invalida'
        resultado = formata_data(data)

        assert resultado == '___'

    def test_formata_data_string_formato_errado(self):
        """Testa string com formato diferente"""
        data = '15/03/2024'
        resultado = formata_data(data)

        assert resultado == '___'

    def test_formata_data_none(self):
        """Testa tratamento quando data é None"""
        resultado = formata_data(None)

        assert resultado == '___'

    def test_formata_data_string_vazia(self):
        """Testa tratamento de string vazia"""
        resultado = formata_data('')

        assert resultado == '___'


class TestFormatarHoraAta:
    """Testes para a função formatar_hora_ata"""

    def test_formatar_hora_ata_objeto_time(self):
        """Testa formatação com objeto time"""
        hora = time(14, 30)
        resultado = formatar_hora_ata(hora)

        assert resultado == '14h30'

    def test_formatar_hora_ata_meia_noite(self):
        """Testa formatação da meia-noite"""
        hora = time(0, 0)
        resultado = formatar_hora_ata(hora)

        assert resultado == '00h00'

    def test_formatar_hora_ata_meio_dia(self):
        """Testa formatação do meio-dia"""
        hora = time(12, 0)
        resultado = formatar_hora_ata(hora)

        assert resultado == '12h00'

    def test_formatar_hora_ata_final_do_dia(self):
        """Testa formatação do final do dia"""
        hora = time(23, 59)
        resultado = formatar_hora_ata(hora)

        assert resultado == '23h59'

    def test_formatar_hora_ata_hora_matinal(self):
        """Testa formatação de hora da manhã com zero à esquerda"""
        hora = time(9, 5)
        resultado = formatar_hora_ata(hora)

        assert resultado == '09h05'

    def test_formatar_hora_ata_string_formato_hms(self):
        """Testa formatação com string no formato HH:MM:SS"""
        hora = '15:45:00'
        resultado = formatar_hora_ata(hora)

        assert resultado == '15h45'

    def test_formatar_hora_ata_string_formato_hm(self):
        """Testa formatação com string no formato HH:MM"""
        hora = '08:20'
        resultado = formatar_hora_ata(hora)

        assert resultado == '08h20'

    def test_formatar_hora_ata_string_invalida(self):
        """Testa tratamento de string em formato inválido"""
        hora = 'hora-invalida'
        resultado = formatar_hora_ata(hora)

        assert resultado == '00h00'

    def test_formatar_hora_ata_string_formato_errado(self):
        """Testa string com formato diferente"""
        hora = '14h30'
        resultado = formatar_hora_ata(hora)

        assert resultado == '00h00'

    def test_formatar_hora_ata_none(self):
        """Testa tratamento quando hora é None"""
        resultado = formatar_hora_ata(None)

        assert resultado == '00h00'

    def test_formatar_hora_ata_string_vazia(self):
        """Testa tratamento de string vazia"""
        resultado = formatar_hora_ata('')

        assert resultado == '00h00'


@pytest.fixture
def associacao_completa(unidade):
    """Fixture para associação com todos os campos preenchidos"""
    return baker.make(
        'Associacao',
        nome='Associação de Pais e Mestres',
        cnpj='12.345.678/0001-90',
        unidade=unidade
    )


@pytest.fixture
def paa_completo(associacao_completa, periodo_paa):
    """Fixture para PAA com associação completa"""
    return baker.make(
        'Paa',
        associacao=associacao_completa,
        periodo_paa=periodo_paa
    )


@pytest.mark.django_db
class TestCriarIdentificacaoAssociacaoAta:
    """Testes para a função criar_identificacao_associacao_ata"""

    def test_criar_identificacao_estrutura_retorno(self, paa_completo):
        """Testa se retorna a estrutura esperada"""
        resultado = criar_identificacao_associacao_ata(paa_completo)

        assert isinstance(resultado, dict)
        assert 'nome_associacao' in resultado
        assert 'cnpj_associacao' in resultado
        assert 'codigo_eol' in resultado
        assert 'dre' in resultado
        assert len(resultado) == 4
