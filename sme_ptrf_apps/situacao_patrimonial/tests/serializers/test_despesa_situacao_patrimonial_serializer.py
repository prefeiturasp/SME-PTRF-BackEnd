import pytest

from sme_ptrf_apps.situacao_patrimonial.api.serializers.despesa_situacao_patrimonial_serializer import (
    DespesaSituacaoPatrimonialSerializer,
)

pytestmark = pytest.mark.django_db


def test_periodo_referencia_retorna_periodo_do_recurso_da_despesa(
    associacao_1,
    recurso_factory,
    periodo_factory,
    despesa_factory,
):
    recurso = recurso_factory.create(legado=False)
    outro_recurso = recurso_factory.create(legado=False)

    periodo_factory.create(
        recurso=outro_recurso,
        referencia='2026.1',
        data_inicio_realizacao_despesas='2026-01-01',
        data_fim_realizacao_despesas='2026-06-30',
    )
    periodo_factory.create(
        recurso=recurso,
        referencia='2026.2',
        data_inicio_realizacao_despesas='2026-01-01',
        data_fim_realizacao_despesas='2026-06-30',
    )

    despesa = despesa_factory.create(associacao=associacao_1, recurso=recurso, data_documento='2026-03-15')
    despesa.refresh_from_db()

    data = DespesaSituacaoPatrimonialSerializer(despesa).data

    assert data['periodo_referencia'] == '2026.2'
