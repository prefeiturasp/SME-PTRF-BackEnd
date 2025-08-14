import pytest
from model_bakery import baker
from freezegun import freeze_time
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def ambiente():
    return baker.make(
        'Ambiente',
        prefixo='dev-sig-escola',
        nome='Ambiente de desenvolvimento',
    )


@pytest.fixture
@freeze_time('2020-06-30 00:00:00')
def comprovante_extrato():
    return SimpleUploadedFile('comprovante.pdf', bytes('CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
def observacao_conciliacao_exportacao_csv(associacao, conta_associacao, periodo_2020_1, comprovante_extrato):
    return baker.make(
        'ObservacaoConciliacao',
        associacao=associacao,
        periodo=periodo_2020_1,
        conta_associacao=conta_associacao,
        data_extrato='2020-06-30',
        saldo_extrato=300,
        comprovante_extrato=comprovante_extrato)
