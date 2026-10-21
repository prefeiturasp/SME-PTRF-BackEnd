from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr


class Inner:
    valor = 42


class Outer:
    inner = Inner()
    nome = "Outer"


class TestGetRecursiveAttr:
    def test_campo_unico(self):
        assert get_recursive_attr(Outer(), "nome") == "Outer"

    def test_dois_niveis_encadeados(self):
        assert get_recursive_attr(Outer(), "inner__valor") == 42

    def test_tres_niveis_encadeados(self):
        class A:
            pass

        class B:
            pass

        class C:
            x = "deep"

        b = B()
        b.c = C()
        a = A()
        a.b = b
        assert get_recursive_attr(a, "b__c__x") == "deep"

    def test_fields_string_vazia_retorna_none(self):
        assert get_recursive_attr(Outer(), "") is None

    def test_fields_none_retorna_none(self):
        assert get_recursive_attr(Outer(), None) is None

    def test_fields_lista_vazia_retorna_none(self):
        assert get_recursive_attr(Outer(), []) is None

    def test_campo_intermediario_none_retorna_none(self):
        class Obj:
            filho = None

        assert get_recursive_attr(Obj(), "filho__nome") is None
