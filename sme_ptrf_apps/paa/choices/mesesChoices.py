from django.db import models


class Mes(models.IntegerChoices):
    JANEIRO = 1, 'Janeiro'
    FEVEREIRO = 2, 'Fevereiro'
    MARCO = 3, 'Março'
    ABRIL = 4, 'Abril'
    MAIO = 5, 'Maio'
    JUNHO = 6, 'Junho'
    JULHO = 7, 'Julho'
    AGOSTO = 8, 'Agosto'
    SETEMBRO = 9, 'Setembro'
    OUTUBRO = 10, 'Outubro'
    NOVEMBRO = 11, 'Novembro'
    DEZEMBRO = 12, 'Dezembro'
