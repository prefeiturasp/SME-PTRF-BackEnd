from sme_ptrf_apps.utils.choices_to_json import choices_to_json


class TestChoicesToJson:
    def test_lista_vazia_retorna_lista_vazia(self):
        assert choices_to_json([]) == []

    def test_converte_tupla_para_dict_com_id_e_nome(self):
        result = choices_to_json([("A", "Alpha")])
        assert result == [{"id": "A", "nome": "Alpha"}]

    def test_converte_multiplas_choices(self):
        choices = [("A", "Alpha"), ("B", "Beta"), ("C", "Gamma")]
        result = choices_to_json(choices)
        assert result == [
            {"id": "A", "nome": "Alpha"},
            {"id": "B", "nome": "Beta"},
            {"id": "C", "nome": "Gamma"},
        ]

    def test_preserva_ordem_das_choices(self):
        choices = [("Z", "Zeta"), ("A", "Alpha")]
        result = choices_to_json(choices)
        assert result[0]["id"] == "Z"
        assert result[1]["id"] == "A"

    def test_aceita_id_inteiro(self):
        result = choices_to_json([(1, "Um"), (2, "Dois")])
        assert result == [{"id": 1, "nome": "Um"}, {"id": 2, "nome": "Dois"}]

    def test_retorna_lista(self):
        assert isinstance(choices_to_json([("X", "Y")]), list)
