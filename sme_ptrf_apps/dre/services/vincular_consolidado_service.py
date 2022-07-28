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
        consolidado.eh_parcial = False
        consolidado.status = ConsolidadoDRE.STATUS_GERADOS_TOTAIS
        consolidado.save()

        artefato.consolidado_dre = consolidado
        artefato.save()

        logger.info(f'Artefato {artefato} vinculado ao consolidado {consolidado.id}.')

    @classmethod
    def __obter_ou_criar_consolidado_dre(cls, periodo, dre):
        return ConsolidadoDRE.criar_ou_retornar_consolidado_dre(dre=dre, periodo=periodo, sequencia_de_publicacao=0)

