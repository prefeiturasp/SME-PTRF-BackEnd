import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker


from sme_ptrf_apps.core.choices.tipos_carga import CARGA_ASSOCIACOES

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo_modelo_carga_associacao():
    return SimpleUploadedFile(
        f'arquivo.csv',
        bytes(f"""Código EOL UE;Nome UE;Código EOL DRE;Nome da DRE UE;Sigla DRE;Nome da associação;CNPJ da associação;RF Presidente Diretoria;Nome Presidente Diretoria;RF Presidente Conselho Fiscal;Nome Presidente Conselho Fiscal""", encoding="utf-8"))


@pytest.fixture
def modelo_carga_associacao(arquivo_modelo_carga_associacao):
    return baker.make(
        'ModeloCarga',
        tipo_carga=CARGA_ASSOCIACOES,
        arquivo=arquivo_modelo_carga_associacao,
    )
