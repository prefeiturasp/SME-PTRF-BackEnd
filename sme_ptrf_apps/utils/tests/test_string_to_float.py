from sme_ptrf_apps.utils.string_to_float import string_to_float


class TestStringToFloat:
    def test_virgula_como_separador_decimal(self):
        assert string_to_float("12,34") == 12.34

    def test_ponto_como_separador_de_milhar_e_virgula_decimal(self):
        assert string_to_float("1.234,56") == 1234.56

    def test_inteiro_sem_separadores(self):
        assert string_to_float("1234") == 1234.0

    def test_zero_virgula(self):
        assert string_to_float("0,99") == 0.99

    def test_ponto_como_separador_de_milhar_sem_decimal(self):
        assert string_to_float("1.000") == 1000.0

    def test_multiplos_separadores_de_milhar(self):
        assert string_to_float("1.000.000,00") == 1000000.0

    def test_retorna_tipo_float(self):
        assert isinstance(string_to_float("1,5"), float)
