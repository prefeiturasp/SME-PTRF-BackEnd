import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db

from freezegun import freeze_time
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

@pytest.fixture
@freeze_time('2020-10-27 13:59:00')
def arquivo_gerado_em_2020_10_27_13_59_00():
    return SimpleUploadedFile(f'arquivo.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
@freeze_time('2020-10-27 13:59:00')
def relatorio_dre_consolidado_gerado_final(periodo, dre, tipo_conta, arquivo_gerado_em_2020_10_27_13_59_00):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=dre,
        tipo_conta=tipo_conta,
        periodo=periodo,
        arquivo=arquivo_gerado_em_2020_10_27_13_59_00,
        status='GERADO_TOTAL'
    )


