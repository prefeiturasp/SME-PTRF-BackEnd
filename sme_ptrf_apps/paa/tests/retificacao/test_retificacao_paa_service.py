import pytest

from sme_ptrf_apps.paa.models import AtaPaa, ReplicaPaa, DocumentoPaa
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.services.retificacao_paa_service import RetificacaoPaaService, ValidacaoRetificacao

pytestmark = pytest.mark.django_db


def _service(paa, username='usuario_teste'):
    user = type('User', (), {'username': username})()
    return RetificacaoPaaService(paa=paa, usuario=user)


class TestGerarSnapshot:

    def test_snapshot_contem_todas_as_secoes(self, paa_retificacao):
        snapshot = _service(paa_retificacao).gerar_snapshot()

        assert 'texto_introducao' in snapshot
        assert 'texto_conclusao' in snapshot
        assert 'objetivos_paa' in snapshot
        assert 'objetivos_globais' in snapshot
        assert 'atividades_estatutarias_paa' in snapshot
        assert 'atividades_estatutarias_globais' in snapshot
        assert 'receitas_ptrf' in snapshot
        assert 'receitas_pdde' in snapshot
        assert 'receitas_recurso_proprio' in snapshot
        assert 'receitas_outros_recursos' in snapshot
        assert 'prioridades' in snapshot

    def test_snapshot_captura_texto_introducao(self, paa_retificacao):
        snapshot = _service(paa_retificacao).gerar_snapshot()
        assert snapshot['texto_introducao'] == 'Introducao original.'

    def test_snapshot_captura_texto_conclusao(self, paa_retificacao):
        snapshot = _service(paa_retificacao).gerar_snapshot()
        assert snapshot['texto_conclusao'] == 'Conclusao original.'

    def test_snapshot_captura_objetivo(self, paa_retificacao, objetivo_no_paa):
        snapshot = _service(paa_retificacao).gerar_snapshot()

        assert str(objetivo_no_paa.uuid) in snapshot['objetivos_paa']
        assert snapshot['objetivos_paa'][str(objetivo_no_paa.uuid)]['nome'] == objetivo_no_paa.nome

    def test_snapshot_sem_objetivos_retorna_dict_vazio(self, paa_retificacao):
        snapshot = _service(paa_retificacao).gerar_snapshot()
        assert snapshot['objetivos_paa'] == {}

    def test_snapshot_captura_receita_ptrf(self, paa_retificacao, receita_ptrf_no_paa):
        snapshot = _service(paa_retificacao).gerar_snapshot()
        uuid_acao = str(receita_ptrf_no_paa.acao_associacao.uuid)

        assert uuid_acao in snapshot['receitas_ptrf']
        dados = snapshot['receitas_ptrf'][uuid_acao]
        assert 'previsao_valor_custeio' in dados
        assert 'previsao_valor_capital' in dados
        assert 'previsao_valor_livre' in dados

    def test_snapshot_captura_receita_pdde(self, paa_retificacao, receita_pdde_no_paa):
        snapshot = _service(paa_retificacao).gerar_snapshot()
        uuid_acao = str(receita_pdde_no_paa.acao_pdde.uuid)

        assert uuid_acao in snapshot['receitas_pdde']
        dados = snapshot['receitas_pdde'][uuid_acao]
        assert 'previsao_valor_custeio' in dados
        assert 'saldo_custeio' in dados

    def test_snapshot_captura_prioridade(self, paa_retificacao, prioridade_no_paa):
        snapshot = _service(paa_retificacao).gerar_snapshot()
        uuid_prioridade = str(prioridade_no_paa.uuid)

        assert uuid_prioridade in snapshot['prioridades']
        dados = snapshot['prioridades'][uuid_prioridade]
        assert 'recurso' in dados
        assert 'valor_total' in dados
        assert 'tipo_aplicacao' in dados


class TestCriarReplica:

    def test_cria_nova_replica_no_banco(self, paa_retificacao):
        assert not ReplicaPaa.objects.filter(paa=paa_retificacao).exists()

        _service(paa_retificacao).criar_replica()

        assert ReplicaPaa.objects.filter(paa=paa_retificacao).exists()

    def test_replica_criada_com_historico_do_paa(self, paa_retificacao):
        replica = _service(paa_retificacao).criar_replica()

        assert replica.historico['texto_introducao'] == 'Introducao original.'
        assert replica.historico['texto_conclusao'] == 'Conclusao original.'

    def test_get_or_create_retorna_replica_existente_sem_alterar(self, paa_retificacao, replica_paa):
        historico_original = replica_paa.historico.copy()

        # Modifica o PAA antes de chamar criar_replica novamente
        paa_retificacao.texto_introducao = 'Texto modificado depois da replica.'
        paa_retificacao.save()

        replica_retornada = _service(paa_retificacao).criar_replica()

        replica_paa.refresh_from_db()
        assert replica_retornada.pk == replica_paa.pk
        assert replica_paa.historico == historico_original

    def test_nao_cria_segunda_replica_para_o_mesmo_paa(self, paa_retificacao, replica_paa):
        _service(paa_retificacao).criar_replica()

        assert ReplicaPaa.objects.filter(paa=paa_retificacao).count() == 1


class TestCriarAtaRetificacao:

    def test_cria_ata_com_tipo_retificacao(self, paa_retificacao):
        ata = _service(paa_retificacao).criar_ata_retificacao('Minha justificativa.')

        assert ata.tipo_ata == AtaPaa.ATA_RETIFICACAO

    def test_ata_salva_justificativa(self, paa_retificacao):
        justificativa = 'Justificativa detalhada para a retificação.'
        ata = _service(paa_retificacao).criar_ata_retificacao(justificativa)

        assert ata.justificativa == justificativa

    def test_ata_associada_ao_paa(self, paa_retificacao):
        ata = _service(paa_retificacao).criar_ata_retificacao('Justificativa.')

        assert ata.paa == paa_retificacao

    def test_ata_persiste_no_banco(self, paa_retificacao):
        ata = _service(paa_retificacao).criar_ata_retificacao('Justificativa.')

        assert AtaPaa.objects.filter(pk=ata.pk).exists()


class TestIniciarRetificacao:

    def test_levanta_permission_error_quando_flag_inativa(self, paa_retificacao):
        with pytest.raises(ValidacaoRetificacao):
            _service(paa_retificacao).iniciar_retificacao('Justificativa.')

    def test_cria_replica_paa_no_banco(self, paa_factory, flag_paa_retificacao,
                                       ata_paa_factory, documento_paa_factory):
        paa_retificacao = paa_factory(
            texto_introducao='Introducao original.',
            texto_conclusao='Conclusao original.',
            status=PaaStatusEnum.GERADO.name
        )
        ata_paa_factory.create(
            paa=paa_retificacao,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        documento_paa_factory.create(
            paa=paa_retificacao,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )
        assert paa_retificacao.status == PaaStatusEnum.GERADO.name
        _service(paa_retificacao).iniciar_retificacao('Justificativa.')
        paa_retificacao.refresh_from_db()
        assert paa_retificacao.status == PaaStatusEnum.EM_RETIFICACAO.name
        assert ReplicaPaa.objects.filter(paa=paa_retificacao).exists()

    def test_cria_ata_de_retificacao_no_banco(self, paa_factory, flag_paa_retificacao,
                                              ata_paa_factory, documento_paa_factory):
        paa_retificacao = paa_factory(
            texto_introducao='Introducao original.',
            texto_conclusao='Conclusao original.',
            status=PaaStatusEnum.GERADO.name
        )
        ata_paa_factory.create(
            paa=paa_retificacao,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        documento_paa_factory.create(
            paa=paa_retificacao,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )
        _service(paa_retificacao).iniciar_retificacao('Justificativa.')

        assert AtaPaa.objects.filter(
            paa=paa_retificacao, tipo_ata=AtaPaa.ATA_RETIFICACAO
        ).exists()

    def test_ata_criada_com_justificativa_correta(self, paa_factory, flag_paa_retificacao,
                                                  ata_paa_factory, documento_paa_factory):
        paa_retificacao = paa_factory(
            texto_introducao='Introducao original.',
            texto_conclusao='Conclusao original.',
            status=PaaStatusEnum.GERADO.name
        )
        ata_paa_factory.create(
            paa=paa_retificacao,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        documento_paa_factory.create(
            paa=paa_retificacao,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )
        justificativa = 'Retificação necessária por revisão de valores.'
        _service(paa_retificacao).iniciar_retificacao(justificativa)

        assert AtaPaa.objects.filter(
            paa=paa_retificacao, tipo_ata=AtaPaa.ATA_RETIFICACAO
        ).first().justificativa == justificativa


class TestIdentificarAlteracoes:

    def test_sem_replica_retorna_dict_vazio(self, paa_retificacao):
        sem_replica = _service(paa_retificacao).identificar_alteracoes()
        assert sem_replica == {}

    def test_sem_alteracoes_retorna_dict_vazio(self, paa_retificacao, replica_paa):
        sem_alteracoes = _service(paa_retificacao).identificar_alteracoes()
        assert sem_alteracoes == {}

    def test_detecta_alteracao_em_texto_introducao(self, paa_retificacao, replica_paa):
        paa_retificacao.texto_introducao = 'Introducao alterada.'
        paa_retificacao.save()

        resultado = _service(paa_retificacao).identificar_alteracoes()

        assert 'texto_introducao' in resultado
        assert resultado['texto_introducao']['anterior'] == 'Introducao original.'
        assert resultado['texto_introducao']['atual'] == 'Introducao alterada.'

    def test_detecta_alteracao_em_texto_conclusao(self, paa_retificacao, replica_paa):
        paa_retificacao.texto_conclusao = 'Conclusao alterada.'
        paa_retificacao.save()

        resultado = _service(paa_retificacao).identificar_alteracoes()

        assert 'texto_conclusao' in resultado
        assert resultado['texto_conclusao']['anterior'] == 'Conclusao original.'
        assert resultado['texto_conclusao']['atual'] == 'Conclusao alterada.'

    def test_detecta_objetivo_adicionado(self, paa_retificacao, replica_paa, objetivo_paa_factory):
        novo_objetivo = objetivo_paa_factory(paa=paa_retificacao)
        paa_retificacao.objetivos.add(novo_objetivo)

        resultado = _service(paa_retificacao).identificar_alteracoes()

        assert 'objetivos_paa' in resultado
        assert str(novo_objetivo.uuid) in resultado['objetivos_paa']
        assert resultado['objetivos_paa'][str(novo_objetivo.uuid)]['acao'] == 'adicionado'

    def test_detecta_receita_ptrf_adicionada(self, paa_retificacao, replica_paa, receita_ptrf_no_paa):
        resultado = _service(paa_retificacao).identificar_alteracoes()

        uuid_acao = str(receita_ptrf_no_paa.acao_associacao.uuid)
        assert 'receitas_ptrf' in resultado
        assert uuid_acao in resultado['receitas_ptrf']
        assert resultado['receitas_ptrf'][uuid_acao]['acao'] == 'adicionado'

    def test_campos_texto_inalterados_nao_aparecem(self, paa_retificacao, replica_paa):
        resultado = _service(paa_retificacao).identificar_alteracoes()

        assert 'texto_introducao' not in resultado
        assert 'texto_conclusao' not in resultado

    def test_secoes_inalteradas_nao_aparecem(self, paa_retificacao, replica_paa):
        resultado = _service(paa_retificacao).identificar_alteracoes()

        assert 'objetivos_paa' not in resultado
        assert 'receitas_ptrf' not in resultado
        assert 'prioridades' not in resultado
