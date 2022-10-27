class NotificacaoService:
    def __init__(self, dre, periodo, comentarios, enviar_email):
        self.__dre = dre
        self.__periodo = periodo
        self.__comentarios = comentarios
        self.__enviar_email = enviar_email

    @property
    def periodo(self):
        return self.__periodo

    @property
    def dre(self):
        return self.__dre

    @property
    def comentarios(self):
        return list(self.__comentarios)

    @property
    def enviar_email(self):
        return self.__enviar_email
