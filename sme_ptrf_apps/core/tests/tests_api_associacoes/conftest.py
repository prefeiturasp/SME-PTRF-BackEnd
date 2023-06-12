import pytest
from model_bakery import baker
from sme_ptrf_apps.core.models.membro_associacao import MembroEnum, RepresentacaoCargo

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
