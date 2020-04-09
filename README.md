# SME-PTRF-BackEnd

## Executando com docker 

- Clone o repositório
```console
$ git clone git@github.com:prefeiturasp/SME-PTRF-BackEnd.git back
```

- Entre no diretório criado
```console
$ cd back
```

- cp env_sample .env
```console
cp env-sample
```

- Execute o docker
```console
$ docker-compose -f local.yml up --build -d
```

- Crie um super usuário no container criado
```console
docker-compose -f local.yml run --rm django sh -c "python manage.py createsuperuser"
```

- Acesse a url para verificar a versão (Faça o login primeiro com o usuário criado).
```console
http://localhost:8000/api/versao
```