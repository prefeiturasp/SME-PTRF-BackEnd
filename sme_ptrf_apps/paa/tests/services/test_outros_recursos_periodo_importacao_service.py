import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from sme_ptrf_apps.paa.services import (
    OutroRecursoPeriodoPaaImportacaoService,
    ImportacaoUnidadesOutroRecursoException
)
from sme_ptrf_apps.paa.fixtures.factories import OutroRecursoPeriodoFactory
from sme_ptrf_apps.core.fixtures.factories import UnidadeFactory


@pytest.fixture
def outros_recursos_periodo(periodo_paa_factory, outro_recurso_factory, outro_recurso_periodo_factory):
    periodo_paa = periodo_paa_factory.create(
        referencia='2000.10',
        data_inicial=date(2000, 1, 1),
        data_final=date(2000, 4, 30),
    )
    outro_recurso = outro_recurso_factory.create(nome='Teste 2000')
    return outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa,
        ativo=True
    )


@pytest.mark.django_db
def test_importar_unidades_com_sucesso(
    outros_recursos_periodo,
    periodo_paa,
    outro_recurso_factory,
):
    """Testa importação de unidades com sucesso"""
    # Cria recurso de origem com unidades
    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem")
    )
    unidades = UnidadeFactory.create_batch(3)
    origem.unidades.add(*unidades)

    # Executa importação
    OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
        destino=outros_recursos_periodo,
        origem_uuid=str(origem.uuid)
    )

    # Verifica que unidades foram importadas
    assert outros_recursos_periodo.unidades.count() == 3
    for unidade in unidades:
        assert unidade in outros_recursos_periodo.unidades.all()


@pytest.mark.django_db
def test_importar_unidades_sem_origem_uuid(
    outros_recursos_periodo,
):
    """Testa que exceção é levantada quando origem_uuid não é fornecido"""
    with pytest.raises(ImportacaoUnidadesOutroRecursoException) as excinfo:
        OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
            destino=outros_recursos_periodo,
            origem_uuid=""
        )

    assert "origem_uuid é obrigatório" in str(excinfo.value)


@pytest.mark.django_db
def test_importar_unidades_origem_uuid_none(
    outros_recursos_periodo,
):
    """Testa que exceção é levantada quando origem_uuid é None"""
    with pytest.raises(ImportacaoUnidadesOutroRecursoException) as excinfo:
        OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
            destino=outros_recursos_periodo,
            origem_uuid=None
        )

    assert "origem_uuid é obrigatório" in str(excinfo.value)


@pytest.mark.django_db
def test_importar_unidades_origem_nao_encontrada(
    outros_recursos_periodo,
):
    """Testa que exceção é levantada quando origem não existe"""
    import uuid
    origem_uuid_inexistente = str(uuid.uuid4())

    with pytest.raises(ImportacaoUnidadesOutroRecursoException) as excinfo:
        OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
            destino=outros_recursos_periodo,
            origem_uuid=origem_uuid_inexistente
        )

    assert "Recurso de origem não encontrado" in str(excinfo.value)


@pytest.mark.django_db
def test_importar_unidades_origem_destino_iguais(
    outros_recursos_periodo,
):
    """Testa que exceção é levantada quando origem e destino são iguais"""
    with pytest.raises(ImportacaoUnidadesOutroRecursoException) as excinfo:
        OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
            destino=outros_recursos_periodo,
            origem_uuid=str(outros_recursos_periodo.uuid)
        )

    assert "origem não pode ser o mesmo que o destino" in str(excinfo.value)


@pytest.mark.django_db
def test_importar_unidades_origem_sem_unidades(
    outros_recursos_periodo,
    periodo_paa,
    outro_recurso_factory,
):
    """Testa importação quando origem não tem unidades vinculadas"""
    # Cria recurso de origem sem unidades
    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem")
    )

    # Executa importação
    OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
        destino=outros_recursos_periodo,
        origem_uuid=str(origem.uuid)
    )

    # Verifica que nenhuma unidade foi importada
    assert outros_recursos_periodo.unidades.count() == 0


@pytest.mark.django_db
def test_importar_unidades_destino_ja_possui_unidades(
    outros_recursos_periodo,
    periodo_paa,
    outro_recurso_factory,
):
    """Testa importação quando destino já possui unidades"""
    # Adiciona unidades ao destino
    unidades_destino = UnidadeFactory.create_batch(2)
    outros_recursos_periodo.unidades.add(*unidades_destino)

    # Cria recurso de origem com unidades diferentes
    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem")
    )
    unidades_origem = UnidadeFactory.create_batch(3)
    origem.unidades.add(*unidades_origem)

    # Executa importação
    OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
        destino=outros_recursos_periodo,
        origem_uuid=str(origem.uuid)
    )

    # Verifica que destino possui todas as unidades (2 antigas + 3 novas)
    assert outros_recursos_periodo.unidades.count() == 5


@pytest.mark.django_db
def test_importar_unidades_com_unidades_duplicadas(
    outros_recursos_periodo,
    periodo_paa,
    outro_recurso_factory,
):
    """Testa importação quando há unidades duplicadas entre origem e destino"""
    # Cria unidades compartilhadas
    unidades_compartilhadas = UnidadeFactory.create_batch(2)
    outros_recursos_periodo.unidades.add(*unidades_compartilhadas)

    # Cria recurso de origem com mesmas unidades + novas
    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem")
    )
    unidades_novas = UnidadeFactory.create_batch(3)
    origem.unidades.add(*unidades_compartilhadas)
    origem.unidades.add(*unidades_novas)

    # Executa importação
    OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
        destino=outros_recursos_periodo,
        origem_uuid=str(origem.uuid)
    )

    # Verifica que não há duplicatas (2 compartilhadas + 3 novas = 5 total)
    assert outros_recursos_periodo.unidades.count() == 5


@pytest.mark.django_db
def test_importar_unidades_transacao_atomica(
    outros_recursos_periodo,
    periodo_paa,
    outro_recurso_factory,
):
    """Testa que importação é realizada em transação atômica"""
    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem")
    )
    unidades = UnidadeFactory.create_batch(3)
    origem.unidades.add(*unidades)

    # Mock para forçar erro durante a execução
    with patch.object(
        OutroRecursoPeriodoPaaImportacaoService,
        '_executar_importacao',
        side_effect=Exception("Erro simulado")
    ):
        with pytest.raises(Exception):
            OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
                destino=outros_recursos_periodo,
                origem_uuid=str(origem.uuid)
            )

    # Verifica que nenhuma unidade foi adicionada (rollback)
    assert outros_recursos_periodo.unidades.count() == 0


@pytest.mark.django_db
def test_obter_origem_com_sucesso(
    outros_recursos_periodo,
):
    """Testa obtenção da origem com sucesso"""
    origem = OutroRecursoPeriodoPaaImportacaoService._obter_origem(
        str(outros_recursos_periodo.uuid)
    )

    assert origem == outros_recursos_periodo


@pytest.mark.django_db
def test_obter_origem_nao_encontrada():
    """Testa exceção quando origem não é encontrada"""
    import uuid
    origem_uuid_inexistente = str(uuid.uuid4())

    with pytest.raises(ImportacaoUnidadesOutroRecursoException) as excinfo:
        OutroRecursoPeriodoPaaImportacaoService._obter_origem(origem_uuid_inexistente)

    assert "Recurso de origem não encontrado" in str(excinfo.value), str(excinfo.value)


@pytest.mark.django_db
def test_obter_origem_com_prefetch_related(
    outros_recursos_periodo,
):
    """Testa que unidades são carregadas com prefetch_related"""
    unidades = UnidadeFactory.create_batch(3)
    outros_recursos_periodo.unidades.add(*unidades)

    with patch('sme_ptrf_apps.paa.models.OutroRecursoPeriodoPaa.objects.prefetch_related') as mock_prefetch:
        mock_queryset = MagicMock()
        mock_prefetch.return_value = mock_queryset
        mock_queryset.get.return_value = outros_recursos_periodo

        OutroRecursoPeriodoPaaImportacaoService._obter_origem(
            str(outros_recursos_periodo.uuid)
        )

        # Verifica que prefetch_related foi chamado com 'unidades'
        mock_prefetch.assert_called_once_with('unidades')


@pytest.mark.django_db
def test_validar_origem_destino_diferentes(
    outros_recursos_periodo,
    periodo_paa,
    outro_recurso_factory,
):
    """Testa validação quando origem e destino são diferentes"""
    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem")
    )

    # Não deve levantar exceção
    try:
        OutroRecursoPeriodoPaaImportacaoService._validar_origem_destino(
            outros_recursos_periodo,
            origem
        )
    except ImportacaoUnidadesOutroRecursoException:
        pytest.fail("Não deveria levantar exceção para origem e destino diferentes")


@pytest.mark.django_db
def test_validar_origem_destino_iguais(
    outros_recursos_periodo,
):
    """Testa validação quando origem e destino são iguais"""
    with pytest.raises(ImportacaoUnidadesOutroRecursoException) as excinfo:
        OutroRecursoPeriodoPaaImportacaoService._validar_origem_destino(
            outros_recursos_periodo,
            outros_recursos_periodo
        )

    assert "origem não pode ser o mesmo que o destino" in str(excinfo.value)


@pytest.mark.django_db
def test_executar_importacao_com_unidades(
    outros_recursos_periodo,
    periodo_paa,
    outro_recurso_factory,
):
    """Testa execução da importação com unidades"""
    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem")
    )
    unidades = UnidadeFactory.create_batch(3)
    origem.unidades.add(*unidades)

    OutroRecursoPeriodoPaaImportacaoService._executar_importacao(
        outros_recursos_periodo,
        origem
    )

    assert outros_recursos_periodo.unidades.count() == 3
    for unidade in unidades:
        assert unidade in outros_recursos_periodo.unidades.all()


@pytest.mark.django_db
def test_executar_importacao_sem_unidades(
    outros_recursos_periodo,
    periodo_paa,
    outro_recurso_factory,
):
    """Testa execução quando origem não tem unidades"""
    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem")
    )

    OutroRecursoPeriodoPaaImportacaoService._executar_importacao(
        outros_recursos_periodo,
        origem
    )

    assert outros_recursos_periodo.unidades.count() == 0


@pytest.mark.django_db
def test_fluxo_completo_importacao(
    outros_recursos_periodo,
    periodo_paa,
    outro_recurso_factory,
):
    """Testa fluxo completo de importação"""
    # Setup: cria origem com unidades
    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem")
    )
    unidades = UnidadeFactory.create_batch(5)
    origem.unidades.add(*unidades)

    # Estado inicial do destino
    assert outros_recursos_periodo.unidades.count() == 0

    # Executa importação
    OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
        destino=outros_recursos_periodo,
        origem_uuid=str(origem.uuid)
    )

    # Verifica resultado
    assert outros_recursos_periodo.unidades.count() == 5
    assert origem.unidades.count() == 5  # Origem não é afetada


@pytest.mark.django_db
def test_multiplas_importacoes_sucessivas(
    outros_recursos_periodo,
    periodo_paa,
    outro_recurso_factory,
):
    """Testa múltiplas importações sucessivas"""
    # Primeira importação
    origem1 = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem 1")
    )
    unidades1 = UnidadeFactory.create_batch(3)
    origem1.unidades.add(*unidades1)

    OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
        destino=outros_recursos_periodo,
        origem_uuid=str(origem1.uuid)
    )
    assert outros_recursos_periodo.unidades.count() == 3

    # Segunda importação
    origem2 = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa,
        outro_recurso=outro_recurso_factory.create(nome="Recurso Origem 2")
    )
    unidades2 = UnidadeFactory.create_batch(2)
    origem2.unidades.add(*unidades2)

    OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
        destino=outros_recursos_periodo,
        origem_uuid=str(origem2.uuid)
    )
    assert outros_recursos_periodo.unidades.count() == 5
