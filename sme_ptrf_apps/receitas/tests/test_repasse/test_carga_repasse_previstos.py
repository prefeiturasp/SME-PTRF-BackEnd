import pytest
import datetime
from unittest.mock import patch
from uuid import uuid4
from decimal import Decimal

from sme_ptrf_apps.receitas.services.carga_repasses_previstos import (
    CargaRepassePrevistoException,
    associacao_periodo_tem_pc,
    carrega_repasses_previstos,
    get_acao,
    get_acao_associacao,
    get_conta_associacao,
    get_datas_periodo,
    get_id_linha,
    get_periodo,
    get_tipo_conta,
    get_valor,
    processa_repasse,
    verifica_tipo_aplicacao,
)
from sme_ptrf_apps.receitas.models import Repasse
from sme_ptrf_apps.core.models import ContaAssociacao
from django.core.files.uploadedfile import SimpleUploadedFile

from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    SUCESSO,
    PROCESSADO_COM_ERRO)

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_REPASSE_PREVISTO

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        '2020_01_01_a_2020_06_30_cheque.csv',
        bytes(
            (
                "Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n"
                "10,93238,99000.98,99000.98,,Role Cultural"
            ),
            encoding="utf-8"))


@pytest.fixture
def arquivo_deve_criar_conta():
    return SimpleUploadedFile(
        '2023_01_01_a_2023_06_30_cartao.csv',
        bytes(
            (
                "Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n"
                "10,123456,99000.98,99000.98,,PTRF Básico"
            ),
            encoding="utf-8"))


@pytest.fixture
def arquivo_processado():
    return SimpleUploadedFile(
        'carga_repasse_cheque.csv',
        bytes(
            (
                "Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n"
                "10,123456,99000.98,99000.98,,Role Cultural\n"
                "20,93238,99000.98,99000.98,,Role Cultural"
            ),
            encoding="utf-8"))


@pytest.fixture
def arquivo_associacao_encerrada():
    return SimpleUploadedFile(
        'carga_repasse_cheque_2.csv',
        bytes(
            (
                "Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n"
                "10,999999,99000.98,99000.98,,PTRF Básico"
            ),
            encoding="utf-8"))


@pytest.fixture
def periodo_teste_2(periodo_factory):
    return periodo_factory(
        referencia='2020.1',
        data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2020, 6, 30),
    )


@pytest.fixture
def tipo_conta(tipo_conta_factory):
    return tipo_conta_factory(
        nome='Cheque',
        banco_nome='Banco do Inter',
        agencia='67945',
        numero_conta='935556-x',
        numero_cartao='987644164221'
    )


@pytest.fixture
def arquivo_carga(arquivo, tipo_conta, periodo_teste_2, arquivo_factory):
    return arquivo_factory(
        identificador='2020_01_01_a_2020_06_30_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA,
        tipo_de_conta=tipo_conta,
        periodo=periodo_teste_2
    )


@pytest.fixture
def periodo_2024(periodo_factory):
    return periodo_factory(
        referencia='2024.1',
        data_inicio_realizacao_despesas=datetime.date(2024, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2024, 8, 31),
    )


@pytest.fixture
def periodo_teste_2023(periodo_factory):
    return periodo_factory(
        referencia='2023.1',
        data_inicio_realizacao_despesas=datetime.date(2023, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2023, 6, 30),
    )


@pytest.fixture
def arquivo_carga_cartao_deve_criar_conta(arquivo_deve_criar_conta,
                                          tipo_conta, periodo_teste_2023, arquivo_factory):
    return arquivo_factory(
        identificador='2023_01_01_a_2023_06_30_cartao',
        conteudo=arquivo_deve_criar_conta,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
        tipo_de_conta=tipo_conta,
        periodo=periodo_teste_2023
    )


@pytest.fixture
def periodo_teste_4(periodo_factory):
    return periodo_factory(
        referencia='2023.1',
        data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2023, 6, 30),
    )


@pytest.fixture
def arquivo_carga_virgula(arquivo, tipo_conta, periodo_teste_4, arquivo_factory):
    return arquivo_factory(
        identificador='2020_01_01_a_2020_06_30_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
        periodo=periodo_teste_4,
        tipo_de_conta=tipo_conta,
    )


@pytest.fixture
def periodo_teste_5(periodo_factory):
    return periodo_factory(
        referencia='2019.1',
        data_inicio_realizacao_despesas=datetime.date(2019, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2019, 11, 30),
    )


@pytest.fixture
def arquivo_carga_virgula_processado(arquivo_processado, periodo_teste_5, tipo_conta, arquivo_factory):
    return arquivo_factory(
        identificador='2019_01_01_a_2019_11_30_cheque',
        conteudo=arquivo_processado,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
        periodo=periodo_teste_5,
        tipo_de_conta=tipo_conta,
    )


@pytest.fixture
def periodo_teste_1(periodo_factory):
    return periodo_factory(
        referencia='2029.1',
        data_inicio_realizacao_despesas=datetime.date(2019, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2019, 11, 30),
    )


@pytest.fixture
def arquivo_carga_virgula_processado_com_associacao_encerrada(
        arquivo_associacao_encerrada, periodo_teste_1, tipo_conta, arquivo_factory):
    return arquivo_factory(
        identificador='2019_01_01_a_2019_11_30_cheque_2',
        conteudo=arquivo_associacao_encerrada,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
        periodo=periodo_teste_1,
        tipo_de_conta=tipo_conta
    )


def test_carga_com_erro_formatacao(arquivo_carga, tipo_conta_cheque):
    carrega_repasses_previstos(arquivo_carga)
    assert arquivo_carga.log == (
        'Erro ao processar repasses previstos: Formato definido '
        '(DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)')
    assert arquivo_carga.status == ERRO


def test_carga_com_erro(arquivo_carga_virgula, tipo_conta_cheque):
    carrega_repasses_previstos(arquivo_carga_virgula)
    msg = (
        "Erro na linha 1: Associação com código eol: 93238 não encontrado.\n"
        "Foram criados 0 repasses. Erro na importação de 1 repasse(s).")
    assert arquivo_carga_virgula.log == msg
    assert arquivo_carga_virgula.status == ERRO


@pytest.fixture
def acao_role_cultural_teste(acao_factory):
    return acao_factory(nome='Role Cultural')


@pytest.fixture
def acao_ptrf_basico(acao_factory):
    return acao_factory(nome='PTRF Básico',
                        aceita_capital=True, aceita_custeio=True,
                        aceita_livre=True)


@pytest.fixture
def conta_associacao_cartao_teste_data_inicio(associacao, tipo_conta, conta_associacao_factory):
    return conta_associacao_factory(
        associacao=associacao,
        tipo_conta=tipo_conta,
        data_inicio=datetime.date(2024, 1, 1)
    )


def test_carga_processado_com_erro(arquivo_carga_virgula_processado, periodo_teste_1, associacao, tipo_receita_repasse,
                                   tipo_conta_cheque, acao_role_cultural, acao_role_cultural_teste):
    carrega_repasses_previstos(arquivo_carga_virgula_processado)
    msg = (
        "Erro na linha 1: Ação Role Cultural não permite capital.\n"
        "Erro na linha 2: Associação com código eol: 93238 não encontrado.\n"
        "Foram criados 0 repasses. Erro na importação de 2 repasse(s)."
    )
    assert arquivo_carga_virgula_processado.log == msg, arquivo_carga_virgula_processado.log
    assert arquivo_carga_virgula_processado.status == ERRO


def test_carga_processado_com_erro_associacao_encerrada(arquivo_carga_virgula_processado_com_associacao_encerrada,
                                                        associacao_encerrada_2020_2,
                                                        periodo, tipo_receita_repasse, tipo_conta_cheque,
                                                        acao_ptrf_basico):
    carrega_repasses_previstos(arquivo_carga_virgula_processado_com_associacao_encerrada)
    msg = """Erro na linha 1: A associação foi encerrada em 31/12/2020. Linha ID:1
Foram criados 0 repasses. Erro na importação de 1 repasse(s)."""
    assert arquivo_carga_virgula_processado_com_associacao_encerrada.log == msg
    assert arquivo_carga_virgula_processado_com_associacao_encerrada.status == ERRO


def test_carga_deve_criar_conta(
    arquivo_carga_cartao_deve_criar_conta,
    associacao,
    periodo,
    tipo_receita_repasse,
    tipo_conta_cartao,
    acao_ptrf_basico,
    tipo_conta
):
    assert not ContaAssociacao.objects.filter(tipo_conta=tipo_conta_cartao, associacao=associacao).exists()
    carrega_repasses_previstos(arquivo_carga_cartao_deve_criar_conta)
    msg = """Foram criados 1 repasses. Erro na importação de 0 repasse(s)."""
    assert arquivo_carga_cartao_deve_criar_conta.log == msg
    assert arquivo_carga_cartao_deve_criar_conta.status == SUCESSO
    conta_associacao_cartao = ContaAssociacao.objects.get(tipo_conta=tipo_conta, associacao=associacao)
    assert conta_associacao_cartao.data_inicio == datetime.date(2023, 1, 1)


def test_carga_deve_gerar_erro_periodo_anterior_a_criacao_da_conta(
    arquivo_carga_cartao_deve_criar_conta,
    associacao,
    periodo,
    tipo_receita_repasse,
    tipo_conta,
    conta_associacao_cartao_teste_data_inicio,
    acao_ptrf_basico
):
    carrega_repasses_previstos(arquivo_carga_cartao_deve_criar_conta)
    msg = """Erro na linha 1: O período informado de repasse é anterior ao período de criação da conta.
Foram criados 0 repasses. Erro na importação de 1 repasse(s)."""
    assert arquivo_carga_cartao_deve_criar_conta.log == msg
    assert arquivo_carga_cartao_deve_criar_conta.status == ERRO


def test_carga_em_conta_encerrada_deve_gerar_erro(
        periodos_de_2019_ate_2023, acao_factory, acao_associacao_factory, associacao_factory,
        arquivo_factory, unidade_factory, tipo_conta_factory, conta_associacao_factory,
        solicitacao_encerramento_conta_associacao_factory, periodo_factory):
    from sme_ptrf_apps.core.models.solicitacao_encerramento_conta_associacao import (
        SolicitacaoEncerramentoContaAssociacao)

    unidade = unidade_factory(codigo_eol='666666')
    associacao = associacao_factory(unidade=unidade)
    acao = acao_factory(nome='Acao teste', aceita_capital=True, aceita_custeio=True)
    acao_associacao_factory.create(associacao=associacao, acao=acao)
    tipo_conta = tipo_conta_factory.create(nome='Cheque')
    conta = conta_associacao_factory.create(associacao=associacao, data_inicio='2018-10-20', tipo_conta=tipo_conta)
    solicitacao_encerramento_conta_associacao_factory.create(
        conta_associacao=conta, status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA)
    periodo = periodo_factory.create(data_inicio_realizacao_despesas=datetime.date(
        2023, 1, 1), data_fim_realizacao_despesas=datetime.date(2023, 5, 30))

    conteudo_arquivo = SimpleUploadedFile(
        '2020_01_01_a_2020_06_30_cheque.csv',
        bytes(
            (
                "Linha_ID,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n"
                "10,666666,200,200,,Acao teste"
            ), encoding="utf-8"))

    arquivo = arquivo_factory.create(identificador='2020_01_01_a_2020_06_30_cheque', conteudo=conteudo_arquivo,
                                     tipo_carga=CARGA_REPASSE_PREVISTO, tipo_delimitador=DELIMITADOR_VIRGULA,
                                     tipo_de_conta=tipo_conta, periodo=periodo)

    carrega_repasses_previstos(arquivo)

    msg = (
        "Erro na linha 1: A conta possui pedido de encerramento aprovado pela DRE.\n"
        "Foram criados 0 repasses. Erro na importação de 1 repasse(s).")

    assert arquivo.log == msg
    assert arquivo.status == ERRO


@pytest.fixture
def arquivo_associacao_periodo_com_pc():
    return SimpleUploadedFile(
        'carga_repasse_cheque_2.csv',
        bytes(
            (
                "Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n"
                "10,123456,99000.98,99000.98,,PTRF Básico"
            ),
            encoding="utf-8"))


@pytest.fixture
def arquivo_carga_associacao_periodo_com_pc(
        arquivo_associacao_periodo_com_pc, tipo_conta, periodo_2024, arquivo_factory):
    return arquivo_factory(
        identificador='cheque_2',
        conteudo=arquivo_associacao_periodo_com_pc,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
        tipo_de_conta=tipo_conta,
        periodo=periodo_2024
    )


@pytest.fixture
def periodo_pc(periodo_factory):
    return periodo_factory(
        referencia='2019.1',
        data_inicio_realizacao_despesas=datetime.date(2019, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2019, 11, 30),
    )


@pytest.fixture
def pc_teste(periodo_2024, associacao, prestacao_conta_factory):
    return prestacao_conta_factory(
        periodo=periodo_2024,
        associacao=associacao,
        data_recebimento=datetime.date(2020, 1, 1),
        status='APROVADA'
    )


def test_carga_processado_com_erro_associacao_periodo_com_pc(
    arquivo_carga_associacao_periodo_com_pc,
    periodo_pc,
    associacao,
    pc_teste,
    tipo_receita_repasse,
    tipo_conta_cheque,
    acao_ptrf_basico
):
    carrega_repasses_previstos(arquivo_carga_associacao_periodo_com_pc)
    assert "já possui PC gerada" in arquivo_carga_associacao_periodo_com_pc.log
    assert arquivo_carga_associacao_periodo_com_pc.status == ERRO, arquivo_carga_associacao_periodo_com_pc.status


class TestGetValor:
    def test_retorna_zero_para_valor_vazio(self):
        assert get_valor('') == 0

    def test_retorna_zero_para_none(self):
        assert get_valor(None) == 0

    def test_converte_string_com_ponto(self):
        assert get_valor('100.50') == Decimal('100.50')

    def test_converte_string_com_virgula(self):
        assert get_valor('100,50') == Decimal('100.50')

    def test_converte_inteiro(self):
        assert get_valor('99000') == Decimal('99000.0')

    def test_levanta_value_error_para_string_invalida(self):
        with pytest.raises(ValueError, match="Não foi possível converter"):
            get_valor('abc')


class TestGetIdLinha:
    def test_retorna_zero_para_string_vazia(self):
        assert get_id_linha('') == 0

    def test_retorna_zero_para_somente_espacos(self):
        assert get_id_linha('   ') == 0

    def test_converte_string_numerica(self):
        assert get_id_linha('10') == 10

    def test_converte_com_espacos(self):
        assert get_id_linha('  5  ') == 5

    def test_levanta_value_error_para_string_invalida(self):
        with pytest.raises(ValueError, match="Não foi possível converter"):
            get_id_linha('abc')


class TestGetAcao:
    def test_retorna_acao_existente(self, acao):
        resultado = get_acao(acao.nome)
        assert resultado == acao

    def test_levanta_excecao_para_acao_inexistente(self):
        with pytest.raises(CargaRepassePrevistoException, match="não encontrada"):
            get_acao('Ação Inexistente')


class TestVerificaTipoAplicacao:
    @pytest.fixture
    def acao_sem_capital(self, acao_factory):
        return acao_factory(nome='Acao Sem Capital', aceita_capital=False, aceita_custeio=True, aceita_livre=True)

    @pytest.fixture
    def acao_sem_custeio(self, acao_factory):
        return acao_factory(nome='Acao Sem Custeio', aceita_capital=True, aceita_custeio=False, aceita_livre=True)

    @pytest.fixture
    def acao_sem_livre(self, acao_factory):
        return acao_factory(nome='Acao Sem Livre', aceita_capital=True, aceita_custeio=True, aceita_livre=False)

    @pytest.fixture
    def acao_completa(self, acao_factory):
        return acao_factory(nome='Acao Completa', aceita_capital=True, aceita_custeio=True, aceita_livre=True)

    def test_levanta_excecao_quando_capital_nao_permitido(self, acao_sem_capital):
        with pytest.raises(CargaRepassePrevistoException, match="não permite capital"):
            verifica_tipo_aplicacao(acao_sem_capital, 100.0, 0, 0)

    def test_levanta_excecao_quando_custeio_nao_permitido(self, acao_sem_custeio):
        with pytest.raises(CargaRepassePrevistoException, match="não permite custeio"):
            verifica_tipo_aplicacao(acao_sem_custeio, 0, 100.0, 0)

    def test_levanta_excecao_quando_livre_nao_permitido(self, acao_sem_livre):
        with pytest.raises(CargaRepassePrevistoException, match="não permite livre aplicação"):
            verifica_tipo_aplicacao(acao_sem_livre, 0, 0, 100.0)

    def test_sem_excecao_quando_valores_zero(self, acao_sem_capital):
        verifica_tipo_aplicacao(acao_sem_capital, 0, 0, 0)

    def test_sem_excecao_para_acao_completa(self, acao_completa):
        verifica_tipo_aplicacao(acao_completa, 100.0, 100.0, 100.0)


class TestGetTipoConta:
    def test_retorna_tipo_conta_existente(self, tipo_conta):
        resultado = get_tipo_conta(tipo_conta.uuid)
        assert resultado == tipo_conta

    def test_levanta_excecao_para_uuid_inexistente(self):
        with pytest.raises(CargaRepassePrevistoException, match="não encontrado"):
            get_tipo_conta(uuid4())


class TestGetPeriodo:
    def test_retorna_periodo_existente(self, periodo):
        resultado = get_periodo(periodo.uuid)
        assert resultado == periodo

    def test_levanta_excecao_para_uuid_inexistente(self):
        with pytest.raises(CargaRepassePrevistoException, match="não encontrado"):
            get_periodo(uuid4())


class TestGetAcaoAssociacao:
    def test_retorna_acao_associacao_existente(self, acao_associacao, acao, associacao):
        resultado = get_acao_associacao(acao, associacao)
        assert resultado == acao_associacao

    def test_cria_acao_associacao_quando_nao_existe(self, acao_factory, associacao):
        from sme_ptrf_apps.core.models import AcaoAssociacao
        nova_acao = acao_factory(nome='Nova Acao Teste')
        assert not AcaoAssociacao.objects.filter(acao=nova_acao, associacao=associacao).exists()

        resultado = get_acao_associacao(nova_acao, associacao)

        assert resultado is not None
        assert AcaoAssociacao.objects.filter(acao=nova_acao, associacao=associacao).exists()


class TestGetContaAssociacao:
    def test_retorna_conta_associacao_existente(self, conta_associacao, tipo_conta, associacao):
        resultado = get_conta_associacao(tipo_conta, associacao, None)
        assert resultado == conta_associacao

    def test_cria_conta_associacao_com_data_inicio_quando_tem_periodo(self, tipo_conta, associacao, periodo):
        from sme_ptrf_apps.core.models import ContaAssociacao
        ContaAssociacao.objects.filter(tipo_conta=tipo_conta, associacao=associacao).delete()

        resultado = get_conta_associacao(tipo_conta, associacao, periodo)

        assert resultado is not None
        assert resultado.data_inicio == periodo.data_inicio_realizacao_despesas

    def test_cria_conta_associacao_sem_data_inicio_quando_sem_periodo(self, tipo_conta, associacao):
        from sme_ptrf_apps.core.models import ContaAssociacao
        ContaAssociacao.objects.filter(tipo_conta=tipo_conta, associacao=associacao).delete()

        resultado = get_conta_associacao(tipo_conta, associacao, None)

        assert resultado is not None
        assert resultado.data_inicio is None

    def test_retorna_none_para_tipo_conta_uuid_inexistente(self, associacao):
        resultado = get_conta_associacao(uuid4(), associacao, None)
        assert resultado is None


class TestGetDatasPeriodo:
    def test_retorna_datas_inicio_e_fim(self, periodo):
        start, end = get_datas_periodo(periodo)
        assert start == periodo.data_inicio_realizacao_despesas
        assert end == periodo.data_fim_realizacao_despesas


class TestAssociacaoPeriodoTemPc:
    def test_retorna_false_quando_nao_tem_pc(self, associacao, periodo):
        resultado = associacao_periodo_tem_pc(associacao, periodo)
        assert resultado is False

    def test_retorna_true_quando_tem_pc(self, associacao, periodo, prestacao_conta_factory):
        prestacao_conta_factory(associacao=associacao, periodo=periodo, status='APROVADA')
        resultado = associacao_periodo_tem_pc(associacao, periodo)
        assert resultado is True


# ---------------------------------------------------------------------------
# processa_repasse
# ---------------------------------------------------------------------------
@pytest.fixture
def arquivo_mock(arquivo_factory):
    return arquivo_factory(
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
    )


@pytest.fixture
def periodo_processa(periodo_factory):
    return periodo_factory(
        referencia='2023.1',
        data_inicio_realizacao_despesas=datetime.date(2023, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2023, 6, 30),
    )


@pytest.fixture
def tipo_conta_processa(tipo_conta_factory):
    return tipo_conta_factory(nome='Cheque Processa')


@pytest.fixture
def acao_processa(acao_factory):
    return acao_factory(nome='Acao Processa', aceita_capital=True, aceita_custeio=True, aceita_livre=True)


@pytest.fixture
def unidade_processa(dre, unidade_factory):
    return unidade_factory(codigo_eol='654321', dre=dre)


@pytest.fixture
def associacao_processa(unidade_processa, periodo_factory, associacao_factory):
    periodo_ini = periodo_factory(
        referencia='2022.2',
        data_inicio_realizacao_despesas=datetime.date(2022, 7, 1),
        data_fim_realizacao_despesas=datetime.date(2022, 12, 31),
    )
    return associacao_factory(
        nome='Associacao Processa',
        cnpj='11.222.333/0001-44',
        unidade=unidade_processa,
        periodo_inicial=periodo_ini,
    )


@pytest.fixture
def acao_associacao_processa(associacao_processa, acao_processa, acao_associacao_factory):
    return acao_associacao_factory(associacao=associacao_processa, acao=acao_processa)


@pytest.fixture
def conta_associacao_processa(associacao_processa, tipo_conta_processa, conta_associacao_factory):
    return conta_associacao_factory(
        associacao=associacao_processa,
        tipo_conta=tipo_conta_processa,
        data_inicio=datetime.datetime(2000, 1, 1))


class TestProcessaRepasse:
    def _make_reader(self, rows):
        return [['Id_Linha', 'Código eol', 'Valor capital', 'Valor custeio', 'Valor livre aplicacao', 'Acao']] + rows

    def test_cria_repasse_com_sucesso(
        self,
        arquivo_mock,
        periodo_processa,
        tipo_conta_processa,
        associacao_processa,
        acao_processa,
        acao_associacao_processa,
        conta_associacao_processa,
    ):
        reader = self._make_reader([
            ['1', '654321', '100', '200', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert Repasse.objects.filter(associacao=associacao_processa, periodo=periodo_processa).exists()
        assert arquivo_mock.status == SUCESSO

    def test_status_erro_quando_nenhum_repasse_criado(self, arquivo_mock, periodo_processa, tipo_conta_processa):
        reader = self._make_reader([
            ['1', '000000', '100', '200', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert arquivo_mock.status == ERRO

    def test_status_processado_com_erro_quando_parcialmente_importado(
        self,
        arquivo_mock,
        periodo_processa,
        tipo_conta_processa,
        associacao_processa,
        acao_processa,
        acao_associacao_processa,
        conta_associacao_processa,
    ):
        reader = self._make_reader([
            ['1', '654321', '100', '200', '0', 'Acao Processa'],
            ['2', '000000', '100', '200', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert arquivo_mock.status == PROCESSADO_COM_ERRO

    def test_erro_linha_com_menos_de_seis_colunas(self, arquivo_mock, periodo_processa, tipo_conta_processa):
        reader = [['Id', 'EOL', 'Capital']]
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert 'seis colunas' in arquivo_mock.log

    def test_erro_quando_associacao_nao_encontrada(self, arquivo_mock, periodo_processa, tipo_conta_processa):
        reader = self._make_reader([
            ['1', '000000', '100', '0', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert 'não encontrado' in arquivo_mock.log

    def test_erro_quando_conta_associacao_nao_disponivel(
        self,
        arquivo_mock,
        periodo_processa,
        acao_processa,
        associacao_processa,
        acao_associacao_processa,
        tipo_conta_factory
    ):
        tipo_conta_sem_conta = tipo_conta_factory(nome='TipoConta Sem Conta')
        reader = self._make_reader([
            ['1', '654321', '100', '0', '0', 'Acao Processa'],
        ])
        with patch('sme_ptrf_apps.receitas.services.carga_repasses_previstos.get_conta_associacao', return_value=None):
            processa_repasse(
                reader, tipo_conta_sem_conta.uuid, tipo_conta_sem_conta, arquivo_mock, periodo_processa
            )

        assert 'não possui a conta' in arquivo_mock.log

    def test_ignora_linha_com_todos_valores_zero(
        self,
        arquivo_mock,
        periodo_processa,
        tipo_conta_processa,
        associacao_processa,
        acao_processa,
        acao_associacao_processa,
        conta_associacao_processa,
    ):
        reader = self._make_reader([
            ['1', '654321', '0', '0', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert not Repasse.objects.filter(associacao=associacao_processa, periodo=periodo_processa).exists()
        assert arquivo_mock.status == ERRO

    def test_apaga_repasse_anterior_sem_realizacao_e_recria(
        self,
        arquivo_mock,
        periodo_processa,
        tipo_conta_processa,
        associacao_processa,
        acao_processa,
        acao_associacao_processa,
        conta_associacao_processa,
        repasse_factory
    ):
        repasse_existente = repasse_factory(
            associacao=associacao_processa,
            periodo=periodo_processa,
            carga_origem=arquivo_mock,
            carga_origem_linha_id=1,
            realizado_capital=False,
            realizado_custeio=False,
            realizado_livre=False,
        )
        repasse_existente_id = repasse_existente.pk

        reader = self._make_reader([
            ['1', '654321', '100', '0', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert not Repasse.objects.filter(pk=repasse_existente_id).exists()
        assert Repasse.objects.filter(associacao=associacao_processa, periodo=periodo_processa).count() == 1

    def test_ignora_repasse_anterior_com_realizacao(
        self,
        arquivo_mock,
        periodo_processa,
        tipo_conta_processa,
        associacao_processa,
        acao_processa,
        acao_associacao_processa,
        conta_associacao_processa,
        repasse_factory
    ):
        repasse_existente = repasse_factory(
            associacao=associacao_processa,
            periodo=periodo_processa,
            carga_origem=arquivo_mock,
            carga_origem_linha_id=2,
            realizado_capital=True,
            realizado_custeio=False,
            realizado_livre=False,
        )
        reader = self._make_reader([
            ['2', '654321', '100', '0', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert 'já teve realização' in arquivo_mock.log
        assert Repasse.objects.filter(pk=repasse_existente.pk).exists()

    def test_erro_quando_associacao_encerrada(
        self,
        arquivo_mock,
        periodo_processa,
        tipo_conta_processa,
        acao_processa,
        dre,
        unidade_factory,
        associacao_factory,
        acao_associacao_factory,
        conta_associacao_factory,
    ):
        unidade_enc = unidade_factory(codigo_eol='741852', dre=dre)
        assoc_enc = associacao_factory(
            unidade=unidade_enc,
            data_de_encerramento=datetime.date(2020, 1, 1),
        )
        acao_associacao_factory(associacao=assoc_enc, acao=acao_processa)
        conta_associacao_factory(associacao=assoc_enc, tipo_conta=tipo_conta_processa)

        reader = self._make_reader([
            ['1', '741852', '100', '0', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert 'foi encerrada' in arquivo_mock.log

    def test_erro_quando_periodo_anterior_a_data_inicio_da_conta(
        self,
        arquivo_mock,
        tipo_conta_processa,
        acao_processa,
        associacao_processa,
        acao_associacao_processa,
        periodo_factory,
        conta_associacao_factory
    ):
        periodo_antigo = periodo_factory(
            referencia='2021.1',
            data_inicio_realizacao_despesas=datetime.date(2021, 1, 1),
            data_fim_realizacao_despesas=datetime.date(2021, 6, 30),
        )
        conta_associacao_factory(
            associacao=associacao_processa,
            tipo_conta=tipo_conta_processa,
            data_inicio=datetime.date(2023, 1, 1),
        )

        reader = self._make_reader([
            ['1', '654321', '100', '0', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_antigo)

        assert 'anterior ao período de criação da conta' in arquivo_mock.log

    def test_erro_quando_associacao_tem_pc_no_periodo(
        self,
        arquivo_mock,
        periodo_processa,
        tipo_conta_processa,
        associacao_processa,
        acao_processa,
        acao_associacao_processa,
        conta_associacao_processa,
        prestacao_conta_factory,
    ):
        prestacao_conta_factory(associacao=associacao_processa, periodo=periodo_processa, status='APROVADA')

        reader = self._make_reader([
            ['1', '654321', '100', '0', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert 'já possui PC gerada' in arquivo_mock.log

    def test_linha_cabecalho_ignorada(
        self,
        arquivo_mock,
        periodo_processa,
        tipo_conta_processa,
        associacao_processa,
        acao_processa,
        acao_associacao_processa,
        conta_associacao_processa,
    ):
        reader = self._make_reader([
            ['1', '654321', '100', '0', '0', 'Acao Processa'],
        ])
        processa_repasse(reader, tipo_conta_processa.uuid, tipo_conta_processa, arquivo_mock, periodo_processa)

        assert Repasse.objects.filter(associacao=associacao_processa).count() == 1


@pytest.fixture
def periodo_carga(periodo_factory):
    return periodo_factory(
        referencia='2023.2',
        data_inicio_realizacao_despesas=datetime.date(2023, 7, 1),
        data_fim_realizacao_despesas=datetime.date(2023, 12, 31),
    )


@pytest.fixture
def tipo_conta_carga(tipo_conta_factory):
    return tipo_conta_factory(nome='Cheque Carga')


@pytest.fixture
def conteudo_csv_virgula():
    return SimpleUploadedFile(
        'repasses_virgula.csv',
        bytes(
            (
                "Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n"
                "1,123456,100,200,0,PTRF Básico"
            ),
            encoding='utf-8',
        ),
    )


@pytest.fixture
def conteudo_csv_ponto_virgula():
    return SimpleUploadedFile(
        'repasses_pv.csv',
        bytes(
            (
                "Id_Linha;Código eol;Valor capital;Valor custeio;Valor livre aplicacao;Acao\n"
                "1;123456;100;200;0;PTRF Básico"
            ),
            encoding='utf-8',
        ),
    )


class TestCarregaRepassesPrevistos:
    def test_erro_quando_sem_tipo_de_conta(self, periodo_carga, conteudo_csv_virgula, arquivo_factory):
        arquivo = arquivo_factory(
            identificador='carga-sem-tipo-conta',
            conteudo=conteudo_csv_virgula,
            tipo_carga=CARGA_REPASSE_PREVISTO,
            tipo_delimitador=DELIMITADOR_VIRGULA,
            tipo_de_conta=None,
            periodo=periodo_carga,
        )
        carrega_repasses_previstos(arquivo)

        assert arquivo.status == ERRO
        assert 'tipo de conta' in arquivo.log.lower()

    def test_erro_quando_sem_periodo(self, tipo_conta_carga, conteudo_csv_virgula, arquivo_factory):
        arquivo = arquivo_factory(
            identificador='carga-sem-periodo',
            conteudo=conteudo_csv_virgula,
            tipo_carga=CARGA_REPASSE_PREVISTO,
            tipo_delimitador=DELIMITADOR_VIRGULA,
            tipo_de_conta=tipo_conta_carga,
            periodo=None,
        )
        carrega_repasses_previstos(arquivo)

        assert arquivo.status == ERRO
        assert 'periodo' in arquivo.log.lower()

    def test_erro_quando_delimitador_incorreto(
            self, tipo_conta_carga, periodo_carga, conteudo_csv_virgula, arquivo_factory):
        arquivo = arquivo_factory(
            identificador='carga-delimitador-errado',
            conteudo=conteudo_csv_virgula,
            tipo_carga=CARGA_REPASSE_PREVISTO,
            tipo_delimitador=DELIMITADOR_PONTO_VIRGULA,
            tipo_de_conta=tipo_conta_carga,
            periodo=periodo_carga,
        )
        carrega_repasses_previstos(arquivo)

        assert arquivo.status == ERRO
        assert 'diferente do formato' in arquivo.log

    def test_sucesso_com_arquivo_valido(
        self,
        tipo_conta_carga,
        periodo_carga,
        conteudo_csv_virgula,
        associacao,
        unidade,
        acao_factory,
        conta_associacao_factory,
        acao_associacao_factory,
        arquivo_factory,
    ):
        acao = acao_factory(
            nome='PTRF Básico', aceita_capital=True, aceita_custeio=True, aceita_livre=True)
        conta_associacao_factory.create(
            associacao=associacao, tipo_conta=tipo_conta_carga, data_inicio=datetime.datetime(2000, 1, 1))
        acao_associacao_factory.create(
            associacao=associacao, acao=acao)

        arquivo = arquivo_factory(
            identificador='carga-valida',
            conteudo=conteudo_csv_virgula,
            tipo_carga=CARGA_REPASSE_PREVISTO,
            tipo_delimitador=DELIMITADOR_VIRGULA,
            tipo_de_conta=tipo_conta_carga,
            periodo=periodo_carga,
        )
        carrega_repasses_previstos(arquivo)

        assert arquivo.status == SUCESSO
        assert Repasse.objects.filter(associacao=associacao, periodo=periodo_carga).exists()

    def test_atualiza_ultima_execucao(self, tipo_conta_carga, periodo_carga, conteudo_csv_virgula, arquivo_factory):
        arquivo = arquivo_factory(
            identificador='carga-ultima-exec',
            conteudo=conteudo_csv_virgula,
            tipo_carga=CARGA_REPASSE_PREVISTO,
            tipo_delimitador=DELIMITADOR_PONTO_VIRGULA,
            tipo_de_conta=tipo_conta_carga,
            periodo=periodo_carga,
            ultima_execucao=None,
        )
        carrega_repasses_previstos(arquivo)

        assert arquivo.ultima_execucao is not None
