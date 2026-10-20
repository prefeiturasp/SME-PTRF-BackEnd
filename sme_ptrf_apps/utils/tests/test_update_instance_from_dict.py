from unittest.mock import MagicMock

from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict


class Obj:
    pass


class TestUpdateInstanceFromDict:
    def test_atualiza_atributos_da_instancia(self):
        obj = Obj()
        update_instance_from_dict(obj, {"nome": "Teste", "valor": 42})
        assert obj.nome == "Teste"
        assert obj.valor == 42

    def test_retorna_a_propria_instancia(self):
        obj = Obj()
        result = update_instance_from_dict(obj, {"x": 1})
        assert result is obj

    def test_dict_vazio_nao_altera_instancia(self):
        obj = Obj()
        obj.nome = "original"
        update_instance_from_dict(obj, {})
        assert obj.nome == "original"

    def test_sobrescreve_atributo_existente(self):
        obj = Obj()
        obj.status = "ativo"
        update_instance_from_dict(obj, {"status": "inativo"})
        assert obj.status == "inativo"

    def test_save_false_nao_chama_save(self):
        mock = MagicMock()
        update_instance_from_dict(mock, {"x": 1}, save=False)
        mock.save.assert_not_called()

    def test_save_true_chama_save(self):
        mock = MagicMock()
        update_instance_from_dict(mock, {"x": 1}, save=True)
        mock.save.assert_called_once()

    def test_save_padrao_nao_chama_save(self):
        mock = MagicMock()
        update_instance_from_dict(mock, {"x": 1})
        mock.save.assert_not_called()
