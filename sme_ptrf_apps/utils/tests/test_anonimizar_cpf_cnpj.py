from sme_ptrf_apps.utils.anonimizar_cpf_cnpj import anonimizar_cpf


class TestAnonimizarCpfCnpjFornecedor:
    """Testes do padrão de anonimização: 3 primeiros + X + 2 últimos."""

    def test_cpf_11_digitos_anonimizado(self):
        assert anonimizar_cpf("12345678901") == "123XXXXXX01"
        assert anonimizar_cpf("123.456.789-01") == "123XXXXXX01"
        assert anonimizar_cpf("12345678945") == "123XXXXXX45"

    def test_cnpj_14_digitos_retorna_original(self):
        """CNPJ não é anonimizado; retorna o valor original."""
        assert anonimizar_cpf("11478276000104") == "11478276000104"
        assert anonimizar_cpf("11.478.276/0001-04") == "11.478.276/0001-04"

    def test_valor_vazio_retorna_vazio(self):
        assert anonimizar_cpf("") == ""
        assert anonimizar_cpf(None) == ""

    def test_valor_none_retorna_string_vazia(self):
        assert anonimizar_cpf(None) == ""

    def test_digitos_diferente_11_ou_14_retorna_original(self):
        assert anonimizar_cpf("123") == "123"
        assert anonimizar_cpf("12345678") == "12345678"

    def test_formato_alfanumerico_11_caracteres_anonimizado(self):
        """Aceita formato alfanumérico (novo formato) com 11 caracteres."""
        assert anonimizar_cpf("ABC12345678") == "ABCXXXXXX78"
        assert anonimizar_cpf("1A2B3C4D5E6") == "1A2XXXXXXE6"

    def test_formato_alfanumerico_14_caracteres_retorna_original(self):
        """CNPJ (14 caracteres) não é anonimizado; retorna o valor original."""
        assert anonimizar_cpf("AB123456780099") == "AB123456780099"
        assert anonimizar_cpf("11.478.276/0001-04") == "11.478.276/0001-04"
