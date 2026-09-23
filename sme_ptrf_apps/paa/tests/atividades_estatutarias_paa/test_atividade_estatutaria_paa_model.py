import pytest

from sme_ptrf_apps.paa.choices import StatusChoices
from sme_ptrf_apps.paa.models import AtividadeEstatutariaPaa

pytestmark = pytest.mark.django_db


class TestVerificarAtividadesEstatutariasSemDatas:
    def test_retorna_false_quando_nao_ha_atividades_estatutarias_ativas(self, paa):
        assert AtividadeEstatutariaPaa.verificar_atividades_estatutarias_sem_datas(paa) is False

    def test_retorna_false_quando_so_ha_atividades_inativas(self, paa, atividade_estatutaria_factory):
        atividade_estatutaria_factory.create(status=StatusChoices.INATIVO, paa=None)

        assert AtividadeEstatutariaPaa.verificar_atividades_estatutarias_sem_datas(paa) is False

    def test_retorna_true_quando_atividade_ativa_nao_tem_data_registrada(self, paa, atividade_estatutaria_factory):
        atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=None)

        assert AtividadeEstatutariaPaa.verificar_atividades_estatutarias_sem_datas(paa) is True

    def test_retorna_false_quando_atividade_ativa_ja_tem_data_registrada(
            self, paa, atividade_estatutaria_factory, atividade_estatutaria_paa_factory):
        atividade_estatutaria = atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=None)
        atividade_estatutaria_paa_factory.create(paa=paa, atividade_estatutaria=atividade_estatutaria)

        assert AtividadeEstatutariaPaa.verificar_atividades_estatutarias_sem_datas(paa) is False

    def test_retorna_true_quando_apenas_parte_das_atividades_ativas_tem_data(
            self, paa, atividade_estatutaria_factory, atividade_estatutaria_paa_factory):
        atividade_com_data = atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=None)
        atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=None)
        atividade_estatutaria_paa_factory.create(paa=paa, atividade_estatutaria=atividade_com_data)

        assert AtividadeEstatutariaPaa.verificar_atividades_estatutarias_sem_datas(paa) is True

    def test_considera_atividade_especifica_do_paa(
            self, paa, atividade_estatutaria_factory, atividade_estatutaria_paa_factory):
        atividade_estatutaria = atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=paa)

        assert AtividadeEstatutariaPaa.verificar_atividades_estatutarias_sem_datas(paa) is True

        atividade_estatutaria_paa_factory.create(paa=paa, atividade_estatutaria=atividade_estatutaria)

        assert AtividadeEstatutariaPaa.verificar_atividades_estatutarias_sem_datas(paa) is False

    def test_nao_considera_atividade_ativa_de_outro_paa(self, paa, paa_factory, atividade_estatutaria_factory):
        outro_paa = paa_factory.create()
        atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=outro_paa)

        assert AtividadeEstatutariaPaa.verificar_atividades_estatutarias_sem_datas(paa) is False

    def test_nao_considera_data_registrada_para_outro_paa(
            self, paa, paa_factory, atividade_estatutaria_factory, atividade_estatutaria_paa_factory):
        outro_paa = paa_factory.create()
        atividade_estatutaria = atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=None)
        atividade_estatutaria_paa_factory.create(paa=outro_paa, atividade_estatutaria=atividade_estatutaria)

        assert AtividadeEstatutariaPaa.verificar_atividades_estatutarias_sem_datas(paa) is True


class TestTodasDatasPreenchidas:
    def test_retorna_true_quando_nao_ha_atividades_estatutarias_ativas(self, paa):
        assert AtividadeEstatutariaPaa.todas_datas_preenchidas(paa) is True

    def test_retorna_false_quando_existe_atividade_ativa_sem_data(self, paa, atividade_estatutaria_factory):
        atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=None)

        assert AtividadeEstatutariaPaa.todas_datas_preenchidas(paa) is False

    def test_retorna_true_quando_todas_as_atividades_ativas_tem_data(
            self, paa, atividade_estatutaria_factory, atividade_estatutaria_paa_factory):
        atividade_estatutaria = atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=None)
        atividade_estatutaria_paa_factory.create(paa=paa, atividade_estatutaria=atividade_estatutaria)

        assert AtividadeEstatutariaPaa.todas_datas_preenchidas(paa) is True

    def test_retorna_false_quando_apenas_parte_das_atividades_tem_data(
            self, paa, atividade_estatutaria_factory, atividade_estatutaria_paa_factory):
        atividade_com_data = atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=None)
        atividade_estatutaria_factory.create(status=StatusChoices.ATIVO, paa=None)
        atividade_estatutaria_paa_factory.create(paa=paa, atividade_estatutaria=atividade_com_data)

        assert AtividadeEstatutariaPaa.todas_datas_preenchidas(paa) is False

    def test_ignora_atividades_estatutarias_inativas(self, paa, atividade_estatutaria_factory):
        atividade_estatutaria_factory.create(status=StatusChoices.INATIVO, paa=None)

        assert AtividadeEstatutariaPaa.todas_datas_preenchidas(paa) is True
