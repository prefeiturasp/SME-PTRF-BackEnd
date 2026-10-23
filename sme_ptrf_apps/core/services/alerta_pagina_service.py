import logging
from datetime import date

from sme_ptrf_apps.core.models import AlertaPagina, Recurso, Unidade
from sme_ptrf_apps.core.services.recursos_service import RecursoService

logger = logging.getLogger(__name__)

DIAS_EXIBICAO_ALERTA = 10  # validade do alerta


class AlertaPaginaService:

    @staticmethod
    def data_de_hoje() -> date:
        """Data atual."""
        return date.today()

    @staticmethod
    def ocorrencia_mais_recente(data_disparo: date, hoje: date) -> date | None:
        """Calcula a última ocorrência anual de uma data de disparo que não seja futura.
        Aqui, não considera o corte de exibição.

        O ano de ``data_disparo`` é o primeiro ano de vigência. Em 29/02 de ano não bissexto
        considera-se 01/03.

        Args:
            data_disparo: Data cadastrada (dia/mês se repetem todo ano).
            hoje: Data de referência.

        Returns:
            A ocorrência mais recente ou ``None`` quando ainda não houve nenhuma.
        """
        for ano in (hoje.year, hoje.year - 1):
            if ano < data_disparo.year:
                return None

            try:
                ocorrencia = date(ano, data_disparo.month, data_disparo.day)
            except ValueError:
                if data_disparo.month == 2 and data_disparo.day == 29:
                    # casos de ano bissexto
                    ocorrencia = date(ano, 3, 1)
                else:
                    logger.exception(f"Ocorreu um erro ao calcular a ocorrência de um alerta: {data_disparo}")
                    return None

            if ocorrencia <= hoje:
                return ocorrencia
        return None

    @classmethod
    def alerta_vigente(
            cls, recurso: Recurso, categoria: str, hoje: date | None = None) -> tuple[AlertaPagina, date] | None:
        """Retorna o alerta ativo com a ocorrência mais recente, não futura.
        Aqui, considera-se o corte de exibição.

        Args:
            recurso: Recurso do alerta.
            categoria: Categoria do alerta.
            hoje: Data de referência.

        Returns:
            Tuple ``(alerta, ocorrencia)`` ou ``None``.
        """
        hoje = hoje or cls.data_de_hoje()
        alertas = AlertaPagina.objects.ativos().do_recurso(recurso).da_categoria(categoria)

        candidatos = []
        for alerta in alertas:
            ocorrencia = cls.ocorrencia_mais_recente(alerta.data_disparo, hoje)
            if ocorrencia and (hoje - ocorrencia).days < DIAS_EXIBICAO_ALERTA:
                candidatos.append((ocorrencia, alerta))

        if not candidatos:
            return None

        ocorrencia, alerta = max(candidatos, key=lambda candidato: candidato[0])
        return alerta, ocorrencia

    @staticmethod
    def unidade_elegivel(unidade: Unidade, recurso: Recurso) -> bool:
        """Indica se a unidade é UE e possui o recurso informado."""
        return (
            unidade.tipo_unidade_pertence_a_grupo_ue() and
            RecursoService.disponiveis_para_unidade(unidade).filter(pk=recurso.pk).exists()
        )

    @classmethod
    def alerta_para_unidade(
            cls, unidade: Unidade, recurso: Recurso, categoria: str, hoje: date | None = None) -> dict | None:
        """Monta o alerta a ser exibindo para a unidade/recurso selecionados, ou ``None``."""
        if not cls.unidade_elegivel(unidade, recurso):
            return None

        resultado = cls.alerta_vigente(recurso, categoria, hoje)
        if not resultado:
            return None

        alerta, ocorrencia = resultado
        return {
            "uuid": alerta.uuid,
            "categoria": alerta.categoria,
            "texto": alerta.texto,
            "data_ocorrencia": ocorrencia,
            "chave": f"{alerta.uuid}:{ocorrencia.isoformat()}",
        }
