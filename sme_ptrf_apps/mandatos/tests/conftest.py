from datetime import date
import pytest
from model_bakery import baker

pytestmark = pytest.mark.django_db


# Testes Solicitação de Migração
@pytest.fixture
def mandato_2023_a_2025__teste_solicitacao_de_migracao():
    return baker.make(
        'Mandato',
        referencia_mandato='2023 a 2025',
        data_inicial=date(2023, 1, 1),
        data_final=date(2025, 12, 31),
    )


@pytest.fixture
def solicitacao_de_migracao_eol_unidade_teste_service(unidade_teste_solicitacao_de_migracao):
    return baker.make(
        'SolicitacaoDeMigracao',
        eol_unidade=unidade_teste_solicitacao_de_migracao,
        dre=None,
        todas_as_unidades=False,
        status_processamento='PENDENTE',
        log_execucao='Este é o log da execução da migração',
    )


@pytest.fixture
def solicitacao_de_migracao_dre_teste_service(dre_teste_solicitacao_de_migracao):
    return baker.make(
        'SolicitacaoDeMigracao',
        eol_unidade=None,
        dre=dre_teste_solicitacao_de_migracao,
        todas_as_unidades=False,
        status_processamento='PENDENTE',
        log_execucao='Este é o log da execução da migração',
    )


@pytest.fixture
def solicitacao_de_migracao_todas_as_unidades_teste_service():
    return baker.make(
        'SolicitacaoDeMigracao',
        eol_unidade=None,
        dre=None,
        todas_as_unidades=True,
        status_processamento='PENDENTE',
        log_execucao='Este é o log da execução da migração',
    )


@pytest.fixture
def membro_associacao_teste_solicitacao_de_migracao(associacao_teste_solicitacao_de_migracao):
    return baker.make(
        'MembroAssociacao',
        nome='Jose Testando Solicitação de Migração',
        associacao=associacao_teste_solicitacao_de_migracao,
        cargo_associacao="VOGAL_1",
        cargo_educacao='',
        representacao="ESTUDANTE",
        codigo_identificacao='',
        email='jose@teste.com',
        cpf='372.346.360-64',
        telefone='11992137854',
        cep='04302000',
        bairro='Vila Teste',
        endereco='Rua Teste, 57'
    )


@pytest.fixture
def membro_associacao_teste_solicitacao_de_migracao_02(associacao_teste_solicitacao_de_migracao_02):
    return baker.make(
        'MembroAssociacao',
        nome='Jose Testando Solicitação de Migração 02',
        associacao=associacao_teste_solicitacao_de_migracao_02,
        cargo_associacao="VOGAL_2",
        cargo_educacao='',
        representacao="ESTUDANTE",
        codigo_identificacao='',
        email='jose@teste.com',
        cpf='959.603.370-02',
        telefone='11992137854',
        cep='04302000',
        bairro='Vila Teste',
        endereco='Rua Teste, 57'
    )

@pytest.fixture
def dre_teste_solicitacao_de_migracao():
    return baker.make(
        'Unidade',
        codigo_eol='12345',
        tipo_unidade='DRE',
        nome='DRE teste solicitação de migração',
        sigla='TM'
    )


@pytest.fixture
def unidade_teste_solicitacao_de_migracao(dre_teste_solicitacao_de_migracao):
    return baker.make(
        'Unidade',
        nome='Unidade Teste Solicitação de Migração',
        tipo_unidade='CEU',
        codigo_eol='123456',
        dre=dre_teste_solicitacao_de_migracao,
    )


@pytest.fixture
def unidade_teste_solicitacao_de_migracao_02(dre_teste_solicitacao_de_migracao):
    return baker.make(
        'Unidade',
        nome='Unidade Teste Solicitação de Migração 02',
        tipo_unidade='CEU',
        codigo_eol='654321',
        dre=dre_teste_solicitacao_de_migracao,
    )

@pytest.fixture
def periodo_anterior_teste_solicitacao_de_migracao():
    return baker.make(
        'Periodo',
        referencia='2023.1',
        data_inicio_realizacao_despesas=date(2023, 1, 1),
        data_fim_realizacao_despesas=date(2023, 8, 31),
    )


@pytest.fixture
def associacao_teste_solicitacao_de_migracao(unidade_teste_solicitacao_de_migracao, periodo_anterior_teste_solicitacao_de_migracao):
    return baker.make(
        'Associacao',
        nome='Associacao Teste Solicitação de Migração',
        cnpj='34.845.266/0001-57',
        unidade=unidade_teste_solicitacao_de_migracao,
        periodo_inicial=periodo_anterior_teste_solicitacao_de_migracao,
        ccm='0.000.00-0',
        email="ollyverottoboni2@gmail.com",
        processo_regularidade='123456',
    )

@pytest.fixture
def associacao_teste_solicitacao_de_migracao_02(unidade_teste_solicitacao_de_migracao_02, periodo_anterior_teste_solicitacao_de_migracao):
    return baker.make(
        'Associacao',
        nome='Associacao Teste Solicitação de Migração 02',
        cnpj='03.634.054/0001-05',
        unidade=unidade_teste_solicitacao_de_migracao_02,
        periodo_inicial=periodo_anterior_teste_solicitacao_de_migracao,
        ccm='0.000.00-0',
        email="ollyverottoboni2@gmail.com",
        processo_regularidade='123456',
    )


@pytest.fixture
def solicitacao_de_migracao_eol_unidade(unidade):
    return baker.make(
        'SolicitacaoDeMigracao',
        eol_unidade=unidade,
        dre=None,
        todas_as_unidades=False,
        status_processamento='PENDENTE',
        log_execucao='Este é o log da execução da migração',
    )

# FIM Testes Solicitação de Migração


@pytest.fixture
def mandato_2023_a_2025():
    return baker.make(
        'Mandato',
        referencia_mandato='2023 a 2025',
        data_inicial=date(2023, 7, 19),
        data_final=date(2023, 7, 20),
    )


@pytest.fixture
def mandato_2023_a_2025_testes_servicos_01():
    return baker.make(
        'Mandato',
        referencia_mandato='2023 a 2025',
        data_inicial=date(2023, 8, 8),
        data_final=date(2025, 12, 31),
    )


@pytest.fixture
def mandato_2023_a_2025_testes_servicos_02():
    return baker.make(
        'Mandato',
        referencia_mandato='2026 a 2028',
        data_inicial=date(2023, 7, 19),
        data_final=date(2023, 7, 20),
    )


@pytest.fixture
def mandato_2026_a_2027_testes_servicos_03():
    return baker.make(
        'Mandato',
        referencia_mandato='2026 a 2027',
        data_inicial=date(2026, 1, 1),
        data_final=date(2027, 12, 31),
    )


@pytest.fixture
def composicao_01_2023_a_2025_testes_servicos(mandato_2023_a_2025_testes_servicos_01, associacao):
    return baker.make(
        'Composicao',
        associacao=associacao,
        mandato=mandato_2023_a_2025_testes_servicos_01,
        data_inicial=date(2023, 1, 1),
        data_final=date(2025, 12, 31),
    )


@pytest.fixture
def composicao_02_2023_a_2025_testes_servicos(mandato_2023_a_2025_testes_servicos_01, associacao):
    return baker.make(
        'Composicao',
        associacao=associacao,
        mandato=mandato_2023_a_2025_testes_servicos_01,
        data_inicial=date(2026, 1, 1),
        data_final=date(2028, 12, 31),
    )


@pytest.fixture
def composicao_01_2023_a_2025(mandato_2023_a_2025, associacao):
    return baker.make(
        'Composicao',
        associacao=associacao,
        mandato=mandato_2023_a_2025,
        data_inicial=date(2023, 1, 1),
        data_final=date(2025, 12, 31),
    )


@pytest.fixture
def composicao_02_2023_a_2025(mandato_2023_a_2025, associacao):
    return baker.make(
        'Composicao',
        associacao=associacao,
        mandato=mandato_2023_a_2025,
        data_inicial=date(2023, 1, 1),
        data_final=date(2025, 12, 31),
    )


@pytest.fixture
def ocupante_cargo_01():
    return baker.make(
        'OcupanteCargo',
        nome="Ollyver Ottoboni",
        codigo_identificacao='1234567',
        cargo_educacao="Diretor de Escola",
        representacao='Servidor',
        email='ottoboniollyver@gmail.com',
        cpf_responsavel='907.536.560-86',
        telefone='11976643126',
        cep='02847070',
        bairro='Jd. Aeroporto',
        endereco='Rua do ocupante, 212',
    )


@pytest.fixture
def ocupante_cargo_02():
    return baker.make(
        'OcupanteCargo',
        nome="Ollyver Ottoboni 02",
        codigo_identificacao='754321',
        cargo_educacao="Diretor de Escola 02",
        representacao='Servidor',
        email='ottoboniollyver@gmail.com',
        cpf_responsavel='907.536.560-86',
        telefone='11976643126',
        cep='02847070',
        bairro='Jd. Aeroporto',
        endereco='Rua do ocupante, 212',
    )


@pytest.fixture
def cargo_composicao_01(
    composicao_01_2023_a_2025,
    ocupante_cargo_01,
):
    return baker.make(
        'CargoComposicao',
        composicao=composicao_01_2023_a_2025,
        ocupante_do_cargo=ocupante_cargo_01,
        cargo_associacao='Presidente da diretoria executiva',
        substituto=False,
        substituido=False,
    )


@pytest.fixture
def cargo_composicao_01_testes_services(
    composicao_01_2023_a_2025_testes_servicos,
    ocupante_cargo_01,
):
    return baker.make(
        'CargoComposicao',
        composicao=composicao_01_2023_a_2025_testes_servicos,
        ocupante_do_cargo=ocupante_cargo_01,
        cargo_associacao='PRESIDENTE_DIRETORIA_EXECUTIVA',
        substituto=False,
        substituido=False,
    )


@pytest.fixture
def cargo_composicao_02(
    composicao_01_2023_a_2025,
    ocupante_cargo_02,
):
    return baker.make(
        'CargoComposicao',
        composicao=composicao_01_2023_a_2025,
        ocupante_do_cargo=ocupante_cargo_02,
        cargo_associacao='Vice Presidente da diretoria executiva',
        substituto=False,
        substituido=False,
    )
