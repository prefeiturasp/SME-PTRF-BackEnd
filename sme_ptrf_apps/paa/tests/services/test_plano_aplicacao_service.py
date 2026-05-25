import pytest
from unittest.mock import patch, MagicMock

from sme_ptrf_apps.paa.services.plano_aplicacao_service import PlanoAplicacaoService


# ---------------------------------------------------------------------------
# Fixtures locais
# ---------------------------------------------------------------------------

@pytest.fixture
def paa(paa_factory, periodo_paa_1, associacao):
    return paa_factory.create(periodo_paa=periodo_paa_1, associacao=associacao)


@pytest.fixture
def service(paa):
    return PlanoAplicacaoService(paa=paa)


@pytest.fixture
def service_com_usuario(paa):
    usuario = MagicMock()
    usuario.username = 'testuser'
    return PlanoAplicacaoService(paa=paa, usuario=usuario)


def _make_prioridade(prioridade: bool, recurso: str, valor_total=None) -> dict:
    """Fábrica de dicts que imitam a saída do PrioridadePaaListSerializer."""
    return {
        'prioridade': prioridade,
        'recurso': recurso,
        'valor_total': valor_total,
    }


# ---------------------------------------------------------------------------
# _obter_alteracoes
# ---------------------------------------------------------------------------

_PATCH_RETIFICACAO = 'sme_ptrf_apps.paa.services.retificacao_paa_service.RetificacaoPaaService'


@pytest.mark.django_db
class TestObterAlteracoes:
    def test_retorna_dict_do_service_retificacao(self, service):
        alteracoes_esperadas = {'campo_a': ['antes', 'depois']}
        with patch(_PATCH_RETIFICACAO) as MockRetificacao:
            MockRetificacao.return_value.identificar_alteracoes.return_value = alteracoes_esperadas

            resultado = service._obter_alteracoes()

        assert resultado == alteracoes_esperadas

    def test_retorna_dict_vazio_quando_retificacao_lanca_excecao(self, service):
        with patch(_PATCH_RETIFICACAO) as MockRetificacao:
            MockRetificacao.return_value.identificar_alteracoes.side_effect = Exception('falha')

            resultado = service._obter_alteracoes()

        assert resultado == {}

    def test_resultado_e_cacheado_entre_chamadas(self, service):
        alteracoes = {'x': ['a', 'b']}
        with patch(_PATCH_RETIFICACAO) as MockRetificacao:
            MockRetificacao.return_value.identificar_alteracoes.return_value = alteracoes

            primeiro = service._obter_alteracoes()
            segundo = service._obter_alteracoes()

        assert primeiro is segundo
        MockRetificacao.return_value.identificar_alteracoes.assert_called_once()

    def test_usa_usuario_passado_na_inicializacao(self, service_com_usuario):
        with patch(_PATCH_RETIFICACAO) as MockRetificacao:
            MockRetificacao.return_value.identificar_alteracoes.return_value = {}

            service_com_usuario._obter_alteracoes()

        MockRetificacao.assert_called_once_with(
            service_com_usuario.paa,
            service_com_usuario.usuario,
        )


# ---------------------------------------------------------------------------
# _construir_grupo
# ---------------------------------------------------------------------------

class TestConstruirGrupo:
    def test_estrutura_basica_do_retorno(self):
        service = PlanoAplicacaoService.__new__(PlanoAplicacaoService)
        itens = [{'key': 'item-1', 'valor_total': 100.0}]

        resultado = service._construir_grupo('meu-grupo', 'Meu Grupo', itens)

        assert resultado['key'] == 'meu-grupo'
        assert resultado['titulo'] == 'Meu Grupo'
        assert resultado['ehOutrosRecursos'] is False

    def test_eh_outros_recursos_propagado(self):
        service = PlanoAplicacaoService.__new__(PlanoAplicacaoService)

        resultado = service._construir_grupo('g', 'G', [], eh_outros_recursos=True)

        assert resultado['ehOutrosRecursos'] is True

    def test_adiciona_linha_de_total_ao_final(self):
        service = PlanoAplicacaoService.__new__(PlanoAplicacaoService)
        itens = [
            {'valor_total': 200.0},
            {'valor_total': 300.0},
        ]

        resultado = service._construir_grupo('g', 'G', itens)
        linha_total = resultado['dados'][-1]

        assert linha_total['isTotal'] is True
        assert linha_total['key'] == 'g-total'
        assert linha_total['valor_total'] == 500.0

    def test_total_correto_com_multiplos_itens(self):
        service = PlanoAplicacaoService.__new__(PlanoAplicacaoService)
        itens = [
            {'valor_total': 1000.0},
            {'valor_total': 250.5},
            {'valor_total': 749.5},
        ]

        resultado = service._construir_grupo('g', 'G', itens)
        total = resultado['dados'][-1]['valor_total']

        assert total == 2000.0

    def test_itens_originais_preservados_antes_do_total(self):
        service = PlanoAplicacaoService.__new__(PlanoAplicacaoService)
        itens = [
            {'valor_total': 10.0, 'id': 1},
            {'valor_total': 20.0, 'id': 2},
        ]

        resultado = service._construir_grupo('g', 'G', itens)

        assert resultado['dados'][0] == itens[0]
        assert resultado['dados'][1] == itens[1]
        assert len(resultado['dados']) == 3  # 2 itens + 1 total

    def test_total_ignora_itens_com_valor_none(self):
        service = PlanoAplicacaoService.__new__(PlanoAplicacaoService)
        itens = [
            {'valor_total': 100.0},
            {'valor_total': None},
            {'valor_total': 50.0},
        ]

        resultado = service._construir_grupo('g', 'G', itens)
        total = resultado['dados'][-1]['valor_total']

        assert total == 150.0

    def test_total_zero_quando_sem_itens(self):
        service = PlanoAplicacaoService.__new__(PlanoAplicacaoService)

        resultado = service._construir_grupo('g', 'G', [])
        total = resultado['dados'][-1]['valor_total']

        assert total == 0


# ---------------------------------------------------------------------------
# construir_plano_aplicacao
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestConstruirPlanoAplicacao:
    def _patch_prioridades(self, service, prioridades: list):
        """Utilitário para mockar _obter_prioridades_serializadas."""
        return patch.object(service, '_obter_prioridades_serializadas', return_value=prioridades)

    def test_retorna_lista_vazia_sem_prioridades(self, service):
        with self._patch_prioridades(service, []):
            resultado = service.construir_plano_aplicacao()

        assert resultado == []

    def test_cria_grupo_prioridades_ptrf(self, service):
        prioridades = [_make_prioridade(True, 'PTRF', 500.0)]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        keys = [g['key'] for g in resultado]
        assert 'prioridades-ptrf' in keys

    def test_cria_grupo_prioridades_pdde(self, service):
        prioridades = [_make_prioridade(True, 'PDDE', 300.0)]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        keys = [g['key'] for g in resultado]
        assert 'prioridades-pdde' in keys

    def test_cria_grupo_prioridades_outros_recursos_para_recurso_proprio(self, service):
        prioridades = [_make_prioridade(True, 'RECURSO_PROPRIO', 200.0)]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        keys = [g['key'] for g in resultado]
        assert 'prioridades-outros-recursos' in keys

    def test_cria_grupo_prioridades_outros_recursos_para_outro_recurso(self, service):
        prioridades = [_make_prioridade(True, 'OUTRO_RECURSO', 150.0)]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        keys = [g['key'] for g in resultado]
        assert 'prioridades-outros-recursos' in keys

    def test_cria_grupo_nao_prioridades_ptrf(self, service):
        prioridades = [_make_prioridade(False, 'PTRF', 100.0)]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        keys = [g['key'] for g in resultado]
        assert 'nao-prioridades-ptrf' in keys

    def test_cria_grupo_nao_prioridades_pdde(self, service):
        prioridades = [_make_prioridade(False, 'PDDE', 100.0)]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        keys = [g['key'] for g in resultado]
        assert 'nao-prioridades-pdde' in keys

    def test_cria_grupo_nao_prioridades_outros_recursos(self, service):
        prioridades = [_make_prioridade(False, 'RECURSO_PROPRIO', 100.0)]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        keys = [g['key'] for g in resultado]
        assert 'nao-prioridades-outros-recursos' in keys

    def test_omite_grupos_sem_itens(self, service):
        # Somente prioridades PTRF; nenhum outro grupo deve aparecer
        prioridades = [_make_prioridade(True, 'PTRF', 500.0)]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        keys = [g['key'] for g in resultado]
        assert 'prioridades-pdde' not in keys
        assert 'nao-prioridades-ptrf' not in keys

    def test_todos_os_seis_grupos_aparecem_quando_ha_itens(self, service):
        prioridades = [
            _make_prioridade(True, 'PTRF', 100.0),
            _make_prioridade(True, 'PDDE', 100.0),
            _make_prioridade(True, 'RECURSO_PROPRIO', 100.0),
            _make_prioridade(False, 'PTRF', 100.0),
            _make_prioridade(False, 'PDDE', 100.0),
            _make_prioridade(False, 'OUTRO_RECURSO', 100.0),
        ]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        assert len(resultado) == 6

    def test_grupo_contem_somente_itens_do_seu_recurso(self, service):
        prioridades = [
            _make_prioridade(True, 'PTRF', 100.0),
            _make_prioridade(True, 'PDDE', 200.0),
        ]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        grupo_ptrf = next(g for g in resultado if g['key'] == 'prioridades-ptrf')
        # dados = [item, linha_total]
        itens_do_grupo = [d for d in grupo_ptrf['dados'] if not d.get('isTotal')]
        assert all(p['recurso'] == 'PTRF' for p in itens_do_grupo)

    def test_grupo_outros_recursos_tem_flag_eh_outros_recursos(self, service):
        prioridades = [_make_prioridade(True, 'RECURSO_PROPRIO', 100.0)]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        grupo = next(g for g in resultado if g['key'] == 'prioridades-outros-recursos')
        assert grupo['ehOutrosRecursos'] is True

    def test_grupos_ptrf_e_pdde_nao_tem_flag_eh_outros_recursos(self, service):
        prioridades = [
            _make_prioridade(True, 'PTRF', 100.0),
            _make_prioridade(True, 'PDDE', 100.0),
        ]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        for grupo in resultado:
            assert grupo['ehOutrosRecursos'] is False

    def test_valor_total_do_grupo_soma_itens(self, service):
        prioridades = [
            _make_prioridade(True, 'PTRF', 400.0),
            _make_prioridade(True, 'PTRF', 600.0),
        ]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        grupo_ptrf = next(g for g in resultado if g['key'] == 'prioridades-ptrf')
        linha_total = grupo_ptrf['dados'][-1]
        assert linha_total['isTotal'] is True
        assert linha_total['valor_total'] == 1000.0

    def test_ordem_dos_grupos_segue_definicao_de_grupos(self, service):
        prioridades = [
            _make_prioridade(True, 'PTRF', 10.0),
            _make_prioridade(True, 'PDDE', 10.0),
            _make_prioridade(True, 'RECURSO_PROPRIO', 10.0),
            _make_prioridade(False, 'PTRF', 10.0),
            _make_prioridade(False, 'PDDE', 10.0),
            _make_prioridade(False, 'OUTRO_RECURSO', 10.0),
        ]
        ordem_esperada = [
            'prioridades-ptrf',
            'prioridades-pdde',
            'prioridades-outros-recursos',
            'nao-prioridades-ptrf',
            'nao-prioridades-pdde',
            'nao-prioridades-outros-recursos',
        ]
        with self._patch_prioridades(service, prioridades):
            resultado = service.construir_plano_aplicacao()

        assert [g['key'] for g in resultado] == ordem_esperada
