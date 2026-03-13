def test_recurso_list_filter_lookups(recursos, request_factory_admin, recurso_list_filter):
    ptrf, premium = recursos

    filtro = recurso_list_filter

    resultado = list(filtro.lookups(request_factory_admin, None))

    esperado = [
        (str(premium.id), "premium"),
        (str(ptrf.id), "ptrf"),
    ]

    for item in esperado:
        assert item in resultado
