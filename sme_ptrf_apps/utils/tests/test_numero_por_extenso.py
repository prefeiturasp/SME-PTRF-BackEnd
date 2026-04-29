from sme_ptrf_apps.utils.numero_por_extenso import (
    formatar,
    milhares,
    monetario,
    real,
    separar_casas,
    unidade_dezena_centena,
)


class TestSepararCasas:
    def test_um_digito(self):
        assert separar_casas(5) == [[5]]

    def test_dois_digitos(self):
        assert separar_casas(10) == [[1, 0]]

    def test_tres_digitos(self):
        assert separar_casas(100) == [[1, 0, 0]]

    def test_quatro_digitos_forma_dois_ternos(self):
        assert separar_casas(1000) == [[1], [0, 0, 0]]

    def test_sete_digitos_forma_tres_ternos(self):
        assert separar_casas(1000000) == [[1], [0, 0, 0], [0, 0, 0]]

    def test_numero_composto(self):
        assert separar_casas(1234) == [[1], [2, 3, 4]]


class TestUnidadeDezena:
    def test_zero(self):
        assert unidade_dezena_centena([0]) == 'zero'

    def test_um(self):
        assert unidade_dezena_centena([1]) == 'um'

    def test_nove(self):
        assert unidade_dezena_centena([9]) == 'nove'

    def test_dez(self):
        assert unidade_dezena_centena([1, 0]) == 'dez'

    def test_onze_dezena_especial(self):
        assert unidade_dezena_centena([1, 1]) == 'onze'

    def test_dezenove_dezena_especial(self):
        assert unidade_dezena_centena([1, 9]) == 'dezenove'

    def test_vinte_dezena_exata(self):
        assert unidade_dezena_centena([2, 0]) == 'vinte'

    def test_dezena_composta(self):
        assert unidade_dezena_centena([2, 5]) == 'vinte e cinco'

    def test_cem_centena_exata(self):
        assert unidade_dezena_centena([1, 0, 0]) == 'cem'

    def test_cento_e_um(self):
        assert unidade_dezena_centena([1, 0, 1]) == 'cento e um'

    def test_duzentos_centena_exata(self):
        assert unidade_dezena_centena([2, 0, 0]) == 'duzentos'

    def test_centena_composta(self):
        assert unidade_dezena_centena([3, 4, 5]) == 'trezentos e quarenta e cinco'


class TestMilhares:
    def test_terno_simples(self):
        assert milhares([[5]]) == 'cinco'

    def test_milhar_exato(self):
        assert milhares([[1], [0, 0, 0]]) == 'um mil'

    def test_milhao_exato(self):
        assert milhares([[1], [0, 0, 0], [0, 0, 0]]) == 'um milhão'

    def test_terno_zero_ignorado(self):
        assert milhares([[0, 0, 0], [5]]) == ' cinco'


class TestFormatar:
    def test_inteiro_simples(self):
        assert formatar("100") == (100, '0')

    def test_decimal_com_ponto(self):
        assert formatar("1.5") == (1, '5')

    def test_decimal_com_virgula(self):
        assert formatar("1,5") == (1, '5')

    def test_zero(self):
        assert formatar("0") == (0, '0')

    def test_valor_monetario_dois_casas(self):
        assert formatar("1.50") == (1, '5')


class TestReal:
    def test_zero(self):
        assert real(0) == 'zero'

    def test_um(self):
        assert real(1) == 'um'

    def test_cinco(self):
        assert real(5) == 'cinco'

    def test_dez(self):
        assert real(10) == 'dez'

    def test_onze(self):
        assert real(11) == 'onze'

    def test_vinte_e_cinco(self):
        assert real(25) == 'vinte e cinco'

    def test_cem(self):
        assert real(100) == 'cem'

    def test_cento_e_um(self):
        assert real(101) == 'cento e um'

    def test_mil(self):
        assert real(1000) == 'um mil'

    def test_milhao(self):
        assert real(1000000) == 'um milhão'

    def test_decimal_virgula(self):
        assert real("1,5") == 'um inteiro e cinco décimos'

    def test_dois_inteiros_e_decimal(self):
        assert real("2.5") == 'dois inteiros e cinco décimos'

    def test_so_decimal_sem_parte_inteira(self):
        assert real("0.25") == 'vinte e cinco centésimos'


class TestMonetario:
    def test_zero_retorna_vazio(self):
        assert monetario(0) == ''

    def test_um_real(self):
        assert monetario(1) == 'um real'

    def test_dois_reais(self):
        assert monetario(2) == 'dois reais'

    def test_mil_reais(self):
        assert monetario(1000) == 'um mil reais'

    def test_um_centavo(self):
        assert monetario("0.01") == 'um centavo'

    def test_cinquenta_centavos(self):
        assert monetario("0.50") == 'cincoenta centavos'

    def test_um_real_e_um_centavo(self):
        assert monetario("1.01") == 'um real e um centavo'

    def test_um_real_e_cinquenta_centavos(self):
        assert monetario("1.50") == 'um real e cincoenta centavos'

    def test_mil_reais_e_cinquenta_centavos(self):
        assert monetario("1000.50") == 'um mil reais e cincoenta centavos'

    def test_aceita_virgula_como_separador(self):
        assert monetario("2,50") == 'dois reais e cincoenta centavos'
