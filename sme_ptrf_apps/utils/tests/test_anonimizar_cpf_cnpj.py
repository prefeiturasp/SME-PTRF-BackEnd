from sme_ptrf_apps.utils.anonimizar_cpf_cnpj import anonimizar_cpf_cnpj_fornecedor


class TestAnonimizarCpfCnpjFornecedor:
    """Testes do padrão de anonimização: 3 primeiros + X + 2 últimos."""

    def test_cpf_11_digitos_anonimizado(self):
        assert anonimizar_cpf_cnpj_fornecedor("12345678901") == "123XXXXXX01"
        assert anonimizar_cpf_cnpj_fornecedor("123.456.789-01") == "123XXXXXX01"
        assert anonimizar_cpf_cnpj_fornecedor("12345678945") == "123XXXXXX45"

    def test_cnpj_14_digitos_anonimizado(self):
        assert anonimizar_cpf_cnpj_fornecedor("11478276000104") == "114XXXXXXXXX04"
        assert anonimizar_cpf_cnpj_fornecedor("11.478.276/0001-04") == "114XXXXXXXXX04"

    def test_valor_vazio_retorna_vazio(self):
        assert anonimizar_cpf_cnpj_fornecedor("") == ""
        assert anonimizar_cpf_cnpj_fornecedor(None) == ""

    def test_valor_none_retorna_string_vazia(self):
        assert anonimizar_cpf_cnpj_fornecedor(None) == ""

    def test_digitos_diferente_11_ou_14_retorna_original(self):
        assert anonimizar_cpf_cnpj_fornecedor("123") == "123"
        assert anonimizar_cpf_cnpj_fornecedor("12345678") == "12345678"
