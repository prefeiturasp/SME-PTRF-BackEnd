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

def test_relatorio_final(jwt_authenticated_client_relatorio_consolidado, periodo, dre, tipo_conta, relatorio_dre_consolidado_gerado_final):

    url = f'/api/relatorios-consolidados-dre/download/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}'
    response = jwt_authenticated_client_relatorio_consolidado.get(url)
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == 'attachment; filename=relatorio_dre.xlsx'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response.status_code == status.HTTP_200_OK

