import pytest
from sme_ptrf_apps.despesas.services.tipo_custeio_vinculo_unidade_service import (
    TipoCusteioVinculoUnidadeService,
    ValidacaoVinculoException,
    STATUS_COMPLETO
)
from sme_ptrf_apps.core.fixtures.factories import UnidadeFactory


@pytest.fixture
def tipo_depesa_1(tipo_custeio_factory):
    tipo_receita = tipo_custeio_factory.create(nome='Teste Tipo Despesa de Custeio')
    return tipo_receita


@pytest.fixture
def service_vinculo(tipo_depesa_1):
    """Fixture que retorna instância do service de vínculo"""
    return TipoCusteioVinculoUnidadeService(tipo_depesa_1)


@pytest.fixture
def unidades_teste():
    """Fixture de unidades para testes"""
    return UnidadeFactory.create_batch(3)


class TestTipoReceitaVinculoUnidadeServiceInit:
    """Testes para inicialização do service"""

    @pytest.mark.django_db
    def test_init_service_com_sucesso(self, tipo_depesa_1):
        """Testa inicialização do service com sucesso"""
        service = TipoCusteioVinculoUnidadeService(tipo_depesa_1)

        assert service.tipo_custeio == tipo_depesa_1
        assert isinstance(service, TipoCusteioVinculoUnidadeService)


class TestVincularTodasUnidades:
    """Testes para vincular_todas_unidades"""

    @pytest.mark.django_db
    def test_vincular_todas_sem_unidades_atuais(self, service_vinculo):
        """Testa vincular todas quando não há unidades vinculadas"""
        resultado = service_vinculo.vincular_todas_unidades()
        assert resultado['sucesso'] is True
        assert 'já estão habilitadas' in resultado['mensagem']

    @pytest.mark.django_db
    def test_vincular_todas_com_unidades_atuais(self, service_vinculo, unidades_teste):
        """Testa vincular todas quando há unidades vinculadas"""
        service_vinculo.tipo_custeio.unidades.add(*unidades_teste)
        resultado = service_vinculo.vincular_todas_unidades()
        assert resultado['sucesso'] is True
        assert 'habilitadas com sucesso' in resultado['mensagem']
        assert service_vinculo.tipo_custeio.unidades.count() == 0


class TestDesvincularUnidades:
    """Testes para desvincular_unidades"""

    @pytest.mark.django_db
    def test_desvincular_unidades_sem_unidades(self, service_vinculo):
        """Testa desvinculação sem unidades identificadas"""
        with pytest.raises(ValidacaoVinculoException) as excinfo:
            service_vinculo.desvincular_unidades([])

        assert 'Nenhuma unidade' in str(excinfo.value)

    @pytest.mark.django_db
    def test_desvincular_unidades_com_sucesso(self, service_vinculo, unidades_teste):
        """Testa desvinculação com sucesso"""
        service_vinculo.tipo_custeio.unidades.add(*unidades_teste)
        uuids = [str(unidades_teste[0].uuid)]
        resultado = service_vinculo.desvincular_unidades(uuids)
        assert resultado['sucesso'] is True
        assert 'desvinculada com sucesso' in resultado['mensagem']
        assert service_vinculo.tipo_custeio.unidades.count() == 2
            
    @pytest.mark.django_db
    def test_desvincular_unidades_com_despesa_associada(
        self,
        service_vinculo,
        rateio_despesa_factory,
        despesa_factory,
        associacao_factory
    ):
        unidade_teste = UnidadeFactory.create()
        associacao = associacao_factory(unidade=unidade_teste)

        tipo_custeio = service_vinculo.tipo_custeio

        despesa = despesa_factory(
            status=STATUS_COMPLETO,
            associacao=associacao,
        )

        rateio_despesa_factory(
            despesa=despesa,
            associacao=associacao,
            tipo_custeio=tipo_custeio,
        )

        service_vinculo.tipo_custeio.unidades.add(unidade_teste)

        uuids = [str(unidade_teste.uuid)]

        with pytest.raises(ValidacaoVinculoException) as excinfo:
            service_vinculo.desvincular_unidades(uuids)

        assert "Não é possível restringir o tipo de custeio" in str(excinfo.value)