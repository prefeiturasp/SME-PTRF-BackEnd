import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from sme_ptrf_apps.paa.services import (
    OutroRecursoPeriodoPaaVinculoUnidadeService,
    UnidadeNaoEncontradaException,
    ValidacaoVinculoException,
    ConfirmacaoVinculoException
)
from sme_ptrf_apps.paa.fixtures.factories import PaaFactory
from sme_ptrf_apps.core.fixtures.factories import UnidadeFactory
from sme_ptrf_apps.paa.enums import PaaStatusEnum


@pytest.fixture
def periodo_paa_1(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia='P 2020.1',
        data_inicial=date(2020, 1, 1),
        data_final=date(2020, 4, 30),
    )


@pytest.fixture
def outros_recursos_periodo(periodo_paa_1, outro_recurso_factory, outro_recurso_periodo_factory):
    outro_recurso = outro_recurso_factory.create(nome='Teste 2000')
    return outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa_1,
        ativo=True
    )


@pytest.fixture
def paa_em_elaboracao(outros_recursos_periodo):
    """Fixture de PAA em elaboração"""
    return PaaFactory.create(
        status=PaaStatusEnum.EM_ELABORACAO.name,
        periodo_paa=outros_recursos_periodo.periodo_paa
    )


@pytest.fixture
def paa_gerado(outros_recursos_periodo):
    """Fixture de PAA gerado"""
    return PaaFactory.create(
        status=PaaStatusEnum.GERADO.name,
        periodo_paa=outros_recursos_periodo.periodo_paa
    )


@pytest.fixture
def paa_retificado(outros_recursos_periodo):
    """Fixture de PAA retificado"""
    return PaaFactory.create(
        status=PaaStatusEnum.EM_RETIFICACAO.name,
        periodo_paa=outros_recursos_periodo.periodo_paa
    )


@pytest.fixture
def service_vinculo(outros_recursos_periodo):
    """Fixture que retorna instância do service de vínculo"""
    return OutroRecursoPeriodoPaaVinculoUnidadeService(outros_recursos_periodo)


@pytest.fixture
def unidades_teste():
    """Fixture de unidades para testes"""
    return UnidadeFactory.create_batch(3)


class TestOutroRecursoPeriodoPaaVinculoUnidadeServiceInit:
    """Testes para inicialização do service"""

    @pytest.mark.django_db
    def test_init_service_com_sucesso(self, outros_recursos_periodo):
        """Testa inicialização do service com sucesso"""
        service = OutroRecursoPeriodoPaaVinculoUnidadeService(outros_recursos_periodo)

        assert service.outro_recurso_periodo == outros_recursos_periodo
        assert isinstance(service, OutroRecursoPeriodoPaaVinculoUnidadeService)

    @pytest.mark.django_db
    def test_init_service_herda_base_service(self, outros_recursos_periodo):
        """Testa que service herda de OutroRecursoPeriodoBaseService"""
        from sme_ptrf_apps.paa.services import OutroRecursoPeriodoBaseService

        service = OutroRecursoPeriodoPaaVinculoUnidadeService(outros_recursos_periodo)

        assert isinstance(service, OutroRecursoPeriodoBaseService)


class TestValidarRecursoAtivo:
    """Testes para _validar_recurso_ativo"""

    @pytest.mark.django_db
    def test_validar_recurso_ativo_sucesso(self, service_vinculo):
        """Testa validação quando recurso está ativo"""
        service_vinculo.outro_recurso_periodo.ativo = True
        service_vinculo.outro_recurso_periodo.save()

        # Não deve levantar exceção
        try:
            service_vinculo._validar_recurso_ativo()
        except ValidacaoVinculoException:
            pytest.fail("Não deveria levantar exceção para recurso ativo")

    @pytest.mark.django_db
    def test_validar_recurso_inativo(self, service_vinculo):
        """Testa validação quando recurso está inativo"""
        service_vinculo.outro_recurso_periodo.ativo = False
        service_vinculo.outro_recurso_periodo.save()

        with pytest.raises(ValidacaoVinculoException) as excinfo:
            service_vinculo._validar_recurso_ativo()

        assert "recurso inativo" in str(excinfo.value)


class TestObterUnidade:
    """Testes para _obter_unidade"""

    @pytest.mark.django_db
    def test_obter_unidade_com_sucesso(self, service_vinculo):
        """Testa obtenção de unidade com sucesso"""
        unidade = UnidadeFactory.create()

        resultado = service_vinculo._obter_unidade(str(unidade.uuid))

        assert resultado == unidade

    @pytest.mark.django_db
    def test_obter_unidade_nao_encontrada(self, service_vinculo):
        """Testa exceção quando unidade não é encontrada"""
        import uuid
        unidade_uuid_inexistente = str(uuid.uuid4())

        with pytest.raises(UnidadeNaoEncontradaException) as excinfo:
            service_vinculo._obter_unidade(unidade_uuid_inexistente)

        assert "não encontrada" in str(excinfo.value)
        assert unidade_uuid_inexistente in str(excinfo.value)


class TestObterUnidades:
    """Testes para _obter_unidades"""

    @pytest.mark.django_db
    def test_obter_unidades_com_sucesso(self, service_vinculo, unidades_teste):
        """Testa obtenção de múltiplas unidades"""
        uuids = [str(u.uuid) for u in unidades_teste]

        resultado = service_vinculo._obter_unidades(uuids)

        assert len(resultado) == 3
        for unidade in unidades_teste:
            assert unidade in resultado

    @pytest.mark.django_db
    def test_obter_unidades_lista_vazia(self, service_vinculo):
        """Testa obtenção com lista vazia"""
        resultado = service_vinculo._obter_unidades([])

        assert resultado == []

    @pytest.mark.django_db
    def test_obter_unidades_parcialmente_encontradas(self, service_vinculo, unidades_teste):
        """Testa quando apenas algumas unidades são encontradas"""
        import uuid
        uuids = [str(unidades_teste[0].uuid), str(uuid.uuid4())]

        resultado = service_vinculo._obter_unidades(uuids)

        assert len(resultado) == 1
        assert unidades_teste[0] in resultado


class TestLimparRegistrosUnidade:
    """Testes para _limpar_registros_da_unidade_no_recurso_em_elaboracao"""

    @pytest.mark.django_db
    def test_limpar_registros_unidade(self, service_vinculo, periodo_paa):
        """Testa limpeza de registros da unidade"""
        paa = PaaFactory.create(
            periodo_paa=periodo_paa,
            status=PaaStatusEnum.EM_ELABORACAO.name
        )

        with patch.object(service_vinculo, '_remover_receitas_previstas_outro_recurso_periodo', return_value=2):
            with patch.object(service_vinculo, '_remover_prioridades_outro_recurso_periodo', return_value=1):
                resultado = service_vinculo._limpar_registros_da_unidade_no_recurso_em_elaboracao(paa)

        assert resultado['paa_uuid'] == str(paa.uuid)
        assert resultado['receitas_previstas_removidas'] == 2
        assert resultado['prioridades_afetadas'] == 1
        assert 'removido' in resultado['acao'].lower()

    @pytest.mark.django_db
    def test_limpar_registros_estrutura_retorno(self, service_vinculo, periodo_paa):
        """Testa estrutura do retorno"""
        paa = PaaFactory.create(periodo_paa=periodo_paa)

        with patch.object(service_vinculo, '_remover_receitas_previstas_outro_recurso_periodo', return_value=0):
            with patch.object(service_vinculo, '_remover_prioridades_outro_recurso_periodo', return_value=0):
                resultado = service_vinculo._limpar_registros_da_unidade_no_recurso_em_elaboracao(paa)

        assert 'paa_uuid' in resultado
        assert 'associacao' in resultado
        assert 'unidade' in resultado
        assert 'status' in resultado
        assert 'receitas_previstas_removidas' in resultado
        assert 'prioridades_afetadas' in resultado
        assert 'acao' in resultado


class TestObtemInformacaoParaConfirmacao:
    """Testes para obtem_informacao_para_confirmacao"""

    @pytest.mark.django_db
    def test_sem_necessidade_confirmacao(self, service_vinculo, periodo_paa):
        """Testa quando não há necessidade de confirmação"""
        unidades = UnidadeFactory.create_batch(2)
        paas = [PaaFactory.create(periodo_paa=periodo_paa)]

        resultado = service_vinculo.obtem_informacao_para_confirmacao(unidades, paas)

        assert resultado['requer_confirmacao'] is False
        assert resultado['mensagem'] is None

    @pytest.mark.django_db
    def test_confirmacao_paa_em_elaboracao_com_receitas(
        self,
        service_vinculo,
        paa_em_elaboracao
    ):
        """Testa confirmação necessária para PAA em elaboração com receitas"""

        # Mock para simular receitas existentes
        with patch.object(service_vinculo, '_paa_em_elaboracao', return_value=True):
            with patch.object(service_vinculo, '_receitas_previstas_outro_recurso_periodo_afetadas') as mock_receitas:
                mock_queryset = MagicMock()
                mock_queryset.exists.return_value = True
                mock_receitas.return_value = mock_queryset

                with patch.object(service_vinculo, '_prioridades_afetadas') as mock_prioridades:
                    mock_prioridades_queryset = MagicMock()
                    mock_prioridades_queryset.exists.return_value = True
                    mock_prioridades.return_value = mock_prioridades_queryset

                    resultado = service_vinculo.obtem_informacao_para_confirmacao(
                        [paa_em_elaboracao.associacao.unidade], [paa_em_elaboracao])

        assert resultado['requer_confirmacao'] is True, resultado

    @pytest.mark.django_db
    def test_confirmacao_paa_gerado(self, service_vinculo, paa_gerado):
        """Testa confirmação necessária para PAA gerado"""

        with patch.object(service_vinculo, '_paa_gerado', return_value=True):
            with patch.object(service_vinculo, '_paa_em_elaboracao', return_value=False):
                with patch.object(service_vinculo, '_paa_retificado', return_value=False):
                    resultado = service_vinculo.obtem_informacao_para_confirmacao(
                        [paa_gerado.associacao.unidade], [paa_gerado])

        assert resultado['requer_confirmacao'] is True
        assert 'mensagem' in resultado

    @pytest.mark.django_db
    def test_confirmacao_paa_retificado(self, service_vinculo, paa_retificado):
        """Testa confirmação necessária para PAA retificado"""

        with patch.object(service_vinculo, '_paa_gerado', return_value=False):
            with patch.object(service_vinculo, '_paa_em_elaboracao', return_value=False):
                with patch.object(service_vinculo, '_paa_retificado', return_value=True):
                    resultado = service_vinculo.obtem_informacao_para_confirmacao(
                        [paa_retificado.associacao.unidade], [paa_retificado])

        assert resultado['requer_confirmacao'] is True
        assert 'mensagem' in resultado


class TestValidarConfirmacaoVinculoUnidades:
    """Testes para validar_confirmacao_para_vinculo_unidades"""

    @pytest.mark.django_db
    def test_validar_sem_confirmacao_necessaria(self, service_vinculo, unidades_teste):
        """Testa validação quando não há necessidade de confirmação"""
        # Adiciona unidades ao recurso (não é "todas as unidades")
        service_vinculo.outro_recurso_periodo.unidades.add(unidades_teste[0])
        uuids = [str(u.uuid) for u in unidades_teste]
        # Não deve levantar exceção
        try:
            service_vinculo.validar_confirmacao_para_vinculo_unidades(uuids)
        except ConfirmacaoVinculoException:
            pytest.fail("Não deveria requerer confirmação")

    @pytest.mark.django_db
    def test_validar_confirmacao_necessaria(self, service_vinculo, periodo_paa, unidades_teste):
        """Testa validação quando confirmação é necessária"""
        # Recurso sem unidades (tinha todas)
        paa = PaaFactory.create(
            periodo_paa=periodo_paa,
            status=PaaStatusEnum.GERADO.name
        )
        with patch.object(service_vinculo, '_tinha_todas_unidades', return_value=True):
            with patch.object(service_vinculo, '_paas_afetados_em_elaboracao', return_value=[]):
                with patch.object(service_vinculo, '_paas_afetados_gerado_retificado', return_value=[paa]):
                    with patch.object(service_vinculo, 'obtem_informacao_para_confirmacao') as mock_obtem:
                        mock_obtem.return_value = {
                            'requer_confirmacao': True,
                            'mensagem': 'Confirmação necessária'
                        }
                        uuids = [str(u.uuid) for u in unidades_teste]
                        with pytest.raises(ConfirmacaoVinculoException):
                            service_vinculo.validar_confirmacao_para_vinculo_unidades(uuids)


class TestValidarConfirmacaoDesvinculoUnidades:
    """Testes para validar_confirmacao_para_desvinculo_unidades"""

    @pytest.mark.django_db
    def test_validar_desvinculo_sem_confirmacao(self, service_vinculo, unidades_teste):
        """Testa validação de desvínculo sem necessidade de confirmação"""
        uuids = [str(u.uuid) for u in unidades_teste]
        with patch.object(service_vinculo, '_paas_afetados_em_elaboracao', return_value=[]):
            with patch.object(service_vinculo, '_paas_afetados_gerado_retificado', return_value=[]):
                with patch.object(service_vinculo, 'obtem_informacao_para_confirmacao') as mock_obtem:
                    mock_obtem.return_value = {'requer_confirmacao': False, 'mensagem': None}
                    # Não deve levantar exceção
                    try:
                        service_vinculo.validar_confirmacao_para_desvinculo_unidades(uuids)
                    except ConfirmacaoVinculoException:
                        pytest.fail("Não deveria requerer confirmação")

    @pytest.mark.django_db
    def test_validar_desvinculo_confirmacao_necessaria(self, service_vinculo, unidades_teste):
        """Testa validação de desvínculo quando confirmação é necessária"""
        uuids = [str(u.uuid) for u in unidades_teste]
        with patch.object(service_vinculo, 'obtem_informacao_para_confirmacao') as mock_obtem:
            mock_obtem.return_value = {
                'requer_confirmacao': True,
                'mensagem': 'Confirmação necessária para desvínculo'
            }
            with pytest.raises(ConfirmacaoVinculoException) as excinfo:
                service_vinculo.validar_confirmacao_para_desvinculo_unidades(uuids)
            assert 'Confirmação necessária' in str(excinfo.value)


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
        service_vinculo.outro_recurso_periodo.unidades.add(*unidades_teste)
        resultado = service_vinculo.vincular_todas_unidades()
        assert resultado['sucesso'] is True
        assert 'habilitadas com sucesso' in resultado['mensagem']
        assert service_vinculo.outro_recurso_periodo.unidades.count() == 0


class TestVincularUnidades:
    """Testes para vincular_unidades"""

    @pytest.mark.django_db
    def test_vincular_unidades_sem_unidades(self, service_vinculo):
        """Testa vinculação sem unidades identificadas"""
        with pytest.raises(ValidacaoVinculoException) as excinfo:
            service_vinculo.vincular_unidades([])

        assert 'Nenhuma unidade' in str(excinfo.value)

    @pytest.mark.django_db
    def test_vincular_unidades_recurso_inativo(self, service_vinculo, unidades_teste):
        """Testa vinculação com recurso inativo"""
        service_vinculo.outro_recurso_periodo.ativo = False
        service_vinculo.outro_recurso_periodo.save()
        uuids = [str(u.uuid) for u in unidades_teste]
        with pytest.raises(ValidacaoVinculoException) as excinfo:
            service_vinculo.vincular_unidades(uuids)
        assert 'recurso inativo' in str(excinfo.value)

    @pytest.mark.django_db
    def test_vincular_unidades_com_sucesso(self, service_vinculo, unidades_teste):
        """Testa vinculação com sucesso"""
        uuids = [str(u.uuid) for u in unidades_teste]
        resultado = service_vinculo.vincular_unidades(uuids)
        assert resultado['sucesso'] is True
        assert 'vinculadas com sucesso' in resultado['mensagem']
        assert service_vinculo.outro_recurso_periodo.unidades.count() == 3

    @pytest.mark.django_db
    def test_vincular_unidades_processa_paas_elaboracao(
        self,
        service_vinculo,
        periodo_paa,
        unidades_teste
    ):
        """Testa processamento de PAAs em elaboração"""
        paa = PaaFactory.create(
            periodo_paa=periodo_paa,
            status=PaaStatusEnum.EM_ELABORACAO.name
        )

        with patch.object(service_vinculo, '_tinha_todas_unidades', return_value=True):
            with patch.object(service_vinculo, '_paas_afetados_em_elaboracao', return_value=[paa]):
                with patch.object(
                        service_vinculo, '_limpar_registros_da_unidade_no_recurso_em_elaboracao') as mock_limpar:
                    mock_limpar.return_value = {'paa_uuid': str(paa.uuid)}
                    uuids = [str(u.uuid) for u in unidades_teste]
                    resultado = service_vinculo.vincular_unidades(uuids)
                    assert resultado['sucesso'] is True

    @pytest.mark.django_db
    def test_vincular_unidades_mensagem_singular(self, service_vinculo):
        """Testa mensagem singular para uma unidade"""
        unidade = UnidadeFactory.create()
        resultado = service_vinculo.vincular_unidades([str(unidade.uuid)])
        assert 'Unidade vinculada com sucesso!' in resultado['mensagem']


class TestDesvincularUnidades:
    """Testes para desvincular_unidades"""

    @pytest.mark.django_db
    def test_desvincular_unidades_sem_unidades(self, service_vinculo):
        """Testa desvinculação sem unidades identificadas"""
        with pytest.raises(ValidacaoVinculoException) as excinfo:
            service_vinculo.desvincular_unidades([])

        assert 'Nenhuma unidade' in str(excinfo.value)

    @pytest.mark.django_db
    def test_desvincular_unidades_recurso_inativo(self, service_vinculo, unidades_teste):
        """Testa desvinculação com recurso inativo"""
        service_vinculo.outro_recurso_periodo.ativo = False
        service_vinculo.outro_recurso_periodo.save()
        uuids = [str(u.uuid) for u in unidades_teste]
        with pytest.raises(ValidacaoVinculoException) as excinfo:
            service_vinculo.desvincular_unidades(uuids)
        assert 'recurso inativo' in str(excinfo.value)

    @pytest.mark.django_db
    def test_desvincular_unidades_com_sucesso(self, service_vinculo, unidades_teste):
        """Testa desvinculação com sucesso"""
        service_vinculo.outro_recurso_periodo.unidades.add(*unidades_teste)
        uuids = [str(unidades_teste[0].uuid)]
        resultado = service_vinculo.desvincular_unidades(uuids)
        assert resultado['sucesso'] is True
        assert 'desvinculada com sucesso' in resultado['mensagem']
        assert service_vinculo.outro_recurso_periodo.unidades.count() == 2

    @pytest.mark.django_db
    def test_desvincular_unidades_processa_paas_elaboracao(
        self,
        service_vinculo,
        periodo_paa,
        unidades_teste
    ):
        """Testa processamento de PAAs em elaboração no desvínculo"""
        service_vinculo.outro_recurso_periodo.unidades.add(*unidades_teste)

        paa = PaaFactory.create(
            periodo_paa=periodo_paa,
            status=PaaStatusEnum.EM_ELABORACAO.name
        )
        with patch.object(service_vinculo, '_paas_afetados_em_elaboracao', return_value=[paa]):
            with patch.object(service_vinculo, '_limpar_registros_da_unidade_no_recurso_em_elaboracao') as mock_limpar:
                mock_limpar.return_value = {'paa_uuid': str(paa.uuid)}
                uuids = [str(unidades_teste[0].uuid)]
                resultado = service_vinculo.desvincular_unidades(uuids)

                assert resultado['sucesso'] is True

    @pytest.mark.django_db
    def test_desvincular_unidades_mensagem_plural(self, service_vinculo, unidades_teste):
        """Testa mensagem plural para múltiplas unidades"""
        service_vinculo.outro_recurso_periodo.unidades.add(*unidades_teste)

        uuids = [str(u.uuid) for u in unidades_teste[:2]]
        resultado = service_vinculo.desvincular_unidades(uuids)

        assert 'Unidades desvinculadas com sucesso!' in resultado['mensagem']
