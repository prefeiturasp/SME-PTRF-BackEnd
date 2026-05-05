import pytest

from sme_ptrf_apps.utils.numero_ordinal import formata_numero_ordinal


class TestFormataNumeroOrdinalUnidades:
    def test_primeira(self):
        assert formata_numero_ordinal(1) == "Primeira"

    def test_segunda(self):
        assert formata_numero_ordinal(2) == "Segunda"

    def test_terceira(self):
        assert formata_numero_ordinal(3) == "Terceira"

    def test_quarta(self):
        assert formata_numero_ordinal(4) == "Quarta"

    def test_quinta(self):
        assert formata_numero_ordinal(5) == "Quinta"

    def test_sexta(self):
        assert formata_numero_ordinal(6) == "Sexta"

    def test_setima(self):
        assert formata_numero_ordinal(7) == "Sétima"

    def test_oitava(self):
        assert formata_numero_ordinal(8) == "Oitava"

    def test_nona(self):
        assert formata_numero_ordinal(9) == "Nona"


class TestFormataNumeroOrdinalDecenas:
    def test_decima(self):
        assert formata_numero_ordinal(10) == "Décima"

    def test_vigesima(self):
        assert formata_numero_ordinal(20) == "Vigésima"

    def test_trigesima(self):
        assert formata_numero_ordinal(30) == "Trigésima"

    def test_quadragesima(self):
        assert formata_numero_ordinal(40) == "Quadragésima"


class TestFormataNumeroOrdinalComposto:
    def test_decima_primeira(self):
        assert formata_numero_ordinal(11) == "Décima primeira"

    def test_decima_quinta(self):
        assert formata_numero_ordinal(15) == "Décima quinta"

    def test_decima_nona(self):
        assert formata_numero_ordinal(19) == "Décima nona"

    def test_vigesima_primeira(self):
        assert formata_numero_ordinal(21) == "Vigésima primeira"

    def test_vigesima_quinta(self):
        assert formata_numero_ordinal(25) == "Vigésima quinta"

    def test_vigesima_nona(self):
        assert formata_numero_ordinal(29) == "Vigésima nona"

    def test_trigesima_primeira(self):
        assert formata_numero_ordinal(31) == "Trigésima primeira"

    def test_trigesima_quinta(self):
        assert formata_numero_ordinal(35) == "Trigésima quinta"

    def test_trigesima_nona(self):
        assert formata_numero_ordinal(39) == "Trigésima nona"

    def test_quadragesima_primeira(self):
        assert formata_numero_ordinal(41) == "Quadragésima primeira"

    def test_quadragesima_quinta(self):
        assert formata_numero_ordinal(45) == "Quadragésima quinta"

    def test_quadragesima_nona(self):
        assert formata_numero_ordinal(49) == "Quadragésima nona"


class TestFormataNumeroOrdinalLimites:
    def test_cinquenta_levanta_exception(self):
        with pytest.raises(Exception, match="só foi realizada até o número 49"):
            formata_numero_ordinal(50)

    def test_acima_de_cinquenta_levanta_exception(self):
        with pytest.raises(Exception):
            formata_numero_ordinal(100)

    def test_zero_retorna_mensagem_de_erro(self):
        resultado = formata_numero_ordinal(0)
        assert resultado.startswith("ocorreu um erro:")
