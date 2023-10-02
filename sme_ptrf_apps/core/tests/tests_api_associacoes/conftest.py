import pytest
from model_bakery import baker
from sme_ptrf_apps.core.models.membro_associacao import MembroEnum, RepresentacaoCargo
from sme_ptrf_apps.core.models import ContaAssociacao, SolicitacaoEncerramentoContaAssociacao

@pytest.fixture
def membro_associacao_001(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 001',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        email='membroassociacao001@gmail.com',
        codigo_identificacao='001'
    )

@pytest.fixture
def membro_associacao_002(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 002',
        associacao=associacao,
        cargo_associacao=MembroEnum.VICE_PRESIDENTE_DIRETORIA_EXECUTIVA.name,
        email='membroassociacao002@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='002'
    )

@pytest.fixture
def membro_associacao_003(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 003',
        associacao=associacao,
        cargo_associacao=MembroEnum.SECRETARIO.name,
        email='membroassociacao003@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='003'
    )

@pytest.fixture
def membro_associacao_004(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 004',
        associacao=associacao,
        cargo_associacao=MembroEnum.TESOUREIRO.name,
        email='membroassociacao004@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='004'
    )

@pytest.fixture
def membro_associacao_005(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 005',
        associacao=associacao,
        cargo_associacao=MembroEnum.VOGAL_1.name,
        email='membroassociacao005@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='005'
    )

@pytest.fixture
def membro_associacao_006(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 006',
        associacao=associacao,
        cargo_associacao=MembroEnum.VOGAL_2.name,
        email='membroassociacao006@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='006'
    )

@pytest.fixture
def membro_associacao_007(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 007',
        associacao=associacao,
        cargo_associacao=MembroEnum.VOGAL_3.name,
        email='membroassociacao007@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='007'
    )

@pytest.fixture
def membro_associacao_008(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 008',
        associacao=associacao,
        cargo_associacao=MembroEnum.VOGAL_4.name,
        email='membroassociacao008@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='008'
    )

@pytest.fixture
def membro_associacao_009(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 009',
        associacao=associacao,
        cargo_associacao=MembroEnum.VOGAL_5.name,
        email='membroassociacao009@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='009'
    )

@pytest.fixture
def membro_associacao_010(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 010',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.name,
        email='membroassociacao010@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='0010'
    )

@pytest.fixture
def membro_associacao_011(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 011',
        associacao=associacao,
        cargo_associacao=MembroEnum.CONSELHEIRO_1.name,
        email='membroassociacao011@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='0011'
    )

@pytest.fixture
def membro_associacao_012(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 012',
        associacao=associacao,
        cargo_associacao=MembroEnum.CONSELHEIRO_2.name,
        email='membroassociacao012@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='0012'
    )

@pytest.fixture
def membro_associacao_013(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 013',
        associacao=associacao,
        cargo_associacao=MembroEnum.CONSELHEIRO_3.name,
        email='membroassociacao013@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='0013'
    )

@pytest.fixture
def membro_associacao_014(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao 014',
        associacao=associacao,
        cargo_associacao=MembroEnum.CONSELHEIRO_4.name,
        email='membroassociacao014@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='0014'
    )


@pytest.fixture
def membro_associacao_cadastro_incompleto_001(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 001',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        email='membroassociacao001@gmail.com',
        codigo_identificacao='001'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_002(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 002',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.VICE_PRESIDENTE_DIRETORIA_EXECUTIVA.name,
        email='membroassociacao002@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='002'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_003(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 003',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.SECRETARIO.name,
        email='membroassociacao003@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='003'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_004(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 004',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.TESOUREIRO.name,
        email='membroassociacao004@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='004'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_005(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 005',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.VOGAL_1.name,
        email='membroassociacao005@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='005'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_006(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 006',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.VOGAL_2.name,
        email='membroassociacao006@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='006'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_007(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 007',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.VOGAL_3.name,
        email='membroassociacao007@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='007'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_008(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 008',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.VOGAL_4.name,
        email='membroassociacao008@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='008'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_009(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 009',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.VOGAL_5.name,
        email='membroassociacao009@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='009'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_010(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 010',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.name,
        email='membroassociacao010@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='0010'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_011(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 011',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.CONSELHEIRO_1.name,
        email='membroassociacao011@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='0011'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_012(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 012',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.CONSELHEIRO_2.name,
        email='membroassociacao012@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='0012'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_013(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 013',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.CONSELHEIRO_3.name,
        email='membroassociacao013@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='0013'
    )

@pytest.fixture
def membro_associacao_cadastro_incompleto_014(associacao_cadastro_incompleto):
    return baker.make(
        'MembroAssociacao',
        nome='Membro Associacao Cadastro Incompleto 014',
        associacao=associacao_cadastro_incompleto,
        cargo_associacao=MembroEnum.CONSELHEIRO_4.name,
        email='membroassociacao014@gmail.com',
        representacao=RepresentacaoCargo.SERVIDOR.name,
        codigo_identificacao='0014'
    )

@pytest.fixture
def tipo_conta_encerramento_conta():
    return baker.make(
        'TipoConta',
        nome='Cheque encerramento conta',
        banco_nome='Banco do Inter',
        agencia='67945',
        numero_conta='935556-x',
        numero_cartao='987644164221',
        permite_inativacao=True
    )

@pytest.fixture
def unidade_encerramento_conta(dre):
    return baker.make(
        'Unidade',
        nome='Escola encerramento conta',
        tipo_unidade='EMEI',
        codigo_eol='270009',
        dre=dre,
        sigla='EA'
    )


@pytest.fixture
def associacao_encerramento_conta(unidade_encerramento_conta, periodo_2020_1):
    return baker.make(
        'Associacao',
        nome='Associacao 271170',
        cnpj='62.738.735/0001-74',
        unidade=unidade_encerramento_conta,
        periodo_inicial=periodo_2020_1
    )

@pytest.fixture
def conta_associacao_encerramento_conta(associacao_encerramento_conta, tipo_conta_encerramento_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao_encerramento_conta,
        tipo_conta=tipo_conta_encerramento_conta,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523',
        status=ContaAssociacao.STATUS_INATIVA
    )
@pytest.fixture
def solicitacao_encerramento_conta_aprovada(conta_associacao_encerramento_conta, periodo_2020_1):
    return baker.make(
        'SolicitacaoEncerramentoContaAssociacao',
        conta_associacao=conta_associacao_encerramento_conta,
        status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA,
        data_de_encerramento_na_agencia=periodo_2020_1.data_inicio_realizacao_despesas,
        data_aprovacao=periodo_2020_1.data_inicio_realizacao_despesas
    )


@pytest.fixture
def solicitacao_encerramento_conta_pendente(conta_associacao_encerramento_conta, periodo_2020_1):
    return baker.make(
        'SolicitacaoEncerramentoContaAssociacao',
        conta_associacao=conta_associacao_encerramento_conta,
        status=SolicitacaoEncerramentoContaAssociacao.STATUS_PENDENTE,
        data_de_encerramento_na_agencia=periodo_2020_1.data_inicio_realizacao_despesas,
    )


@pytest.fixture
def receita_conta_encerrada(associacao_encerramento_conta, conta_associacao_encerramento_conta, acao_associacao, tipo_receita, periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao_encerramento_conta,
        data=periodo_2020_1.data_inicio_realizacao_despesas,
        valor=100.00,
        conta_associacao=conta_associacao_encerramento_conta,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )
