from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa


class DocumentoPaaService:
    def __init__(self, paa, usuario, previa, logger):
        self.paa = paa
        self.usuario = usuario
        self.previa = previa
        self.versao = DocumentoPaa.VersaoChoices.PREVIA if previa else DocumentoPaa.VersaoChoices.FINAL
        self.logger = logger

        self.logger.info('Inicializando DocumentoPaaService...')

    def apagar_documento_anteriores(self):
        documentos_anteriores = self.paa.documentopaa_set.all()
        self.logger.info(f'Documentos anteriores encontrados {len(documentos_anteriores)}.')

        documentos_anteriores.delete()
        self.logger.info('Documentos anteriores apagados com sucesso.')

    def criar_novo_documento(self):
        documento, _ = DocumentoPaa.objects.get_or_create(paa=self.paa, versao=self.versao)
        self.logger.info(f'Documento PAA versão {self.versao} criado com sucesso.')
        return documento

    def iniciar(self):
        self.apagar_documento_anteriores()
        documento = self.criar_novo_documento()
        return documento
