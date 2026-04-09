import json
import uuid
import pytest
from rest_framework import status

from sme_ptrf_apps.paa.models import AtaPaa, ReplicaPaa, DocumentoPaa

pytestmark = pytest.mark.django_db

HISTORICO_VAZIO = {
    'texto_introducao': '', 'texto_conclusao': '',
    'objetivos': {}, 'receitas_ptrf': {},
    'receitas_pdde': {}, 'receitas_outros_recursos': {},
    'prioridades': {},
}


# ===========================================================================
# Action: iniciar-retificacao  (POST /{uuid}/iniciar-retificacao/)
# ===========================================================================

class TestIniciarRetificacaoAction:

    def test_retorna_404_quando_flag_inativa(
        self, jwt_authenticated_client_sme, flag_paa, paa_factory
    ):
        paa = paa_factory()

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa.uuid}/iniciar-retificacao/',
            content_type='application/json',
            data=json.dumps({'justificativa': 'Justificativa.'}),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['erro'] == 'iniciar_retificacao'

    def test_retorna_400_quando_justificativa_ausente(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory
    ):
        paa = paa_factory()

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa.uuid}/iniciar-retificacao/',
            content_type='application/json',
            data=json.dumps({}),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['erro'] == 'iniciar_retificacao'

    def test_retorna_400_quando_justificativa_vazia(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory,
        ata_paa_factory, documento_paa_factory
    ):
        paa = paa_factory(
            texto_introducao='Introducao original.',
            texto_conclusao='Conclusao original.',
            status='GERADO'
        )
        ata_paa_factory.create(
            paa=paa,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa.uuid}/iniciar-retificacao/',
            content_type='application/json',
            data=json.dumps({'justificativa': '   '}),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['erro'] == 'iniciar_retificacao'

    def test_retorna_201_com_justificativa_valida(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory,
        ata_paa_factory, documento_paa_factory
    ):
        paa = paa_factory(
            texto_introducao='Introducao original.',
            texto_conclusao='Conclusao original.',
            status='GERADO'
        )
        ata_paa_factory.create(
            paa=paa,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa.uuid}/iniciar-retificacao/',
            content_type='application/json',
            data=json.dumps({'justificativa': 'Justificativa válida.'}),
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_resposta_contem_paa_uuid(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory,
        ata_paa_factory, documento_paa_factory
    ):
        paa = paa_factory(
            texto_introducao='Introducao original.',
            texto_conclusao='Conclusao original.',
            status='GERADO'
        )
        ata_paa_factory.create(
            paa=paa,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )

        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa.uuid}/iniciar-retificacao/',
            content_type='application/json',
            data=json.dumps({'justificativa': 'Justificativa.'}),
        )

        assert 'paa_uuid' in response.data
        assert response.data['paa_uuid'] == str(paa.uuid)

    def test_cria_replica_paa_no_banco(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory,
        ata_paa_factory, documento_paa_factory
    ):
        paa = paa_factory(
            texto_introducao='Introducao original.',
            texto_conclusao='Conclusao original.',
            status='GERADO'
        )
        ata_paa_factory.create(
            paa=paa,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )
        assert not ReplicaPaa.objects.filter(paa=paa).exists()

        jwt_authenticated_client_sme.post(
            f'/api/paa/{paa.uuid}/iniciar-retificacao/',
            content_type='application/json',
            data=json.dumps({'justificativa': 'Justificativa.'}),
        )

        assert ReplicaPaa.objects.filter(paa=paa).exists()

    def test_cria_ata_de_retificacao_no_banco(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory,
        ata_paa_factory, documento_paa_factory
    ):
        paa = paa_factory(
            texto_introducao='Introducao original.',
            texto_conclusao='Conclusao original.',
            status='GERADO'
        )
        ata_paa_factory.create(
            paa=paa,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )

        jwt_authenticated_client_sme.post(
            f'/api/paa/{paa.uuid}/iniciar-retificacao/',
            content_type='application/json',
            data=json.dumps({'justificativa': 'Justificativa.'}),
        )

        assert AtaPaa.objects.filter(
            paa=paa, tipo_ata=AtaPaa.ATA_RETIFICACAO
        ).exists()

    def test_ata_criada_com_justificativa_correta(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory,
        ata_paa_factory, documento_paa_factory
    ):
        paa = paa_factory(
            texto_introducao='Introducao original.',
            texto_conclusao='Conclusao original.',
            status='GERADO'
        )
        ata_paa_factory.create(
            paa=paa,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )
        justificativa = 'Justificativa específica para o teste.'

        jwt_authenticated_client_sme.post(
            f'/api/paa/{paa.uuid}/iniciar-retificacao/',
            content_type='application/json',
            data=json.dumps({'justificativa': justificativa}),
        )

        ata = AtaPaa.objects.get(paa=paa, tipo_ata=AtaPaa.ATA_RETIFICACAO)
        assert ata.justificativa == justificativa

    def test_paa_inexistente_retorna_404(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao
    ):
        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{uuid.uuid4()}/iniciar-retificacao/',
            content_type='application/json',
            data=json.dumps({'justificativa': 'Justificativa.'}),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# ===========================================================================
# Action: paa-retificacao  (GET /{uuid}/paa-retificacao/)
# ===========================================================================

class TestPaaRetificacaoAction:

    def test_retorna_404_quando_flag_inativa(
        self, jwt_authenticated_client_sme, flag_paa, paa_factory
    ):
        paa = paa_factory()

        response = jwt_authenticated_client_sme.get(
            f'/api/paa/{paa.uuid}/paa-retificacao/',
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['erro'] == 'sem_retificacao'

    def test_retorna_200_quando_replica_existe(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory, replica_paa_factory
    ):
        paa = paa_factory()
        replica_paa_factory(paa=paa, historico=HISTORICO_VAZIO)

        response = jwt_authenticated_client_sme.get(
            f'/api/paa/{paa.uuid}/paa-retificacao/',
        )

        assert response.status_code == status.HTTP_200_OK

    def test_resposta_contem_campo_alteracoes(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory, replica_paa_factory
    ):
        paa = paa_factory()
        replica_paa_factory(paa=paa, historico=HISTORICO_VAZIO)

        response = jwt_authenticated_client_sme.get(
            f'/api/paa/{paa.uuid}/paa-retificacao/',
        )

        assert 'alteracoes' in response.data

    def test_alteracoes_e_dict(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory, replica_paa_factory
    ):
        paa = paa_factory()
        replica_paa_factory(paa=paa, historico=HISTORICO_VAZIO)

        response = jwt_authenticated_client_sme.get(
            f'/api/paa/{paa.uuid}/paa-retificacao/',
        )

        assert isinstance(response.data['alteracoes'], dict)

    def test_alteracoes_detecta_mudanca_em_texto(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory, replica_paa_factory
    ):
        paa = paa_factory(texto_introducao='Texto novo.')
        replica_paa_factory(paa=paa, historico={
            **HISTORICO_VAZIO,
            'texto_introducao': 'Texto original.',
        })

        response = jwt_authenticated_client_sme.get(
            f'/api/paa/{paa.uuid}/paa-retificacao/',
        )

        assert 'texto_introducao' in response.data['alteracoes']

    def test_resposta_contem_campos_do_paa(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao, paa_factory, replica_paa_factory
    ):
        paa = paa_factory()
        replica_paa_factory(paa=paa, historico=HISTORICO_VAZIO)

        response = jwt_authenticated_client_sme.get(
            f'/api/paa/{paa.uuid}/paa-retificacao/',
        )

        assert 'uuid' in response.data
        assert 'status' in response.data
        assert response.data['uuid'] == str(paa.uuid)

    def test_paa_inexistente_retorna_404(
        self, jwt_authenticated_client_sme, flag_paa, flag_paa_retificacao
    ):
        response = jwt_authenticated_client_sme.get(
            f'/api/paa/{uuid.uuid4()}/paa-retificacao/',
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
