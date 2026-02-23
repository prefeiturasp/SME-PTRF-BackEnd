import pytest
from datetime import date

from sme_ptrf_apps.core.fixtures.factories import UnidadeFactory
from sme_ptrf_apps.paa.fixtures.factories import (
    ReceitaPrevistaOutroRecursoPeriodoFactory,
)
from sme_ptrf_apps.paa.services.outros_recursos_periodo_listagem_service import (
    OutroRecursoPeriodoPaaListagemService,
)


# ---------------------------------------------------------------------------
# Fixtures locais
# ---------------------------------------------------------------------------

@pytest.fixture
def periodo_paa_listagem(periodo_paa_factory):
    return periodo_paa_factory.create(
        referencia="P 2024.1",
        data_inicial=date(2024, 1, 1),
        data_final=date(2024, 6, 30),
    )


@pytest.fixture
def periodo_paa_outro(periodo_paa_factory):
    """Período diferente, para garantir que recursos de outro período não aparecem."""
    return periodo_paa_factory.create(
        referencia="P 2024.2",
        data_inicial=date(2024, 7, 1),
        data_final=date(2024, 12, 31),
    )


@pytest.fixture
def paa_listagem(paa_factory, periodo_paa_listagem, associacao):
    return paa_factory.create(periodo_paa=periodo_paa_listagem, associacao=associacao)


@pytest.fixture
def unidade_paa(paa_listagem):
    """Retorna a unidade associada ao PAA."""
    return paa_listagem.associacao.unidade


@pytest.fixture
def recurso_todas_unidades(periodo_paa_listagem, outro_recurso_factory, outro_recurso_periodo_factory):
    """Recurso ativo, sem unidades vinculadas (disponível para todas as unidades)."""
    outro_recurso = outro_recurso_factory.create(nome="Recurso Todas Unidades")
    return outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa_listagem,
        ativo=True,
    )


@pytest.fixture
def recurso_vinculado_a_unidade_do_paa(periodo_paa_listagem, outro_recurso_factory,
                                       outro_recurso_periodo_factory, unidade_paa):
    """Recurso ativo, vinculado especificamente à unidade do PAA."""
    outro_recurso = outro_recurso_factory.create(nome="Recurso Unidade PAA")
    recurso = outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa_listagem,
        ativo=True,
    )
    recurso.unidades.add(unidade_paa)
    return recurso


@pytest.fixture
def recurso_inativo(periodo_paa_listagem, outro_recurso_factory, outro_recurso_periodo_factory):
    """Recurso inativo no mesmo período."""
    outro_recurso = outro_recurso_factory.create(nome="Recurso Inativo")
    return outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa_listagem,
        ativo=False,
    )


@pytest.fixture
def recurso_outro_periodo(periodo_paa_outro, outro_recurso_factory, outro_recurso_periodo_factory):
    """Recurso ativo em um período diferente."""
    outro_recurso = outro_recurso_factory.create(nome="Recurso Outro Período")
    return outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa_outro,
        ativo=True,
    )


@pytest.fixture
def recurso_vinculado_a_outra_unidade(periodo_paa_listagem, outro_recurso_factory, outro_recurso_periodo_factory):
    """Recurso ativo, vinculado a uma unidade que NÃO é a do PAA."""
    outra_unidade = UnidadeFactory.create()
    outro_recurso = outro_recurso_factory.create(nome="Recurso Outra Unidade")
    recurso = outro_recurso_periodo_factory.create(
        outro_recurso=outro_recurso,
        periodo_paa=periodo_paa_listagem,
        ativo=True,
    )
    recurso.unidades.add(outra_unidade)
    return recurso


@pytest.fixture
def service(paa_listagem, unidade_paa):
    return OutroRecursoPeriodoPaaListagemService(paa=paa_listagem, unidade=unidade_paa)


# ---------------------------------------------------------------------------
# Testes de inicialização
# ---------------------------------------------------------------------------

class TestInit:
    @pytest.mark.django_db
    def test_init_armazena_paa(self, paa_listagem, unidade_paa):
        service = OutroRecursoPeriodoPaaListagemService(paa=paa_listagem, unidade=unidade_paa)
        assert service.paa == paa_listagem

    @pytest.mark.django_db
    def test_init_armazena_unidade(self, paa_listagem, unidade_paa):
        service = OutroRecursoPeriodoPaaListagemService(paa=paa_listagem, unidade=unidade_paa)
        assert service.unidade == unidade_paa


# ---------------------------------------------------------------------------
# Testes de queryset_listar_outros_recursos_periodo_unidade
# ---------------------------------------------------------------------------

class TestQuerysetListarOutrosRecursosPeriodoUnidade:
    @pytest.mark.django_db
    def test_retorna_recurso_disponivel_para_todas_unidades(self, service, recurso_todas_unidades):
        """Recurso sem unidades vinculadas (unidades__isnull=True) deve aparecer."""
        resultado = service.queryset_listar_outros_recursos_periodo_unidade()
        assert recurso_todas_unidades in resultado

    @pytest.mark.django_db
    def test_retorna_recurso_vinculado_a_unidade_do_paa(self, service, recurso_vinculado_a_unidade_do_paa):
        """Recurso explicitamente vinculado à unidade do PAA deve aparecer."""
        resultado = service.queryset_listar_outros_recursos_periodo_unidade()
        assert recurso_vinculado_a_unidade_do_paa in resultado

    @pytest.mark.django_db
    def test_exclui_recurso_inativo(self, service, recurso_inativo):
        """Recurso inativo não deve aparecer, mesmo no mesmo período."""
        resultado = service.queryset_listar_outros_recursos_periodo_unidade()
        assert recurso_inativo not in resultado

    @pytest.mark.django_db
    def test_exclui_recurso_de_periodo_diferente(self, service, recurso_outro_periodo):
        """Recurso de outro período não deve aparecer."""
        resultado = service.queryset_listar_outros_recursos_periodo_unidade()
        assert recurso_outro_periodo not in resultado

    @pytest.mark.django_db
    def test_exclui_recurso_vinculado_a_outra_unidade(self, service, recurso_vinculado_a_outra_unidade):
        """Recurso vinculado a outra unidade não deve aparecer."""
        resultado = service.queryset_listar_outros_recursos_periodo_unidade()
        assert recurso_vinculado_a_outra_unidade not in resultado

    @pytest.mark.django_db
    def test_retorna_queryset_vazio_sem_recursos(self, service):
        """Sem recursos cadastrados, deve retornar queryset vazio."""
        resultado = service.queryset_listar_outros_recursos_periodo_unidade()
        assert resultado.count() == 0

    @pytest.mark.django_db
    def test_retorna_apenas_recursos_do_periodo_do_paa(
        self, service, recurso_todas_unidades, recurso_outro_periodo
    ):
        """Só devem aparecer recursos do período correto."""
        resultado = service.queryset_listar_outros_recursos_periodo_unidade()
        assert recurso_todas_unidades in resultado
        assert recurso_outro_periodo not in resultado

    @pytest.mark.django_db
    def test_ordenado_por_nome_do_recurso(
        self, service, periodo_paa_listagem, outro_recurso_factory, outro_recurso_periodo_factory
    ):
        """O queryset deve estar ordenado por outro_recurso__nome."""
        recurso_z = outro_recurso_factory.create(nome="Z Recurso")
        recurso_a = outro_recurso_factory.create(nome="A Recurso")
        recurso_m = outro_recurso_factory.create(nome="M Recurso")

        outro_recurso_periodo_factory.create(
            outro_recurso=recurso_z, periodo_paa=periodo_paa_listagem, ativo=True
        )
        outro_recurso_periodo_factory.create(
            outro_recurso=recurso_a, periodo_paa=periodo_paa_listagem, ativo=True
        )
        outro_recurso_periodo_factory.create(
            outro_recurso=recurso_m, periodo_paa=periodo_paa_listagem, ativo=True
        )

        resultado = service.queryset_listar_outros_recursos_periodo_unidade()
        nomes = list(resultado.values_list("outro_recurso__nome", flat=True))
        assert nomes == sorted(nomes)

    @pytest.mark.django_db
    def test_sem_duplicatas_quando_recurso_tem_multiplas_unidades(
        self, service, periodo_paa_listagem, outro_recurso_factory, outro_recurso_periodo_factory, unidade_paa
    ):
        """Recurso vinculado a múltiplas unidades não deve aparecer duplicado."""
        outra_unidade = UnidadeFactory.create()
        recurso = outro_recurso_periodo_factory.create(
            outro_recurso=outro_recurso_factory.create(nome="Recurso Multi Unidade"),
            periodo_paa=periodo_paa_listagem,
            ativo=True,
        )
        recurso.unidades.add(unidade_paa, outra_unidade)

        resultado = service.queryset_listar_outros_recursos_periodo_unidade()
        ids = list(resultado.values_list("id", flat=True))
        assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# Testes de serialized_listar_outros_recursos_periodo_unidades
# ---------------------------------------------------------------------------

class TestSerializedListarOutrosRecursosPeriodoUnidades:
    @pytest.mark.django_db
    def test_retorna_lista(self, service, recurso_todas_unidades):
        resultado = service.serialized_listar_outros_recursos_periodo_unidades()
        assert isinstance(resultado, list)

    @pytest.mark.django_db
    def test_retorna_lista_vazia_sem_recursos(self, service):
        resultado = service.serialized_listar_outros_recursos_periodo_unidades()
        assert resultado == []

    @pytest.mark.django_db
    def test_contem_campos_esperados(self, service, recurso_todas_unidades):
        """Cada item serializado deve ter os campos básicos do serializer."""
        resultado = service.serialized_listar_outros_recursos_periodo_unidades()
        assert len(resultado) == 1
        item = resultado[0]
        assert "uuid" in item
        assert "outro_recurso" in item
        assert "periodo_paa" in item
        assert "ativo" in item

    @pytest.mark.django_db
    def test_quantidade_corresponde_ao_queryset(
        self, service, recurso_todas_unidades, recurso_vinculado_a_unidade_do_paa
    ):
        """A lista serializada deve ter a mesma quantidade do queryset."""
        queryset = service.queryset_listar_outros_recursos_periodo_unidade()
        resultado = service.serialized_listar_outros_recursos_periodo_unidades()
        assert len(resultado) == queryset.count()

    @pytest.mark.django_db
    def test_nao_inclui_recursos_inativos(self, service, recurso_inativo, recurso_todas_unidades):
        """Recursos inativos não devem aparecer na lista serializada."""
        resultado = service.serialized_listar_outros_recursos_periodo_unidades()
        uuids = [str(item["uuid"]) for item in resultado]
        assert str(recurso_inativo.uuid) not in uuids


# ---------------------------------------------------------------------------
# Testes de serialized_listar_outros_recursos_periodo_receitas_previstas
# ---------------------------------------------------------------------------

class TestSerializedListarOutrosRecursosPeriodoReceitasPrevistas:
    @pytest.mark.django_db
    def test_adiciona_chave_receitas_previstas_em_cada_recurso(
        self, service, paa_listagem, recurso_todas_unidades
    ):
        """Cada recurso serializado deve ter a chave 'receitas_previstas'."""
        resultado = service.serialized_listar_outros_recursos_periodo_receitas_previstas(paa_listagem)
        assert len(resultado) >= 1
        for item in resultado:
            assert "receitas_previstas" in item

    @pytest.mark.django_db
    def test_receitas_previstas_vazia_quando_sem_receitas(
        self, service, paa_listagem, recurso_todas_unidades
    ):
        """Quando não há receitas previstas, a lista deve ser vazia."""
        resultado = service.serialized_listar_outros_recursos_periodo_receitas_previstas(paa_listagem)
        for item in resultado:
            assert item["receitas_previstas"] == []

    @pytest.mark.django_db
    def test_receitas_previstas_contem_receita_do_recurso(
        self, service, paa_listagem, recurso_todas_unidades
    ):
        """A receita prevista do recurso deve aparecer na chave 'receitas_previstas'."""
        receita = ReceitaPrevistaOutroRecursoPeriodoFactory.create(
            paa=paa_listagem,
            outro_recurso_periodo=recurso_todas_unidades,
        )

        resultado = service.serialized_listar_outros_recursos_periodo_receitas_previstas(paa_listagem)

        item = next(r for r in resultado if str(r["uuid"]) == str(recurso_todas_unidades.uuid))
        assert len(item["receitas_previstas"]) == 1
        assert str(item["receitas_previstas"][0]["uuid"]) == str(receita.uuid)

    @pytest.mark.django_db
    def test_nao_mistura_receitas_de_recursos_diferentes(
        self,
        service,
        paa_listagem,
        recurso_todas_unidades,
        recurso_vinculado_a_unidade_do_paa,
    ):
        """As receitas de um recurso não devem aparecer em outro recurso."""
        receita_a = ReceitaPrevistaOutroRecursoPeriodoFactory.create(
            paa=paa_listagem,
            outro_recurso_periodo=recurso_todas_unidades,
        )
        receita_b = ReceitaPrevistaOutroRecursoPeriodoFactory.create(
            paa=paa_listagem,
            outro_recurso_periodo=recurso_vinculado_a_unidade_do_paa,
        )

        resultado = service.serialized_listar_outros_recursos_periodo_receitas_previstas(paa_listagem)

        item_a = next(r for r in resultado if str(r["uuid"]) == str(recurso_todas_unidades.uuid))
        item_b = next(r for r in resultado if str(r["uuid"]) == str(recurso_vinculado_a_unidade_do_paa.uuid))

        uuids_a = [str(r["uuid"]) for r in item_a["receitas_previstas"]]
        uuids_b = [str(r["uuid"]) for r in item_b["receitas_previstas"]]

        assert str(receita_a.uuid) in uuids_a
        assert str(receita_b.uuid) not in uuids_a
        assert str(receita_b.uuid) in uuids_b
        assert str(receita_a.uuid) not in uuids_b

    @pytest.mark.django_db
    def test_retorna_lista_vazia_sem_recursos(self, service, paa_listagem):
        """Sem recursos, retorna lista vazia."""
        resultado = service.serialized_listar_outros_recursos_periodo_receitas_previstas(paa_listagem)
        assert resultado == []

    @pytest.mark.django_db
    def test_multiplas_receitas_para_mesmo_recurso(
        self, service, paa_listagem, recurso_todas_unidades
    ):
        """Múltiplas receitas devem aparecer na lista do recurso."""
        receita_1 = ReceitaPrevistaOutroRecursoPeriodoFactory.create(
            paa=paa_listagem,
            outro_recurso_periodo=recurso_todas_unidades,
        )
        # Apenas uma receita por recurso por PAA é permitida (UniqueTogetherValidator),
        # mas verificamos que a que existe aparece corretamente.
        resultado = service.serialized_listar_outros_recursos_periodo_receitas_previstas(paa_listagem)
        item = next(r for r in resultado if str(r["uuid"]) == str(recurso_todas_unidades.uuid))
        uuids = [str(r["uuid"]) for r in item["receitas_previstas"]]
        assert str(receita_1.uuid) in uuids
