import logging
from sme_ptrf_apps.core.models import FalhaGeracaoPc, Parametros
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FalhaGeracaoPcService:
    def __init__(self, periodo=None, usuario=None, associacao=None, prestacao_de_contas=None):
        self.__prestacao_de_contas = prestacao_de_contas
        self.__periodo = periodo
        self.__usuario = usuario
        self.__associacao = associacao
        self.__quantidade_tentativas_concluir_pc = Parametros.get().quantidade_tentativas_concluir_pc
        self.__periodo_de_tempo_tentativas_concluir_pc = Parametros.get().periodo_de_tempo_tentativas_concluir_pc

    @property
    def prestacao_de_contas(self):
        return self.__prestacao_de_contas

    @property
    def periodo(self):
        return self.__periodo

    @property
    def usuario(self):
        return self.__usuario

    @property
    def associacao(self):
        return self.__associacao

    @property
    def quantidade_tentativas_concluir_pc(self):
        return self.__quantidade_tentativas_concluir_pc

    @property
    def periodo_de_tempo_tentativas_concluir_pc(self):
        return self.__periodo_de_tempo_tentativas_concluir_pc

    def retorna_registro_falha_geracao_pc(self):
        registro_de_falha_ao_gerar_pc = FalhaGeracaoPc.objects.filter(
            associacao=self.associacao,
            periodo=self.periodo
        ).first()

        return registro_de_falha_ao_gerar_pc

    def registra_falha_geracao_pc(self):
        registro_de_falha_ao_gerar_pc = self.retorna_registro_falha_geracao_pc()

        if registro_de_falha_ao_gerar_pc:
            logger.info(f"Atualizando registro de falha {registro_de_falha_ao_gerar_pc}")
            data_hora_ultima_ocorrencia = registro_de_falha_ao_gerar_pc.data_hora_ultima_ocorrencia
            diferenca_em_minutos = datetime.now() - data_hora_ultima_ocorrencia
            diferenca_em_minutos = int(diferenca_em_minutos / timedelta(minutes=1))

            if diferenca_em_minutos > self.periodo_de_tempo_tentativas_concluir_pc:
                qtd_ocorrencias_sucessivas = 1
            else:
                qtd_ocorrencias_sucessivas = registro_de_falha_ao_gerar_pc.qtd_ocorrencias_sucessivas + 1

            registro_de_falha_ao_gerar_pc.ultimo_usuario = self.usuario
            registro_de_falha_ao_gerar_pc.data_hora_ultima_ocorrencia = datetime.now()
            registro_de_falha_ao_gerar_pc.qtd_ocorrencias_sucessivas = qtd_ocorrencias_sucessivas
            registro_de_falha_ao_gerar_pc.resolvido = False
            registro_de_falha_ao_gerar_pc.save()

        else:
            logger.info(f"Criando registro de falha")
            FalhaGeracaoPc.objects.create(
                ultimo_usuario=self.usuario,
                associacao=self.associacao,
                periodo=self.periodo,
                data_hora_ultima_ocorrencia=datetime.now(),
                qtd_ocorrencias_sucessivas=1,
            )

    def marcar_como_resolvido(self):
        registro_de_falha_ao_gerar_pc = self.retorna_registro_falha_geracao_pc()

        if registro_de_falha_ao_gerar_pc:
            logger.info(f"Marcando como resolvido registro de falha {registro_de_falha_ao_gerar_pc}")
            registro_de_falha_ao_gerar_pc.resolvido = True
            registro_de_falha_ao_gerar_pc.save()


class InfoRegistroFalhaGeracaoPc(FalhaGeracaoPcService):
    def __init__(self, associacao, usuario):
        super().__init__(associacao=associacao, usuario=usuario)

    def info_registro_falha_geracao_pc(self):

        info_list = []

        registros_de_falha_ao_gerar_pc = FalhaGeracaoPc.objects.filter(
            associacao=self.associacao,
            ultimo_usuario=self.usuario,
            resolvido=False,
        )

        for registro in registros_de_falha_ao_gerar_pc:

            periodo_referencia = registro.periodo.referencia if registro.periodo and registro.periodo.referencia else ""

            if registro.qtd_ocorrencias_sucessivas > self.quantidade_tentativas_concluir_pc:
                info = {
                    "exibe_modal": True,
                    "excede_tentativas": True,
                    "texto": f"Infelizmente um problema impediu a conclusão do período/acerto {periodo_referencia}",
                    "periodo_referencia": periodo_referencia,
                    "periodo_uuid": registro.periodo.uuid,
                    "periodo_data_final": registro.periodo.data_fim_realizacao_despesas,
                    "periodo_data_inicio": registro.periodo.data_inicio_realizacao_despesas,
                    "associacao": registro.associacao.uuid,
                    "usuario": registro.ultimo_usuario.username,
                }
                info_list.append(info)
            else:
                info = {
                    "exibe_modal": True,
                    "excede_tentativas": False,
                    "texto": f"Houve um problema na conclusão do período/acerto {periodo_referencia}. Favor concluir novamente.",
                    "periodo_referencia": periodo_referencia,
                    "periodo_uuid": registro.periodo.uuid,
                    "periodo_data_final": registro.periodo.data_fim_realizacao_despesas,
                    "periodo_data_inicio": registro.periodo.data_inicio_realizacao_despesas,
                    "associacao": registro.associacao.uuid,
                    "usuario": registro.ultimo_usuario.username,
                }
                info_list.append(info)

        return info_list
