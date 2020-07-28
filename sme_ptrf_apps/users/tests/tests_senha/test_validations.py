import pytest
from rest_framework import serializers

from sme_ptrf_apps.users.api.validations.usuario_validations import senha_nao_pode_ser_nulo, senhas_devem_ser_iguais

pytestmark = pytest.mark.django_db


def test_senhas_devem_ser_iguais():
    password = '12345'
    password2 = '123456'
    esperado = 'Senhas informadas devem ser iguais'
    with pytest.raises(serializers.ValidationError, match=esperado):
        senhas_devem_ser_iguais(password, password2)


def test_campos_vazios_devem_ser_preenchidos():
    campo = 'Senha'
    valor1 = '123456'
    valor2 = ''
    valor3 = None
    esperado = 'O Campo {} deve ser preenchido'.format(campo)
    with pytest.raises(serializers.ValidationError, match=esperado):
        senha_nao_pode_ser_nulo(valor2, campo)
        senha_nao_pode_ser_nulo(valor3, campo)

    assert senha_nao_pode_ser_nulo(valor1, campo) is None
