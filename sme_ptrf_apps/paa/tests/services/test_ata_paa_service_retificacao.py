import pytest
from datetime import date, time
from unittest.mock import patch

from model_bakery import baker

from sme_ptrf_apps.paa.models import AtaPaa, LogReplicaPaa
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.services.ata_paa_service import (
    gerar_arquivo_ata_paa_retificacao,
    validar_geracao_ata_paa,
    _salvar_log_replica,
    _remover_replica,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def usuario():
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_user(
        username='usuario.retificacao',
        email='retificacao@teste.com',
    )


@pytest.fixture
def paa_em_retificacao(paa_factory, periodo_paa_1, associacao):
    return paa_factory.create(
        periodo_paa=periodo_paa_1,
        associacao=associacao,
        status=PaaStatusEnum.EM_RETIFICACAO.name,
    )


@pytest.fixture
def ata_retificacao_nao_gerada(paa_em_retificacao, ata_paa_factory):
    return ata_paa_factory.create(
        paa=paa_em_retificacao,
        tipo_ata=AtaPaa.ATA_RETIFICACAO,
        status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
        data_reuniao=date(2024, 3, 15),
        hora_reuniao=time(14, 30),
        local_reuniao='Sala de Reuniões',
        convocacao=AtaPaa.CONVOCACAO_PRIMEIRA,
        parecer_conselho=AtaPaa.PARECER_APROVADA,
    )


@pytest.fixture
def ata_retificacao_ja_gerada(paa_em_retificacao, ata_paa_factory):
    return ata_paa_factory.create(
        paa=paa_em_retificacao,
        tipo_ata=AtaPaa.ATA_RETIFICACAO,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        data_reuniao=date(2024, 3, 15),
        hora_reuniao=time(14, 30),
        local_reuniao='Sala de Reuniões',
        convocacao=AtaPaa.CONVOCACAO_PRIMEIRA,
        parecer_conselho=AtaPaa.PARECER_APROVADA,
    )


@pytest.fixture
def ata_retificacao_em_processamento(paa_em_retificacao, ata_paa_factory):
    return ata_paa_factory.create(
        paa=paa_em_retificacao,
        tipo_ata=AtaPaa.ATA_RETIFICACAO,
        status_geracao_pdf=AtaPaa.STATUS_EM_PROCESSAMENTO,
    )


@pytest.fixture
def replica_padrao(paa_em_retificacao, replica_paa_factory):
    return replica_paa_factory.create(
        paa=paa_em_retificacao,
        historico={
            'texto_introducao': 'Introdução original.',
            'texto_conclusao': 'Conclusão original.',
            'objetivos': {},
            'receitas_ptrf': {},
            'receitas_pdde': {},
            'receitas_outros_recursos': {},
            'prioridades': {},
            'documento_original': {'uuid': None},
            'documento_retificado': {'uuid': None, 'versao_documento': 2},
        },
    )


@pytest.fixture
def documento_retificado_concluido(paa_em_retificacao, documento_paa_factory):
    return documento_paa_factory.create(
        paa=paa_em_retificacao,
        versao='FINAL',
        status_geracao='CONCLUIDO',
        retificacao=True,
    )


class TestValidarGeracaoAtaPaaRetificacao:

    def test_ata_completa_com_documento_retorna_valido(
        self, ata_retificacao_nao_gerada, documento_retificado_concluido, flag_factory
    ):
        """Ata de retificação preenchida e com documento final retificado concluído deve ser válida."""
        flag_factory.create(name='historico-de-membros', everyone=True)
        participante_pre = baker.make('ParticipanteAtaPaa', ata_paa=ata_retificacao_nao_gerada)
        participante_sec = baker.make('ParticipanteAtaPaa', ata_paa=ata_retificacao_nao_gerada)
        ata_retificacao_nao_gerada.presidente_da_reuniao = participante_pre
        ata_retificacao_nao_gerada.secretario_da_reuniao = participante_sec
        ata_retificacao_nao_gerada.save()

        resultado = validar_geracao_ata_paa(ata_retificacao_nao_gerada)

        assert resultado['is_valid'] is True
        assert 'mensagem' not in resultado

    def test_ata_incompleta_retorna_invalido(self, ata_retificacao_nao_gerada, documento_retificado_concluido):
        """Ata sem campos obrigatórios deve falhar com mensagem específica."""
        ata_vazia = baker.make(
            'AtaPaa',
            paa=ata_retificacao_nao_gerada.paa,
            tipo_ata=AtaPaa.ATA_RETIFICACAO,
        )

        resultado = validar_geracao_ata_paa(ata_vazia)

        assert resultado['is_valid'] is False
        assert 'Todos os dados da edição da ata devem estar preenchidos' in resultado['mensagem']

    def test_sem_documento_final_retificado_retorna_invalido(self, ata_retificacao_nao_gerada, flag_factory):
        """Ata válida, mas sem documento PAA retificado concluído, deve ser inválida."""
        flag_factory.create(name='historico-de-membros', everyone=True)
        participante_pre = baker.make('ParticipanteAtaPaa', ata_paa=ata_retificacao_nao_gerada)
        participante_sec = baker.make('ParticipanteAtaPaa', ata_paa=ata_retificacao_nao_gerada)
        ata_retificacao_nao_gerada.presidente_da_reuniao = participante_pre
        ata_retificacao_nao_gerada.secretario_da_reuniao = participante_sec
        ata_retificacao_nao_gerada.save()

        resultado = validar_geracao_ata_paa(ata_retificacao_nao_gerada)

        assert resultado['is_valid'] is False
        assert 'O documento Plano Anual deve estar gerado' in resultado['mensagem']

    def test_ata_ja_gerada_retorna_valido(
        self, ata_retificacao_ja_gerada, documento_retificado_concluido, flag_factory
    ):
        """Retificação permite regerar mesmo quando status é CONCLUIDO — não bloqueia como na apresentação."""
        flag_factory.create(name='historico-de-membros', everyone=True)
        participante_pre = baker.make('ParticipanteAtaPaa', ata_paa=ata_retificacao_ja_gerada)
        participante_sec = baker.make('ParticipanteAtaPaa', ata_paa=ata_retificacao_ja_gerada)
        ata_retificacao_ja_gerada.presidente_da_reuniao = participante_pre
        ata_retificacao_ja_gerada.secretario_da_reuniao = participante_sec
        ata_retificacao_ja_gerada.save()

        resultado = validar_geracao_ata_paa(ata_retificacao_ja_gerada)

        assert resultado['is_valid'] is True

    def test_ata_em_processamento_retorna_invalido(self, ata_retificacao_em_processamento):
        """Ata com geração em andamento não pode ser gerada novamente simultaneamente."""
        resultado = validar_geracao_ata_paa(ata_retificacao_em_processamento)

        assert resultado['is_valid'] is False
        assert 'A ata já está sendo gerada' in resultado['mensagem']


class TestSalvarLogReplica:

    def test_cria_log_com_origem_conclusao(self, paa_em_retificacao, replica_padrao):
        """Log deve ser criado com origem CONCLUSAO ao finalizar retificação."""
        log = _salvar_log_replica(paa=paa_em_retificacao, replica=replica_padrao)

        assert LogReplicaPaa.objects.filter(pk=log.pk).exists()
        assert log.origem == LogReplicaPaa.CONCLUSAO
        assert log.paa == paa_em_retificacao

    def test_log_preserva_historico_da_replica(self, paa_em_retificacao, replica_padrao):
        """O snapshot do log deve ser o historico completo da réplica."""
        log = _salvar_log_replica(paa=paa_em_retificacao, replica=replica_padrao)

        assert log.replica == replica_padrao.historico

    def test_numero_versao_extraido_do_historico(self, paa_em_retificacao, replica_padrao):
        """
        numero_versao_documento deve ser lido e incrementado de historico.documento_retificado.versao_documento.
        pois o log sempre registra o último documento/versão retificado.
        """
        log = _salvar_log_replica(paa=paa_em_retificacao, replica=replica_padrao)

        assert log.numero_versao_documento == 3

    def test_versao_padrao_quando_ausente_no_historico(self, paa_em_retificacao, replica_paa_factory):
        """Quando versao_documento não está presente no historico, deve usar 1 como padrão."""
        replica = replica_paa_factory.create(
            paa=paa_em_retificacao,
            historico={'documento_retificado': {}},
        )

        log = _salvar_log_replica(paa=paa_em_retificacao, replica=replica)

        assert log.numero_versao_documento == 1

    def test_versao_padrao_quando_historico_vazio(self, paa_em_retificacao, replica_paa_factory):
        """Historico vazio não deve causar erro — versao_documento deve ser 1."""
        replica = replica_paa_factory.create(paa=paa_em_retificacao, historico={})

        log = _salvar_log_replica(paa=paa_em_retificacao, replica=replica)

        assert log.numero_versao_documento == 1


class TestRemoverReplica:

    def test_remove_replica_do_banco(self, replica_padrao):
        """Réplica deve ser deletada do banco após chamada."""
        from sme_ptrf_apps.paa.models import ReplicaPaa

        replica_id = replica_padrao.id
        _remover_replica(replica=replica_padrao)

        assert not ReplicaPaa.objects.filter(pk=replica_id).exists()

    def test_log_replica_persiste_apos_remocao(self, paa_em_retificacao, replica_padrao):
        """Log salvo antes da remoção deve continuar existindo depois da remoção da réplica."""
        log = _salvar_log_replica(paa=paa_em_retificacao, replica=replica_padrao)
        _remover_replica(replica=replica_padrao)

        assert LogReplicaPaa.objects.filter(pk=log.pk).exists()


class TestGerarArquivoAtaPaaRetificacao:

    @pytest.fixture
    def mock_gerar_dados(self):
        with patch(
            'sme_ptrf_apps.paa.services.ata_paa_service.gerar_dados_ata_paa',
            return_value={'cabecalho': {}},
        ) as mock:
            yield mock

    @pytest.fixture
    def mock_gerar_pdf(self):
        with patch(
            'sme_ptrf_apps.paa.services.ata_paa_service.gerar_arquivo_ata_paa_pdf'
        ) as mock:
            yield mock

    @pytest.fixture
    def mock_concluir_paa(self):
        with patch(
            'sme_ptrf_apps.paa.services.ata_paa_service.PaaService.concluir_paa'
        ) as mock:
            yield mock

    def test_sucesso_retorna_ata_paa(
        self,
        ata_retificacao_nao_gerada,
        replica_padrao,
        usuario,
        mock_gerar_dados,
        mock_gerar_pdf,
        mock_concluir_paa,
    ):
        """Geração bem-sucedida deve retornar a instância de AtaPaa com mesmo uuid."""
        resultado = gerar_arquivo_ata_paa_retificacao(
            ata_paa=ata_retificacao_nao_gerada,
            usuario=usuario,
        )

        assert resultado is not None
        assert resultado.uuid == ata_retificacao_nao_gerada.uuid

    def test_sucesso_seta_status_concluido(
        self,
        ata_retificacao_nao_gerada,
        replica_padrao,
        usuario,
        mock_gerar_dados,
        mock_gerar_pdf,
        mock_concluir_paa,
    ):
        """Status da ata deve ser CONCLUIDO após geração bem-sucedida."""
        gerar_arquivo_ata_paa_retificacao(
            ata_paa=ata_retificacao_nao_gerada,
            usuario=usuario,
        )

        ata_retificacao_nao_gerada.refresh_from_db()
        assert ata_retificacao_nao_gerada.status_geracao_pdf == AtaPaa.STATUS_CONCLUIDO

    def test_sucesso_cria_log_replica_com_conclusao(
        self,
        ata_retificacao_nao_gerada,
        replica_padrao,
        usuario,
        mock_gerar_dados,
        mock_gerar_pdf,
        mock_concluir_paa,
    ):
        """Deve criar LogReplicaPaa com origem CONCLUSAO ao finalizar com sucesso."""
        gerar_arquivo_ata_paa_retificacao(
            ata_paa=ata_retificacao_nao_gerada,
            usuario=usuario,
        )

        log = LogReplicaPaa.objects.filter(
            paa=ata_retificacao_nao_gerada.paa,
            origem=LogReplicaPaa.CONCLUSAO,
        ).first()
        assert log is not None

    def test_sucesso_remove_replica(
        self,
        ata_retificacao_nao_gerada,
        replica_padrao,
        usuario,
        mock_gerar_dados,
        mock_gerar_pdf,
        mock_concluir_paa,
    ):
        """Réplica do PAA deve ser removida após conclusão bem-sucedida."""
        from sme_ptrf_apps.paa.models import ReplicaPaa

        replica_id = replica_padrao.id
        gerar_arquivo_ata_paa_retificacao(
            ata_paa=ata_retificacao_nao_gerada,
            usuario=usuario,
        )

        assert not ReplicaPaa.objects.filter(pk=replica_id).exists()

    def test_sucesso_chama_concluir_paa(
        self,
        ata_retificacao_nao_gerada,
        replica_padrao,
        usuario,
        mock_gerar_dados,
        mock_gerar_pdf,
        mock_concluir_paa,
    ):
        """PaaService.concluir_paa deve ser chamado para atualizar o status do PAA para GERADO."""
        gerar_arquivo_ata_paa_retificacao(
            ata_paa=ata_retificacao_nao_gerada,
            usuario=usuario,
        )

        mock_concluir_paa.assert_called_once_with(ata_retificacao_nao_gerada.paa)

    def test_falha_no_pdf_retorna_none(
        self,
        ata_retificacao_nao_gerada,
        usuario,
        mock_gerar_dados,
        mock_concluir_paa,
    ):
        """Exceção na geração do PDF deve fazer o service retornar None."""
        with patch(
            'sme_ptrf_apps.paa.services.ata_paa_service.gerar_arquivo_ata_paa_pdf',
            side_effect=Exception('Erro no weasyprint'),
        ):
            resultado = gerar_arquivo_ata_paa_retificacao(
                ata_paa=ata_retificacao_nao_gerada,
                usuario=usuario,
            )

        assert resultado is None

    def test_falha_no_pdf_seta_status_nao_gerado(
        self,
        ata_retificacao_nao_gerada,
        usuario,
        mock_gerar_dados,
        mock_concluir_paa,
    ):
        """Status deve ser revertido para NAO_GERADO quando a geração do PDF falha."""
        with patch(
            'sme_ptrf_apps.paa.services.ata_paa_service.gerar_arquivo_ata_paa_pdf',
            side_effect=Exception('Erro no weasyprint'),
        ):
            gerar_arquivo_ata_paa_retificacao(
                ata_paa=ata_retificacao_nao_gerada,
                usuario=usuario,
            )

        ata_retificacao_nao_gerada.refresh_from_db()
        assert ata_retificacao_nao_gerada.status_geracao_pdf == AtaPaa.STATUS_NAO_GERADO

    def test_falha_no_pdf_restaura_arquivo_anterior(
        self,
        paa_em_retificacao,
        ata_paa_factory,
        usuario,
        mock_gerar_dados,
        mock_concluir_paa,
    ):
        """Quando o PDF falha, o path do arquivo anterior deve ser restaurado no campo arquivo_pdf."""
        ata_com_arquivo = ata_paa_factory.create(
            paa=paa_em_retificacao,
            tipo_ata=AtaPaa.ATA_RETIFICACAO,
            status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
        )
        ata_com_arquivo.arquivo_pdf = 'path/to/old_file.pdf'
        ata_com_arquivo.save()

        with patch(
            'sme_ptrf_apps.paa.services.ata_paa_service.gerar_arquivo_ata_paa_pdf',
            side_effect=Exception('Falha ao gerar PDF'),
        ):
            gerar_arquivo_ata_paa_retificacao(ata_paa=ata_com_arquivo, usuario=usuario)

        ata_com_arquivo.refresh_from_db()
        assert 'old_file.pdf' in ata_com_arquivo.arquivo_pdf.name

    def test_falha_no_pdf_sem_arquivo_anterior_nao_causa_erro(
        self,
        ata_retificacao_nao_gerada,
        usuario,
        mock_gerar_dados,
        mock_concluir_paa,
    ):
        """Sem arquivo anterior, falha no PDF não deve causar erro ao restaurar (arquivo_pdf fica vazio)."""
        ata_retificacao_nao_gerada.arquivo_pdf = None
        ata_retificacao_nao_gerada.save()

        with patch(
            'sme_ptrf_apps.paa.services.ata_paa_service.gerar_arquivo_ata_paa_pdf',
            side_effect=Exception('Falha'),
        ):
            resultado = gerar_arquivo_ata_paa_retificacao(
                ata_paa=ata_retificacao_nao_gerada,
                usuario=usuario,
            )

        assert resultado is None
        ata_retificacao_nao_gerada.refresh_from_db()
        assert not ata_retificacao_nao_gerada.arquivo_pdf

    def test_falha_na_transacao_reseta_status_para_nao_gerado(
        self,
        ata_retificacao_nao_gerada,
        replica_padrao,
        usuario,
        mock_gerar_dados,
        mock_gerar_pdf,
    ):
        """Falha na transação pós-PDF deve resetar status para NAO_GERADO, permitindo nova tentativa."""
        with patch(
            'sme_ptrf_apps.paa.services.ata_paa_service.PaaService.concluir_paa',
            side_effect=Exception('Falha no concluir_paa'),
        ):
            resultado = gerar_arquivo_ata_paa_retificacao(
                ata_paa=ata_retificacao_nao_gerada,
                usuario=usuario,
            )

        assert resultado is None
        ata_retificacao_nao_gerada.refresh_from_db()
        assert ata_retificacao_nao_gerada.status_geracao_pdf == AtaPaa.STATUS_NAO_GERADO

    def test_permite_regerar_quando_ja_concluido(
        self,
        ata_retificacao_ja_gerada,
        replica_padrao,
        usuario,
        mock_gerar_dados,
        mock_gerar_pdf,
        mock_concluir_paa,
    ):
        """Ata com status CONCLUIDO deve poder ser regerada sem erro (não existe bloqueio para retificação)."""
        resultado = gerar_arquivo_ata_paa_retificacao(
            ata_paa=ata_retificacao_ja_gerada,
            usuario=usuario,
        )

        assert resultado is not None

    def test_sem_replica_nao_cria_log_e_processo_completa(
        self,
        ata_retificacao_nao_gerada,
        usuario,
        mock_gerar_dados,
        mock_gerar_pdf,
        mock_concluir_paa,
    ):
        """PAA sem réplica não deve criar log, mas o processo deve completar normalmente."""
        resultado = gerar_arquivo_ata_paa_retificacao(
            ata_paa=ata_retificacao_nao_gerada,
            usuario=usuario,
        )

        assert resultado is not None
        assert not LogReplicaPaa.objects.filter(paa=ata_retificacao_nao_gerada.paa).exists()
