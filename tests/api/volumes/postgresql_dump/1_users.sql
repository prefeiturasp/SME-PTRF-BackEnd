-- Criar usuario usr_ptrf
create role usr_ptrf login superuser password '12345qw';

alter database db_ptrf owner to usr_ptrf;