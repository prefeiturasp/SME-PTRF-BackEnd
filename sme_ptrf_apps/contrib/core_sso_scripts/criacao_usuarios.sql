/* Qual o ID da entidade */
/* Em Homologação: 6CF424DC-8EC3-E011-9B36-00155D033206 */
SELECT ent_id FROM SYS_Entidade WHERE ent_sigla = 'smesp'

/* Qual o sis_id do sistema PTRF */
/* Em Homologação: 903 */
SELECT sis_id from SYS_Sistema where sis_nome = 'PTRF'

/* Qual os ids dos grupos do PTRF */
/*
Em Homologação
440AD63B-D1D8-EA11-A740-00155D278373	UE
E3EA1B42-D1D8-EA11-A740-00155D278373	DRE
E4EA1B42-D1D8-EA11-A740-00155D278373	SME
DDA7FE96-266A-EA11-87D9-00155DC1C2E2	PTRF
*/
SELECT * FROM SYS_Grupo WHERE sis_id = 903


/* Cria a pessoa */
INSERT INTO PES_Pessoa (pes_nome, pes_sexo, pes_integridade, pes_situacao)
VALUES (
        '<nome completo>',
        '1', '1', '1')

/* Qual o ID da pessoa */
/* pes_id =  */
SELECT pes_id FROM PES_Pessoa WHERE pes_nome = '<nome completo>'

/* Cria o usuário */
/* ent_id definido em um passo anterior */
INSERT INTO SYS_Usuario (usu_login, usu_email,  usu_situacao, pes_id, ent_id)
VALUES (
        '<login do usuario>',
        '<e-mail do usuario>',
        1,
        '<pes_id do usuario>',
        '<ent_id>'
       )

/* Cria registro do usuário no PessoaDocumento*/
/* TDO_ID definido em passo anterior */
INSERT INTO PES_PessoaDocumento (pes_id, psd_numero, psd_situacao, tdo_id)
VALUES ('<pes_id do usuario>', '<cpf do usuario sem pontos>', 1, '<tdo_id>')


/*
Vinculação dos usuários aos grupos
*/

/* Inserir os vínculos ao grupo UE */
/* grupo_id de UE definido em passo anterior */
INSERT INTO SYS_UsuarioGrupo (usu_id, gru_id, usg_situacao)
SELECT
 usu_id, '<grupo_id_UE>' as gru_id, 1 as usg_situacao
FROM SYS_Usuario
WHERE
 usu_login in ('<login do usuario 1>', '<login do usuario 2>')

/* Inserir os vínculos ao grupo DRE */
/* grupo_id de DRE definido em passo anterior */
INSERT INTO SYS_UsuarioGrupo (usu_id, gru_id, usg_situacao)
SELECT
 usu_id, '<grupo_id_dre>' as gru_id, 1 as usg_situacao
FROM SYS_Usuario
WHERE
 usu_login in ('<login do usuario 1>', '<login do usuario 2>')

/* Inserir os vínculos ao grupo SME */
/* grupo_id de SME definido em passo anterior */
INSERT INTO SYS_UsuarioGrupo (usu_id, gru_id, usg_situacao)
SELECT
 usu_id, '<grupo_id_sme>' as gru_id, 1 as usg_situacao
FROM SYS_Usuario
WHERE
 usu_login in ('<login do usuario 1>', '<login do usuario 2>')

/* Inserir os vínculos ao grupo PTRF */
/* grupo_id de PTRF definido em passo anterior */
INSERT INTO SYS_UsuarioGrupo (usu_id, gru_id, usg_situacao)
SELECT
 usu_id, '<grupo_id_ptrf>' as gru_id, 1 as usg_situacao
FROM SYS_Usuario
WHERE
 usu_login in ('<login do usuario 1>', '<login do usuario 2>')


/* Usuários criados */
SELECT usu_id, usu_login, usu_email, pes_id, usu_dataCriacao FROM SYS_Usuario su WHERE usu_login in ('<login do usuario 1>', '<login do usuario 2>')
