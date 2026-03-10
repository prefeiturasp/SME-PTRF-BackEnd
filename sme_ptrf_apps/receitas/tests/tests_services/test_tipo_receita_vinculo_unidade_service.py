import pytest
import uuid
from sme_ptrf_apps.receitas.services.tipo_receita_vinculo_unidade_service import (
    TipoReceitaVinculoUnidadeService,
    ValidacaoVinculoException,
)
from sme_ptrf_apps.core.fixtures.factories import UnidadeFactory


@pytest.fixture
def tipo_receita_1(tipo_receita_factory):
    tipo_receita = tipo_receita_factory.create(nome='Teste Tipo Receita')
    return tipo_receita


@pytest.fixture
def service_vinculo(tipo_receita_1):
    """Fixture que retorna instância do service de vínculo"""
    return TipoReceitaVinculoUnidadeService(tipo_receita_1)


@pytest.fixture
def unidades_teste():
    """Fixture de unidades para testes"""
    return UnidadeFactory.create_batch(3)


class TestTipoReceitaVinculoUnidadeServiceInit:
    """Testes para inicialização do service"""

    @pytest.mark.django_db
    def test_init_service_com_sucesso(self, tipo_receita_1):
        """Testa inicialização do service com sucesso"""
        service = TipoReceitaVinculoUnidadeService(tipo_receita_1)

        assert service.tipo_receita == tipo_receita_1
        assert isinstance(service, TipoReceitaVinculoUnidadeService)


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
        service_vinculo.tipo_receita.unidades.add(*unidades_teste)
        resultado = service_vinculo.vincular_todas_unidades()
        assert resultado['sucesso'] is True
        assert 'habilitadas com sucesso' in resultado['mensagem']
        assert service_vinculo.tipo_receita.unidades.count() == 0


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
        service_vinculo.tipo_receita.unidades.add(*unidades_teste)
        uuids = [str(unidades_teste[0].uuid)]
        resultado = service_vinculo.desvincular_unidades(uuids)
        assert resultado['sucesso'] is True
        assert 'desvinculada com sucesso' in resultado['mensagem']
        assert service_vinculo.tipo_receita.unidades.count() == 2

    @pytest.mark.django_db
    def test_desvincular_unidades_com_receita_associada(self, service_vinculo, receita_factory, associacao_factory):
        """Testa desvinculação com tipo receita em uso por uma unidade"""
        unidade_teste = UnidadeFactory.create()
        associacao_teste = associacao_factory.create(unidade=unidade_teste)

        receita_factory.create(
            tipo_receita=service_vinculo.tipo_receita,
            associacao=associacao_teste
        )

        service_vinculo.tipo_receita.unidades.add(unidade_teste)
        uuids = [str(unidade_teste.uuid)]
        with pytest.raises(ValidacaoVinculoException) as excinfo:
            service_vinculo.desvincular_unidades(uuids)
        assert 'Não é possível restringir o tipo de crédito' in str(excinfo.value)
    
    @pytest.mark.django_db
    def test_vincular_unidades_com_erro(self, service_vinculo):
        """Testa vincular com sucesso"""        
        uuids = [str(uuid.uuid4())]
        with pytest.raises(ValidacaoVinculoException) as excinfo:
            service_vinculo.vincular_unidades(uuids)
        assert "Nenhuma unidade foi identificada para desvínculo." in str(excinfo.value)
