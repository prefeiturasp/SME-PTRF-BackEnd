import pytest

from sme_ptrf_apps.paa.admin_inlines import PaaTabelasMixin

pytestmark = pytest.mark.django_db


class TestMetodosEstaticos:

    def test_check_boolean_verdadeiro(self):
        assert PaaTabelasMixin._check_boolean(True) == '✓'

    def test_check_boolean_falso(self):
        assert PaaTabelasMixin._check_boolean(False) == '✗'

    def test_table_sem_rows_exibe_nenhum_registro(self):
        html = PaaTabelasMixin._table(['Coluna A', 'Coluna B'], [])
        assert 'Nenhum registro.' in html
        assert 'Coluna A' in html
        assert 'Coluna B' in html

    def test_table_com_rows_exibe_conteudo(self):
        html = PaaTabelasMixin._table(['Nome'], [['Valor Teste']])
        assert 'Valor Teste' in html
        assert 'Nenhum registro.' not in html

    def test_table_escapa_html_nos_cabecalhos(self):
        html = PaaTabelasMixin._table(['<script>xss</script>'], [])
        assert '<script>' not in html
        assert '&lt;script&gt;' in html

    def test_table_escapa_html_nas_celulas(self):
        html = PaaTabelasMixin._table(['Col'], [['<b>injeção</b>']])
        assert '<b>injeção</b>' not in html

    def test_table_celula_none_exibe_tracinho(self):
        html = PaaTabelasMixin._table(['Col'], [[None]])
        assert '-' in html

    def test_table_retorna_mark_safe(self):
        from django.utils.safestring import SafeData
        resultado = PaaTabelasMixin._table(['Col'], [])
        assert isinstance(resultado, SafeData)


class TestTabelaObjetivos:

    def test_sem_obj_retorna_tabela_vazia(self, paa_admin):
        html = paa_admin.tabela_objetivos(None)
        assert 'Nenhum registro.' in html

    def test_obj_sem_pk_retorna_tabela_vazia(self, paa_admin):
        obj = type('Paa', (), {'pk': None})()
        html = paa_admin.tabela_objetivos(obj)
        assert 'Nenhum registro.' in html

    def test_com_objetivo_exibe_nome(self, paa_admin, paa, objetivo_paa_factory):
        objetivo = objetivo_paa_factory(paa=paa)
        paa.objetivos.add(objetivo)
        html = paa_admin.tabela_objetivos(paa)
        assert objetivo.nome in html

    def test_sem_objetivos_retorna_tabela_vazia(self, paa_admin, paa):
        html = paa_admin.tabela_objetivos(paa)
        assert 'Nenhum registro.' in html


class TestTabelaAtividadesEstatutarias:

    def test_sem_obj_retorna_tabela_vazia(self, paa_admin):
        html = paa_admin.tabela_atividades_estatutarias(None)
        assert 'Nenhum registro.' in html

    def test_com_atividade_exibe_registro(
        self, paa_admin, paa, atividade_estatutaria_factory, atividade_estatutaria_paa_factory
    ):
        atividade = atividade_estatutaria_factory.create(paa=paa)
        atividade_estatutaria_paa_factory(paa=paa, atividade_estatutaria=atividade)
        html = paa_admin.tabela_atividades_estatutarias(paa)
        assert str(atividade) in html

    def test_sem_atividades_retorna_tabela_vazia(self, paa_admin, paa):
        html = paa_admin.tabela_atividades_estatutarias(paa)
        assert 'Nenhum registro.' in html


class TestTabelaReceitasPtrf:

    def test_sem_obj_retorna_tabela_vazia(self, paa_admin):
        html = paa_admin.tabela_receitas_ptrf(None)
        assert 'Nenhum registro.' in html

    def test_com_receita_exibe_registro(self, paa_admin, paa, receita_prevista_paa_factory):
        receita_prevista_paa_factory(paa=paa)
        html = paa_admin.tabela_receitas_ptrf(paa)
        assert 'Nenhum registro.' not in html

    def test_sem_receitas_retorna_tabela_vazia(self, paa_admin, paa):
        html = paa_admin.tabela_receitas_ptrf(paa)
        assert 'Nenhum registro.' in html


class TestTabelaReceitasPdde:

    def test_sem_obj_retorna_tabela_vazia(self, paa_admin):
        html = paa_admin.tabela_receitas_pdde(None)
        assert 'Nenhum registro.' in html

    def test_com_receita_exibe_registro(self, paa_admin, paa, receita_prevista_pdde_factory):
        receita_prevista_pdde_factory(paa=paa)
        html = paa_admin.tabela_receitas_pdde(paa)
        assert 'Nenhum registro.' not in html

    def test_sem_receitas_retorna_tabela_vazia(self, paa_admin, paa):
        html = paa_admin.tabela_receitas_pdde(paa)
        assert 'Nenhum registro.' in html


class TestTabelaRecursosProprios:

    def test_sem_obj_retorna_tabela_vazia(self, paa_admin):
        html = paa_admin.tabela_recursos_proprios(None)
        assert 'Nenhum registro.' in html

    def test_com_recurso_exibe_registro(
        self, paa_admin, paa, recurso_proprio_paa_factory, fonte_recurso_paa_factory
    ):
        fonte = fonte_recurso_paa_factory.create()
        recurso_proprio_paa_factory.create(paa=paa, fonte_recurso=fonte, associacao=paa.associacao)
        html = paa_admin.tabela_recursos_proprios(paa)
        assert 'Nenhum registro.' not in html

    def test_sem_recursos_retorna_tabela_vazia(self, paa_admin, paa):
        html = paa_admin.tabela_recursos_proprios(paa)
        assert 'Nenhum registro.' in html


class TestTabelaOutrosRecursosPeriodo:

    def test_sem_obj_retorna_tabela_vazia(self, paa_admin):
        html = paa_admin.tabela_outros_recursos_periodo(None)
        assert 'Nenhum registro.' in html

    def test_com_receita_exibe_registro(
        self, paa_admin, paa, receita_prevista_outro_recurso_periodo_factory
    ):
        receita_prevista_outro_recurso_periodo_factory.create(paa=paa)
        html = paa_admin.tabela_outros_recursos_periodo(paa)
        assert 'Nenhum registro.' not in html

    def test_sem_receitas_retorna_tabela_vazia(self, paa_admin, paa):
        html = paa_admin.tabela_outros_recursos_periodo(paa)
        assert 'Nenhum registro.' in html


class TestTabelaDocumentos:

    def test_sem_obj_retorna_tabela_vazia(self, paa_admin):
        html = paa_admin.tabela_documentos(None)
        assert 'Nenhum registro.' in html

    def test_com_documento_exibe_registro(self, paa_admin, paa, documento_paa_factory):
        documento_paa_factory.create(paa=paa)
        html = paa_admin.tabela_documentos(paa)
        assert 'Nenhum registro.' not in html

    def test_sem_documentos_retorna_tabela_vazia(self, paa_admin, paa):
        html = paa_admin.tabela_documentos(paa)
        assert 'Nenhum registro.' in html


class TestTabelaAtas:

    def test_sem_obj_retorna_tabela_vazia(self, paa_admin):
        html = paa_admin.tabela_atas(None)
        assert 'Nenhum registro.' in html

    def test_com_ata_exibe_registro(self, paa_admin, paa, ata_paa_factory):
        ata_paa_factory.create(paa=paa)
        html = paa_admin.tabela_atas(paa)
        assert 'Nenhum registro.' not in html

    def test_sem_atas_retorna_tabela_vazia(self, paa_admin, paa):
        html = paa_admin.tabela_atas(paa)
        assert 'Nenhum registro.' in html


class TestTabelaPrioridades:

    def test_sem_obj_retorna_tabela_vazia(self, paa_admin):
        html = paa_admin.tabela_prioridades(None)
        assert 'Nenhum registro.' in html

    def test_com_prioridade_exibe_registro(self, paa_admin, paa, prioridade_paa_factory):
        prioridade_paa_factory(paa=paa)
        html = paa_admin.tabela_prioridades(paa)
        assert 'Nenhum registro.' not in html

    def test_sem_prioridades_retorna_tabela_vazia(self, paa_admin, paa):
        html = paa_admin.tabela_prioridades(paa)
        assert 'Nenhum registro.' in html
