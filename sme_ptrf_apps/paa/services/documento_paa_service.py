from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa


class DocumentoPaaService:
    def __init__(self, paa, usuario, previa, logger):
        self.paa = paa
        self.usuario = usuario
        self.previa = previa
        self.versao = DocumentoPaa.VersaoChoices.PREVIA if previa else DocumentoPaa.VersaoChoices.FINAL
        self.logger = logger
        self.documento_paa = None

        self.logger.info('Inicializando DocumentoPaaService...')

    def apagar_documento_anteriores(self):
        documentos_anteriores = self.paa.documentopaa_set.all()
        self.logger.info(f'Documentos anteriores encontrados {len(documentos_anteriores)}.')

        documentos_anteriores.delete()
        self.logger.info('Documentos anteriores apagados com sucesso.')

    def criar_novo_documento(self):
        documento, _ = DocumentoPaa.objects.get_or_create(paa=self.paa, versao=self.versao)
        self.logger.info(f'Documento PAA versão {self.versao} criado com sucesso.')
        self.documento_paa = documento

    def iniciar(self):
        self.apagar_documento_anteriores()
        self.criar_novo_documento()
        self.marcar_em_processamento()

    def marcar_em_processamento(self):
        self.documento_paa.arquivo_em_processamento()
        self.logger.info('Documento PAA em processamento')

    def marcar_concluido(self):
        self.documento_paa.arquivo_concluido()
        self.registrar_historico_acoes()
        self.logger.info('Documento PAA concluído')

    def marcar_erro(self):
        self.documento_paa.arquivo_em_erro_processamento()
        self.logger.info('Documento PAA marcado com erro no processamento')

    def registrar_historico_acoes(self):
        from sme_ptrf_apps.paa.services import PaaService
        PaaService.registra_historico_acoes(self.paa)
