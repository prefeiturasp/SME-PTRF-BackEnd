from waffle import get_waffle_flag_model


class FlagsService:
    def __init__(self):
        self.flags = get_waffle_flag_model()

    def flag_ativa(self, flag):
        return self.flags.objects.filter(name=flag, everyone=True).exists()
