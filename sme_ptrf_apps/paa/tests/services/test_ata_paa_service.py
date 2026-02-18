import pytest
from datetime import timedelta, time, date

from unittest.mock import patch
from model_bakery import baker

from sme_ptrf_apps.paa.models import AtaPaa


from sme_ptrf_apps.paa.services.ata_paa_service import (
    gerar_arquivo_ata_paa,
    unidade_precisa_professor_gremio,
    verifica_precisa_professor_gremio,
    validar_geracao_ata_paa,
)
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO

pytestmark = pytest.mark.django_db


def test_unidade_precisa_professor_gremio_com_tipo_configurado(parametros):
    """Testa se unidade_precisa_professor_gremio retorna True quando tipo está configurado"""
    parametros.tipos_unidades_professor_gremio = ['EMEF', 'EMEI']
    parametros.save()

    assert unidade_precisa_professor_gremio('EMEF') is True
    assert unidade_precisa_professor_gremio('EMEI') is True
    assert unidade_precisa_professor_gremio('CEU') is False


def test_unidade_precisa_professor_gremio_sem_configuracao(parametros):
    """Testa se unidade_precisa_professor_gremio retorna False quando não há configuração"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()

    assert unidade_precisa_professor_gremio('EMEF') is False


def test_unidade_precisa_professor_gremio_sem_parametros():
    """Testa se unidade_precisa_professor_gremio retorna False quando não há parâmetros"""
    from sme_ptrf_apps.core.models import Parametros
    Parametros.objects.all().delete()

    assert unidade_precisa_professor_gremio('EMEF') is False


def test_verifica_precisa_professor_gremio_sem_associacao(ata_paa):
    """Testa se verifica_precisa_professor_gremio retorna False quando não há associação"""
    associacao_original = ata_paa.paa.associacao
    ata_paa.paa.associacao = None
    ata_paa.paa.save()

    assert verifica_precisa_professor_gremio(ata_paa) is False

    ata_paa.paa.associacao = associacao_original
    ata_paa.paa.save()


def test_verifica_precisa_professor_gremio_sem_periodo_paa(ata_paa, parametros):
    """Testa se verifica_precisa_professor_gremio retorna False quando não há período PAA"""
    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()

    periodo_paa_original = ata_paa.paa.periodo_paa
    ata_paa.paa.periodo_paa = None
    ata_paa.paa.save()

    assert verifica_precisa_professor_gremio(ata_paa) is False

    ata_paa.paa.periodo_paa = periodo_paa_original
    ata_paa.paa.save()


def test_verifica_precisa_professor_gremio_sem_tipo_configurado(ata_paa, parametros):
    """Testa se verifica_precisa_professor_gremio retorna False quando tipo não está configurado"""
    parametros.tipos_unidades_professor_gremio = []
    parametros.save()

    assert verifica_precisa_professor_gremio(ata_paa) is False


def test_verifica_precisa_professor_gremio_com_tipo_configurado_sem_despesas(ata_paa, parametros):
    """Testa se verifica_precisa_professor_gremio retorna False quando tipo está configurado mas não há despesas"""
    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()

    assert verifica_precisa_professor_gremio(ata_paa) is False


def test_verifica_precisa_professor_gremio_com_despesas_completas_gremio_no_periodo(
    ata_paa, parametros, acao_factory, acao_associacao_factory, despesa_factory, rateio_despesa_factory
):
    """Testa se verifica_precisa_professor_gremio retorna True quando há despesas completas com
        ação grêmio no período"""
    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()

    # Cria ação "Orçamento Grêmio Estudantil"
    acao_gremio = acao_factory.create(nome='Orçamento Grêmio Estudantil')
    acao_associacao_gremio = acao_associacao_factory.create(
        associacao=ata_paa.paa.associacao,
        acao=acao_gremio,
        status='ATIVA'
    )

    # Cria despesa completa no período do PAA
    periodo_paa = ata_paa.paa.periodo_paa
    despesa = despesa_factory.create(
        associacao=ata_paa.paa.associacao,
        data_transacao=periodo_paa.data_inicial + timedelta(days=1),
        status=STATUS_COMPLETO
    )

    # Cria rateio completo com a ação do grêmio
    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=ata_paa.paa.associacao,
        acao_associacao=acao_associacao_gremio
    )

    assert verifica_precisa_professor_gremio(ata_paa) is True


def test_verifica_precisa_professor_gremio_sem_acao_gremio(ata_paa, parametros):
    """Testa se verifica_precisa_professor_gremio retorna False quando não há ação grêmio"""
    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()

    assert verifica_precisa_professor_gremio(ata_paa) is False


def test_verifica_precisa_professor_gremio_com_despesas_fora_do_periodo(
    ata_paa, parametros, acao_factory, acao_associacao_factory, despesa_factory, rateio_despesa_factory
):
    """Testa se verifica_precisa_professor_gremio retorna False quando há despesas fora do período"""
    tipo_unidade = ata_paa.paa.associacao.unidade.tipo_unidade
    parametros.tipos_unidades_professor_gremio = [tipo_unidade]
    parametros.save()

    # Cria ação "Orçamento Grêmio Estudantil"
    acao_gremio = acao_factory.create(nome='Orçamento Grêmio Estudantil')
    acao_associacao_gremio = acao_associacao_factory.create(
        associacao=ata_paa.paa.associacao,
        acao=acao_gremio,
        status='ATIVA'
    )

    # Cria despesa completa FORA do período do PAA (antes do período)
    periodo_paa = ata_paa.paa.periodo_paa
    despesa = despesa_factory.create(
        associacao=ata_paa.paa.associacao,
        data_transacao=periodo_paa.data_inicial - timedelta(days=1),
        status=STATUS_COMPLETO
    )

    # Cria rateio completo com a ação do grêmio
    rateio_despesa_factory.create(
        despesa=despesa,
        associacao=ata_paa.paa.associacao,
        acao_associacao=acao_associacao_gremio
    )

    assert verifica_precisa_professor_gremio(ata_paa) is False


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
def ata_paa_para_gerar(paa):
    """Fixture para AtaPaa pronta para gerar PDF"""
    return baker.make(
        'AtaPaa',
        paa=paa,
        arquivo_pdf=None,
        status_geracao_pdf='NAO_GERADO'
    )


@pytest.fixture
def mock_gerar_dados_ata_paa():
    """Mock da função gerar_dados_ata_paa"""
    with patch('sme_ptrf_apps.paa.services.ata_paa_service.gerar_dados_ata_paa') as mock:
        mock.return_value = {
            'cabecalho': {},
            'identificacao_associacao': {},
            'dados_da_ata': {},
            'dados_texto_da_ata': {},
            'presentes_na_ata': {},
            'prioridades': [],
            'atividades_estatutarias': [],
            'numeros_blocos': {},
        }
        yield mock


@pytest.fixture
def mock_gerar_arquivo_ata_paa_pdf():
    """Mock da função gerar_arquivo_ata_paa_pdf"""
    with patch('sme_ptrf_apps.paa.services.ata_paa_service.gerar_arquivo_ata_paa_pdf') as mock:
        yield mock


@pytest.fixture
def mock_paa_service_concluir():
    """Mock do método PaaService.concluir_paa"""
    with patch('sme_ptrf_apps.paa.services.ata_paa_service.PaaService.concluir_paa') as mock:
        yield mock


@pytest.mark.django_db
class TestGerarArquivoAtaPaa:
    """Testes para a função gerar_arquivo_ata_paa"""

    def test_gerar_arquivo_retorna_ata_paa_sucesso(
        self,
        ata_paa_para_gerar,
        usuario,
        mock_gerar_dados_ata_paa,
        mock_gerar_arquivo_ata_paa_pdf,
        mock_paa_service_concluir
    ):
        """Testa se retorna AtaPaa quando geração é bem-sucedida"""
        resultado = gerar_arquivo_ata_paa(ata_paa_para_gerar, usuario)

        assert isinstance(resultado, AtaPaa)
        assert resultado.uuid == ata_paa_para_gerar.uuid

    def test_gerar_arquivo_retorna_none_em_caso_de_erro(
        self,
        ata_paa_para_gerar,
        usuario,
        mock_gerar_dados_ata_paa,
        mock_paa_service_concluir
    ):
        """Testa se retorna None quando ocorre erro na geração"""
        with patch('sme_ptrf_apps.paa.services.ata_paa_service.gerar_arquivo_ata_paa_pdf') as mock:
            mock.side_effect = Exception('Erro na geração do PDF')

            resultado = gerar_arquivo_ata_paa(ata_paa_para_gerar, usuario)

            assert resultado is None


@pytest.fixture
def paa_com_documento_concluido(paa):
    """Fixture para PAA com documento final concluído"""
    baker.make(
        'DocumentoPaa',
        paa=paa,
        status_geracao='CONCLUIDO',
        versao='FINAL'
    )
    return paa


@pytest.fixture
def ata_paa_completa(paa_com_documento_concluido):
    """Fixture para AtaPaa completa e válida"""
    ata_paa = baker.make(
        'AtaPaa',
        paa=paa_com_documento_concluido,
        data_reuniao=date(2024, 3, 15),
        hora_reuniao=time(14, 30),
        local_reuniao='Sala de Reuniões da Escola',
    )
    participante_presidente = baker.make(
        'ParticipanteAtaPaa',
        ata_paa=ata_paa,
    )
    participante_secretario = baker.make(
        'ParticipanteAtaPaa',
        ata_paa=ata_paa,
    )
    ata_paa.presidente_da_reuniao = participante_presidente
    ata_paa.secretario_da_reuniao = participante_secretario
    ata_paa.parecer_conselho = 'APROVADA'
    return ata_paa


@pytest.fixture
def ata_paa_incompleta(paa_com_documento_concluido):
    """Fixture para AtaPaa incompleta"""
    return baker.make(
        'AtaPaa',
        paa=paa_com_documento_concluido,
    )


@pytest.fixture
def paa_com_documento_pendente(paa):
    """Fixture para PAA com documento final pendente"""
    baker.make(
        'DocumentoPaa',
        paa=paa,
        status_geracao='NAO_GERADO',
    )
    return paa


@pytest.fixture
def ata_paa_ja_gerada(paa_com_documento_concluido):
    """Fixture para AtaPaa já gerada anteriormente"""
    return baker.make(
        'AtaPaa',
        paa=paa_com_documento_concluido,
        status_geracao_pdf='CONCLUIDO'
    )


@pytest.mark.django_db
class TestValidarGeracaoAtaPaa:
    """Testes para a função validar_geracao_ata_paa"""

    def test_validacao_estrutura_retorno(self, ata_paa_completa):
        """Testa se retorna a estrutura esperada"""
        resultado = validar_geracao_ata_paa(ata_paa_completa)

        assert isinstance(resultado, dict)
        assert 'is_valid' in resultado

    def test_validacao_ata_completa_e_valida(self, ata_paa_completa):
        """Testa validação com ata completa e válida"""
        resultado = validar_geracao_ata_paa(ata_paa_completa)

        assert 'mensagem' not in resultado, resultado['mensagem']
        assert resultado['is_valid'] is True

    def test_validacao_ata_incompleta(self, ata_paa_incompleta):
        """Testa validação quando ata não está completa"""
        resultado = validar_geracao_ata_paa(ata_paa_incompleta)

        assert resultado['is_valid'] is False
        assert 'mensagem' in resultado
        assert 'Todos os dados da edição da ata devem estar preenchidos' in resultado['mensagem']

    def test_validacao_documento_nao_gerado(self, paa_com_documento_pendente):
        """Testa validação quando documento PAA não foi gerado"""
        ata_paa = baker.make(
            'AtaPaa',
            paa=paa_com_documento_pendente,
        )

        resultado = validar_geracao_ata_paa(ata_paa)

        assert resultado['is_valid'] is False
        assert 'mensagem' in resultado
        assert 'O documento Plano Anual deve estar gerado' in resultado['mensagem']

    def test_validacao_ata_ja_gerada(self, ata_paa_ja_gerada):
        """Testa validação quando ata já foi gerada anteriormente"""
        resultado = validar_geracao_ata_paa(ata_paa_ja_gerada)

        assert 'mensagem' in resultado, resultado
        assert 'A ata já foi gerada anteriormente' in resultado['mensagem']
        assert resultado['is_valid'] is False
