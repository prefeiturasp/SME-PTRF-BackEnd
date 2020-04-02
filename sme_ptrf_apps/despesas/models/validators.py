from django.core import validators


cpf_cnpj_validation = validators.RegexValidator(
    regex=r"(^\d{3}\.\d{3}\.\d{3}\-\d{2}$)|(^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$)",
    message="Digite o CPF ou CNPJ no formato XX.XXX.XXX/XXXX-XX ou XXX.XXX.XXX-XX.",
)
