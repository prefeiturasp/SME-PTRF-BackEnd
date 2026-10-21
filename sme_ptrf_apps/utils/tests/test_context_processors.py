from django.conf import settings

from sme_ptrf_apps.utils.context_processors import settings_context


class TestSettingsContext:
    def test_retorna_dict_com_chave_settings(self):
        result = settings_context(None)
        assert "settings" in result

    def test_value_e_o_objeto_settings_do_django(self):
        result = settings_context(None)
        assert result["settings"] is settings

    def test_request_nao_e_utilizado(self):
        result_none = settings_context(None)
        result_qualquer = settings_context("qualquer_coisa")
        assert result_none == result_qualquer
