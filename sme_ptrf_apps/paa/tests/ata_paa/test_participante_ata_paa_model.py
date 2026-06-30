import pytest
from unittest.mock import patch
from requests import ConnectTimeout, ReadTimeout

from sme_ptrf_apps.paa.models import ParticipanteAtaPaa
from sme_ptrf_apps.core.services import TerceirizadasException, SmeIntegracaoApiException

pytestmark = pytest.mark.django_db


class TestEhConselhoFiscal:

    def test_cargo_presidente_conselho_seta_conselho_fiscal(self, participante_ata_paa_factory, ata_paa):
        participante = participante_ata_paa_factory.create(
            ata_paa=ata_paa,
            cargo='Presidente do conselho fiscal',
            conselho_fiscal=False,
        )
        participante.eh_conselho_fiscal()
        participante.refresh_from_db()
        assert participante.conselho_fiscal is True

    def test_cargo_conselheiro_seta_conselho_fiscal(self, participante_ata_paa_factory, ata_paa):
        participante = participante_ata_paa_factory.create(
            ata_paa=ata_paa,
            cargo='Conselheiro',
            conselho_fiscal=False,
        )
        participante.eh_conselho_fiscal()
        participante.refresh_from_db()
        assert participante.conselho_fiscal is True

    def test_cargo_outro_nao_seta_conselho_fiscal(self, participante_ata_paa_factory, ata_paa):
        participante = participante_ata_paa_factory.create(
            ata_paa=ata_paa,
            cargo='Secretário',
            conselho_fiscal=False,
        )
        participante.eh_conselho_fiscal()
        participante.refresh_from_db()
        assert participante.conselho_fiscal is False


class TestEditavel:

    def test_editavel_retorna_false(self, participante_ata_paa_factory, ata_paa):
        participante = participante_ata_paa_factory.create(ata_paa=ata_paa)
        assert participante.editavel is False


class TestOrdenarPorCargo:

    @pytest.mark.parametrize("cargo,posicao_esperada", [
        ('Presidente da diretoria executiva', 1),
        ('Vice-Presidente da diretoria executiva', 2),
        ('Secretário', 3),
        ('Tesoureiro', 4),
        ('Vogal', 5),
        ('Presidente do conselho fiscal', 6),
        ('Conselheiro', 7),
        ('Cargo desconhecido', 8),
    ])
    def test_ordenar_por_cargo(self, cargo, posicao_esperada):
        participante = {'cargo': cargo}
        assert ParticipanteAtaPaa.ordenar_por_cargo(participante) == posicao_esperada


class TestParticipantesOrdenadosPorCargo:

    def test_retorna_membros_ordenados(self, participante_ata_paa_factory, ata_paa):
        participante_ata_paa_factory.create(
            ata_paa=ata_paa, cargo='Tesoureiro', membro=True
        )
        participante_ata_paa_factory.create(
            ata_paa=ata_paa, cargo='Presidente da diretoria executiva', membro=True
        )
        resultado = ParticipanteAtaPaa.participantes_ordenados_por_cargo(ata_paa, membro=True)
        assert len(resultado) == 2
        assert resultado[0]['cargo'] == 'Presidente da diretoria executiva'
        assert resultado[1]['cargo'] == 'Tesoureiro'

    def test_filtra_por_membro(self, participante_ata_paa_factory, ata_paa):
        participante_ata_paa_factory.create(ata_paa=ata_paa, cargo='Secretário', membro=True)
        participante_ata_paa_factory.create(ata_paa=ata_paa, cargo='Vogal', membro=False)
        membros = ParticipanteAtaPaa.participantes_ordenados_por_cargo(ata_paa, membro=True)
        nao_membros = ParticipanteAtaPaa.participantes_ordenados_por_cargo(ata_paa, membro=False)
        assert len(membros) == 1
        assert len(nao_membros) == 1


class TestGetInformacaoServidor:

    @patch('sme_ptrf_apps.core.services.TerceirizadasService.get_informacao_servidor')
    def test_identificador_7_digitos_retorna_servidor(self, mock_service):
        mock_service.return_value = [{'nm_pessoa': 'João Silva', 'cargo': 'Professor'}]
        resultado = ParticipanteAtaPaa.get_informacao_servidor('1234567')
        assert resultado['mensagem'] == 'buscando-servidor-nao-membro'
        assert resultado['nome'] == 'João Silva'
        assert resultado['cargo'] == 'Professor'

    @patch('sme_ptrf_apps.core.services.TerceirizadasService.get_informacao_servidor')
    def test_identificador_7_digitos_servidor_nao_encontrado(self, mock_service):
        mock_service.return_value = None
        resultado = ParticipanteAtaPaa.get_informacao_servidor('1234567')
        assert resultado['mensagem'] == 'servidor-nao-encontrado'
        assert resultado['nome'] == ''
        assert resultado['cargo'] == ''

    def test_identificador_menos_de_7_digitos_retorna_nao_encontrado(self):
        resultado = ParticipanteAtaPaa.get_informacao_servidor('123')
        assert resultado['mensagem'] == 'servidor-nao-encontrado'

    def test_identificador_none_retorna_nao_encontrado(self):
        resultado = ParticipanteAtaPaa.get_informacao_servidor(None)
        assert resultado['mensagem'] == 'servidor-nao-encontrado'

    @patch('sme_ptrf_apps.core.services.TerceirizadasService.get_informacao_servidor')
    def test_sme_integracao_api_exception_retorna_nao_encontrado(self, mock_service):
        mock_service.side_effect = SmeIntegracaoApiException('erro')
        resultado = ParticipanteAtaPaa.get_informacao_servidor('1234567')
        assert resultado['mensagem'] == 'servidor-nao-encontrado'

    @patch('sme_ptrf_apps.core.services.TerceirizadasService.get_informacao_servidor')
    def test_terceirizadas_exception_retorna_nao_encontrado(self, mock_service):
        mock_service.side_effect = TerceirizadasException('erro')
        resultado = ParticipanteAtaPaa.get_informacao_servidor('1234567')
        assert resultado['mensagem'] == 'servidor-nao-encontrado'

    @patch('sme_ptrf_apps.core.services.TerceirizadasService.get_informacao_servidor')
    def test_read_timeout_retorna_nao_encontrado(self, mock_service):
        mock_service.side_effect = ReadTimeout()
        resultado = ParticipanteAtaPaa.get_informacao_servidor('1234567')
        assert resultado['mensagem'] == 'servidor-nao-encontrado'

    @patch('sme_ptrf_apps.core.services.TerceirizadasService.get_informacao_servidor')
    def test_connect_timeout_retorna_nao_encontrado(self, mock_service):
        mock_service.side_effect = ConnectTimeout()
        resultado = ParticipanteAtaPaa.get_informacao_servidor('1234567')
        assert resultado['mensagem'] == 'servidor-nao-encontrado'
