from unittest.mock import patch

import pytest
from rest_framework import serializers

from sme_ptrf_apps.core.services import TerceirizadasService
from sme_ptrf_apps.dre.models import MembroComissao, PresenteAtaDre
from sme_ptrf_apps.dre.services.membro_comissao_service import MembroComissaoService

pytestmark = pytest.mark.django_db


def test_validar_duplicidade_rf_rejeita_rf_existente(membro_service, membro_service_dre):
    membro_service.dre = membro_service_dre
    membro_service.save(update_fields=['dre'])

    with pytest.raises(serializers.ValidationError) as exc_info:
        MembroComissaoService.validar_duplicidade_rf(
            rf=membro_service.rf,
            dre=membro_service_dre,
        )

    assert exc_info.value.detail == {
        'detail': 'Já existe um membro de comissão com esse Registro Funcional.'
    }


def test_validar_duplicidade_rf_permite_rf_da_propria_instancia(membro_service, membro_service_dre):
    membro_service.dre = membro_service_dre
    membro_service.save(update_fields=['dre'])

    MembroComissaoService.validar_duplicidade_rf(
        rf=membro_service.rf,
        dre=membro_service_dre,
        instance_rf=membro_service.rf,
    )


def test_validar_e_extrair_comissoes_rejeita_lista_vazia():
    with pytest.raises(serializers.ValidationError) as exc_info:
        MembroComissaoService.validar_e_extrair_comissoes({'comissoes': []})

    assert exc_info.value.detail == {
        'detail': 'Para salvar um membro de comissão, é necessário informar pelo menos uma comissão'
    }


def test_criar_membro_vincula_membro_as_atas_responsaveis(
    membro_service_dre,
    membro_service_comissao_responsavel,
    membro_service_ata,
):
    dados_servidor = [{'nm_pessoa': 'Membro Service', 'cargo': 'Professor'}]
    dados = {
        'rf': '1231231',
        'nome': 'Membro Criado',
        'email': 'criado@teste.com',
        'cargo': 'Professor',
        'dre': membro_service_dre,
        'comissoes': [membro_service_comissao_responsavel],
    }

    with patch.object(
        TerceirizadasService,
        'get_informacao_servidor',
        return_value=dados_servidor,
    ):
        membro = MembroComissaoService.criar_membro(dados)

    assert membro.comissoes.filter(pk=membro_service_comissao_responsavel.pk).exists()
    assert membro_service_ata.presentes_na_ata.filter(rf=membro.rf).exists()
    presente = membro_service_ata.presentes_na_ata.get(rf=membro.rf)
    assert presente.nome == 'Membro Service'
    assert presente.cargo == 'Professor'


def test_atualizar_membro_remove_presenca_ao_trocar_para_comissao_nao_responsavel(
    membro_service,
    membro_service_dre,
    membro_service_comissao,
    presente_ata_membro_service,
):
    MembroComissaoService.atualizar_membro(
        membro_service,
        {
            'comissoes': [membro_service_comissao],
            'cargo': 'Coordenador',
            'dre': membro_service_dre,
            'rf': membro_service.rf,
        },
    )

    assert membro_service.cargo == 'Coordenador'
    assert not presente_ata_membro_service.ata.presentes_na_ata.filter(rf=membro_service.rf).exists()


def test_deletar_membro_remove_presentes_apenas_de_atas_nao_geradas(
    membro_service_com_dre,
    presente_ata_nao_gerada,
    presente_ata_gerada,
):
    MembroComissaoService.deletar_membro(membro_service_com_dre)

    assert not MembroComissao.objects.filter(pk=membro_service_com_dre.pk).exists()
    assert not PresenteAtaDre.objects.filter(pk=presente_ata_nao_gerada.pk).exists()
    assert PresenteAtaDre.objects.filter(pk=presente_ata_gerada.pk).exists()
