from unittest.mock import patch

from ...services.sme_integracao_service import SmeIntegracaoService


def test_pesquisa_rf_sem_cargo_na_escola():

    api_get_cargos_do_rf = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_cargos_do_rf'
    api_get_rfs_com_o_cargo_na_escola = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_rfs_com_o_cargo_na_escola'

    with patch(api_get_cargos_do_rf) as mock_api_get_cargos_do_rf:
        mock_api_get_cargos_do_rf.return_value = {
            "nomeServidor": "LUCIMARA CARDOSO RODRIGUES",
            "codigoServidor": "7210418",
            "cargos": [
                {
                    "codigoCargo": "3298",
                    "nomeCargo": "PROF.ENS.FUND.II E MED.-PORTUGUES",
                    "nomeCargoSobreposto": "ASSISTENTE DE DIRETOR DE ESCOLA",
                    "codigoCargoSobreposto": "3085"
                }
            ]
        }

        with patch(api_get_rfs_com_o_cargo_na_escola) as mock_api_get_rfs_com_o_cargo_na_escola:
            mock_api_get_rfs_com_o_cargo_na_escola.return_value = [
                {
                    "codigoRF": 8382492,
                    "nomeServidor": "DANIELA CRISTINA BRAZ",
                    "dataInicio": "02/03/2017 00:00:00",
                    "dataFim": None,
                    "cargo": "ASSISTENTE DE DIRETOR DE ESCOLA",
                    "cdTipoFuncaoAtividade": 0
                },
                {
                    "codigoRF": 271170,
                    "nomeServidor": "JOSE TESTANDO",
                    "dataInicio": "02/03/2017 00:00:00",
                    "dataFim": None,
                    "cargo": "ASSISTENTE DE DIRETOR DE ESCOLA",
                    "cdTipoFuncaoAtividade": 0
                },
            ]

            cargo_do_rf = SmeIntegracaoService.get_cargos_do_rf_na_escola(rf="271170", codigo_eol="123456")

    cargo_do_rf_esperado = [
        {
            "codigoRF": 271170,
            "nomeServidor": "JOSE TESTANDO",
            "dataInicio": "02/03/2017 00:00:00",
            "dataFim": None,
            "cargo": "ASSISTENTE DE DIRETOR DE ESCOLA",
            "cdTipoFuncaoAtividade": 0
        },
    ]

    assert cargo_do_rf == cargo_do_rf_esperado
