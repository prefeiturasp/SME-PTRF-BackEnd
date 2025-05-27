-- Criar usuario usr_coresso
create role usr_coresso login superuser password 'pNbPrJhgY96G';

alter database db_autentica_coresso owner to usr_coresso;