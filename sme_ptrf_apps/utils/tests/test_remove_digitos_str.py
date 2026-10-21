from sme_ptrf_apps.utils.remove_digitos_str import remove_digitos


class TestRemoveDigitos:
    def test_remove_digitos_do_meio(self):
        assert remove_digitos("teste 123") == "teste "

    def test_string_so_com_digitos_retorna_vazia(self):
        assert remove_digitos("12345") == ""

    def test_string_sem_digitos_retorna_igual(self):
        assert remove_digitos("abc") == "abc"

    def test_string_vazia_retorna_vazia(self):
        assert remove_digitos("") == ""

    def test_digitos_intercalados(self):
        assert remove_digitos("a1b2c3") == "abc"

    def test_caracteres_especiais_sao_preservados(self):
        assert remove_digitos("!@#$%") == "!@#$%"

    def test_espacos_sao_preservados(self):
        assert remove_digitos("  42  ") == "    "

    def test_string_alfanumerica_complexa(self):
        assert remove_digitos("CPF: 123.456.789-00") == "CPF: ..-"
