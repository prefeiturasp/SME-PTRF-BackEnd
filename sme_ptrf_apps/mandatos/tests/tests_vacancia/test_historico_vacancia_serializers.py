from datetime import date

import pytest
from rest_framework import serializers

from sme_ptrf_apps.mandatos.api.serializers.cargo_composicao_vacancia_serializer import (
    CargoComposicaoVacanciaSerializer,
    CargoComposicaoVacanciaCreateSerializer,
    RegistrarSaidaSerializer,
)
from sme_ptrf_apps.mandatos.models import CargoComposicaoVacancia, OcupanteCargo
from sme_ptrf_apps.mandatos.choices import CargoComposicaoVacanciaChoices as Cargo
from sme_ptrf_apps.mandatos.services import ServicoHistoricoCargoComposicao
from sme_ptrf_apps.mandatos.fixtures.factories.mandato_factory import MandatoFactory
from sme_ptrf_apps.mandatos.fixtures.factories.ocupante_cargo_factory import OcupanteCargoFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def mandato_2026():
    return MandatoFactory(data_inicial=date(2026, 1, 1), data_final=date(2026, 12, 31))


@pytest.fixture
def composicao_vacancia(mandato_2026, associacao_factory):
    associacao = associacao_factory.create()
    return ServicoHistoricoCargoComposicao.get_or_create_composicao_vacancia(
        associacao=associacao, mandato=mandato_2026
    )


@pytest.fixture
def cargo_ocupado(composicao_vacancia):
    return ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=OcupanteCargoFactory(),
        cargo_associacao=Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA,
        data_entrada=date(2026, 1, 1),
    )


def _payload_ocupante(**kwargs):
    payload = {
        'nome': 'Fulano de Tal',
        'codigo_identificacao': '654321',
        'cpf_responsavel': '99988877766',
        'representacao': OcupanteCargo.REPRESENTACAO_CARGO_SERVIDOR,
    }
    payload.update(kwargs)
    return payload


# CargoComposicaoVacanciaSerializer (leitura)

def test_serializer_leitura_expoe_campos_esperados(cargo_ocupado):
    """Confere que os campos declarados em Meta.fields são todos serializados."""
    data = CargoComposicaoVacanciaSerializer(cargo_ocupado).data

    assert data['id'] == cargo_ocupado.id
    assert data['uuid'] == str(cargo_ocupado.uuid)
    assert data['cargo_associacao'] == Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA
    assert data['cargo_associacao_label'] == Cargo.CARGO_ASSOCIACAO_PRESIDENTE_DIRETORIA_EXECUTIVA.label
    assert data['ocupante_do_cargo']['id'] == cargo_ocupado.ocupante_do_cargo.id
    assert data['data_inicio_no_cargo'] == '2026-01-01'
    assert data['vago'] is False
    assert data['substituto'] is False
    assert data['substituido'] is False
    assert data['substituido_por'] is None


def test_serializer_leitura_vago_true_para_registro_sem_ocupante(composicao_vacancia):
    """vago (SerializerMethodField) reflete ocupante_do_cargo=None."""
    registro_vago = CargoComposicaoVacancia.objects.create(
        composicao=composicao_vacancia,
        ocupante_do_cargo=None,
        cargo_associacao=Cargo.CARGO_ASSOCIACAO_CONSELHEIRO_1,
        data_inicio_no_cargo=date(2026, 1, 1),
        data_fim_no_cargo=date(2026, 12, 31),
    )

    data = CargoComposicaoVacanciaSerializer(registro_vago).data

    assert data['vago'] is True
    assert data['ocupante_do_cargo'] is None


def test_serializer_leitura_substituto_e_substituido_refletem_substituido_por(composicao_vacancia):
    """substituto/substituido (properties calculadas) aparecem certas no JSON."""
    pedro = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=OcupanteCargoFactory(),
        cargo_associacao=Cargo.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 1, 1),
    )
    ServicoHistoricoCargoComposicao.registrar_saida(pedro, data_saida=date(2026, 2, 1))
    luis = ServicoHistoricoCargoComposicao.registrar_entrada(
        composicao_vacancia=composicao_vacancia,
        ocupante_do_cargo=OcupanteCargoFactory(),
        cargo_associacao=Cargo.CARGO_ASSOCIACAO_TESOUREIRO,
        data_entrada=date(2026, 2, 1),
    )
    pedro.refresh_from_db()

    data_pedro = CargoComposicaoVacanciaSerializer(pedro).data
    data_luis = CargoComposicaoVacanciaSerializer(luis).data

    assert data_pedro['substituido'] is True
    assert data_pedro['substituido_por'] == luis.id
    assert data_luis['substituto'] is True


# CargoComposicaoVacanciaCreateSerializer

def test_create_serializer_cria_ocupante_e_delega_para_o_service(composicao_vacancia):
    """create() monta/reaproveita o OcupanteCargo e delega o registro em si pro service
    (registrar_entrada) — o serializer não guarda lógica de negócio."""
    payload = {
        'composicao': str(composicao_vacancia.uuid),
        'cargo_associacao': Cargo.CARGO_ASSOCIACAO_SECRETARIO,
        'data_inicio_no_cargo': '2026-01-01',
        'ocupante_do_cargo': _payload_ocupante(nome='Pedro Teste'),
    }

    serializer = CargoComposicaoVacanciaCreateSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors

    criado = serializer.save()

    assert criado.pk is not None
    assert criado.cargo_associacao == Cargo.CARGO_ASSOCIACAO_SECRETARIO
    assert criado.ocupante_do_cargo.nome == 'Pedro Teste'
    assert criado.data_fim_no_cargo == composicao_vacancia.mandato.data_final  # vigente


def test_create_serializer_reaproveita_ocupante_existente_por_codigo_e_cpf(composicao_vacancia):
    """update_or_create no create() não deve duplicar OcupanteCargo já cadastrado."""
    existente = OcupanteCargoFactory(
        codigo_identificacao='999999', cpf_responsavel='55566677788', nome='Nome Antigo',
    )
    payload = {
        'composicao': str(composicao_vacancia.uuid),
        'cargo_associacao': Cargo.CARGO_ASSOCIACAO_VOGAL_1,
        'data_inicio_no_cargo': '2026-01-01',
        'ocupante_do_cargo': _payload_ocupante(
            nome='Nome Atualizado', codigo_identificacao='999999', cpf_responsavel='55566677788',
        ),
    }

    serializer = CargoComposicaoVacanciaCreateSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors
    criado = serializer.save()

    assert OcupanteCargo.objects.filter(codigo_identificacao='999999').count() == 1
    assert criado.ocupante_do_cargo.id == existente.id
    existente.refresh_from_db()
    assert existente.nome == 'Nome Atualizado'


def test_create_serializer_invalido_sem_composicao():
    """composicao é obrigatório (SlugRelatedField)."""
    payload = {
        'cargo_associacao': Cargo.CARGO_ASSOCIACAO_VOGAL_2,
        'data_inicio_no_cargo': '2026-01-01',
        'ocupante_do_cargo': _payload_ocupante(),
    }

    serializer = CargoComposicaoVacanciaCreateSerializer(data=payload)

    assert not serializer.is_valid()
    assert 'composicao' in serializer.errors


def test_create_serializer_composicao_uuid_inexistente_invalida():
    """SlugRelatedField rejeita um uuid de composição que não existe."""
    payload = {
        'composicao': '00000000-0000-0000-0000-000000000000',
        'cargo_associacao': Cargo.CARGO_ASSOCIACAO_VOGAL_3,
        'data_inicio_no_cargo': '2026-01-01',
        'ocupante_do_cargo': _payload_ocupante(),
    }

    serializer = CargoComposicaoVacanciaCreateSerializer(data=payload)

    assert not serializer.is_valid()
    assert 'composicao' in serializer.errors


def test_create_serializer_propaga_erro_de_negocio_do_service(cargo_ocupado, composicao_vacancia):
    """Se o service recusar (ex.: cargo já ocupado e vigente), o erro sobe pra
    quem chamou o serializer, sem lógica de validação duplicada aqui."""
    payload = {
        'composicao': str(composicao_vacancia.uuid),
        'cargo_associacao': cargo_ocupado.cargo_associacao,  # já tem alguém vigente
        'data_inicio_no_cargo': '2026-03-01',
        'ocupante_do_cargo': _payload_ocupante(),
    }
    serializer = CargoComposicaoVacanciaCreateSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors

    with pytest.raises(serializers.ValidationError):
        serializer.save()


# RegistrarSaidaSerializer

def test_registrar_saida_serializer_valido_com_data():
    serializer = RegistrarSaidaSerializer(data={'data_saida': '2026-06-01'})

    assert serializer.is_valid()
    assert serializer.validated_data['data_saida'] == date(2026, 6, 1)


def test_registrar_saida_serializer_invalido_sem_data():
    """data_saida é obrigatório."""
    serializer = RegistrarSaidaSerializer(data={})

    assert not serializer.is_valid()
    assert 'data_saida' in serializer.errors


def test_registrar_saida_serializer_invalido_com_data_mal_formatada():
    serializer = RegistrarSaidaSerializer(data={'data_saida': 'não-é-uma-data'})

    assert not serializer.is_valid()
    assert 'data_saida' in serializer.errors
