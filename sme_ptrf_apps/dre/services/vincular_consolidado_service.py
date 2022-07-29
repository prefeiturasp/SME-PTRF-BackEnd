from sme_ptrf_apps.dre.models import RelatorioConsolidadoDRE, AtaParecerTecnico, Lauda, ConsolidadoDRE

import logging

logger = logging.getLogger(__name__)


class VincularConsolidadoServiceException(Exception):
    pass


class VincularConsolidadoService:

    @classmethod
    def vincular_artefato(cls, artefato):
        if not (
            isinstance(artefato, RelatorioConsolidadoDRE) or
            isinstance(artefato, AtaParecerTecnico) or
            isinstance(artefato, Lauda)
        ):
            mensagem = 'Artefato precisa ser um RelatorioConsolidadoDRE, AtaParecerTecnico ou Lauda.'
            logger.error(mensagem)
            raise VincularConsolidadoServiceException(mensagem)

        consolidado = cls.__obter_ou_criar_consolidado_dre(periodo=artefato.periodo, dre=artefato.dre)

        artefato.consolidado_dre = consolidado

        if isinstance(artefato, AtaParecerTecnico):
            artefato.sequencia_de_publicacao = consolidado.sequencia_de_publicacao

        artefato.save()

        logger.info(f'Artefato {artefato} vinculado ao consolidado {consolidado.id}.')

    @classmethod
    def __obter_ou_criar_consolidado_dre(cls, periodo, dre):
        consolidado_dre = ConsolidadoDRE.objects.filter(dre=dre, periodo=periodo).order_by("sequencia_de_publicacao").last()
        if not consolidado_dre:
            consolidado_dre = ConsolidadoDRE.criar_ou_retornar_consolidado_dre(dre=dre, periodo=periodo, sequencia_de_publicacao=0)
            consolidado_dre.eh_parcial = False
            consolidado_dre.status = ConsolidadoDRE.STATUS_GERADOS_TOTAIS
            consolidado_dre.save()

        return consolidado_dre
