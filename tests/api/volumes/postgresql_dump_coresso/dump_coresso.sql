--
-- PostgreSQL database dump
--

-- Dumped from database version 14.6 (Debian 14.6-1.pgdg110+1)
-- Dumped by pg_dump version 14.6 (Debian 14.6-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO usr_coresso;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: usr_coresso
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO usr_coresso;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usr_coresso
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO usr_coresso;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: usr_coresso
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO usr_coresso;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usr_coresso
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO usr_coresso;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: usr_coresso
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO usr_coresso;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usr_coresso
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: authtoken_token; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.authtoken_token (
    key character varying(40) NOT NULL,
    created timestamp with time zone NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.authtoken_token OWNER TO usr_coresso;

--
-- Name: core_customuser; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.core_customuser (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    sistema_id integer
);


ALTER TABLE public.core_customuser OWNER TO usr_coresso;

--
-- Name: core_customuser_groups; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.core_customuser_groups (
    id integer NOT NULL,
    customuser_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.core_customuser_groups OWNER TO usr_coresso;

--
-- Name: core_customuser_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: usr_coresso
--

CREATE SEQUENCE public.core_customuser_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_customuser_groups_id_seq OWNER TO usr_coresso;

--
-- Name: core_customuser_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usr_coresso
--

ALTER SEQUENCE public.core_customuser_groups_id_seq OWNED BY public.core_customuser_groups.id;


--
-- Name: core_customuser_id_seq; Type: SEQUENCE; Schema: public; Owner: usr_coresso
--

CREATE SEQUENCE public.core_customuser_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_customuser_id_seq OWNER TO usr_coresso;

--
-- Name: core_customuser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usr_coresso
--

ALTER SEQUENCE public.core_customuser_id_seq OWNED BY public.core_customuser.id;


--
-- Name: core_customuser_user_permissions; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.core_customuser_user_permissions (
    id integer NOT NULL,
    customuser_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.core_customuser_user_permissions OWNER TO usr_coresso;

--
-- Name: core_customuser_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: usr_coresso
--

CREATE SEQUENCE public.core_customuser_user_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_customuser_user_permissions_id_seq OWNER TO usr_coresso;

--
-- Name: core_customuser_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usr_coresso
--

ALTER SEQUENCE public.core_customuser_user_permissions_id_seq OWNED BY public.core_customuser_user_permissions.id;


--
-- Name: core_sistema; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.core_sistema (
    id integer NOT NULL,
    nome character varying(160) NOT NULL,
    criado_em timestamp with time zone NOT NULL,
    alterado_em timestamp with time zone NOT NULL,
    uuid uuid NOT NULL,
    coresso_sistema_id character varying(8) NOT NULL
);


ALTER TABLE public.core_sistema OWNER TO usr_coresso;

--
-- Name: core_sistema_id_seq; Type: SEQUENCE; Schema: public; Owner: usr_coresso
--

CREATE SEQUENCE public.core_sistema_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.core_sistema_id_seq OWNER TO usr_coresso;

--
-- Name: core_sistema_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usr_coresso
--

ALTER SEQUENCE public.core_sistema_id_seq OWNED BY public.core_sistema.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO usr_coresso;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: usr_coresso
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO usr_coresso;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usr_coresso
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO usr_coresso;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: usr_coresso
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO usr_coresso;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usr_coresso
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO usr_coresso;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: usr_coresso
--

CREATE SEQUENCE public.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO usr_coresso;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: usr_coresso
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: usr_coresso
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO usr_coresso;

--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: core_customuser id; Type: DEFAULT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser ALTER COLUMN id SET DEFAULT nextval('public.core_customuser_id_seq'::regclass);


--
-- Name: core_customuser_groups id; Type: DEFAULT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser_groups ALTER COLUMN id SET DEFAULT nextval('public.core_customuser_groups_id_seq'::regclass);


--
-- Name: core_customuser_user_permissions id; Type: DEFAULT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.core_customuser_user_permissions_id_seq'::regclass);


--
-- Name: core_sistema id; Type: DEFAULT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_sistema ALTER COLUMN id SET DEFAULT nextval('public.core_sistema_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add Token	6	add_token
22	Can change Token	6	change_token
23	Can delete Token	6	delete_token
24	Can view Token	6	view_token
25	Can add Sistema	7	add_sistema
26	Can change Sistema	7	change_sistema
27	Can delete Sistema	7	delete_sistema
28	Can view Sistema	7	view_sistema
29	Can add user	8	add_customuser
30	Can change user	8	change_customuser
31	Can delete user	8	delete_customuser
32	Can view user	8	view_customuser
\.


--
-- Data for Name: authtoken_token; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.authtoken_token (key, created, user_id) FROM stdin;
b29062854cf3a0d831ff3fafa2adf673a043961a	2020-03-30 16:36:21.014971-03	1
4978acb1b3e7e1670f6fcef6262ba4366b737398	2020-03-31 09:22:22.993441-03	2
c2f465d8c2014e1c90d814dd2eeaf80c0e243e40	2022-08-17 18:11:20.45128-03	3
\.


--
-- Data for Name: core_customuser; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.core_customuser (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, sistema_id) FROM stdin;
1	pbkdf2_sha256$150000$udcvWklzMXAC$68+clwfLeFGuoDx6niI0xLuGKkLZSnGCPZZ7AkHvaas=	2020-12-04 11:24:32.79325-03	t	usr_amcom			usr_amcom@amcom.com.br	t	t	2020-03-30 16:36:20.836026-03	\N
2	ptrf	\N	f	ptrf	ptrf			f	t	2020-03-31 09:21:46-03	1
3	pbkdf2_sha256$150000$Cdw4X7aDOxKC$enMDg1wmqv1Hdg3k0jHsh83CB7BiAHOCU7K4/iNHs1Y=	2022-08-17 18:11:27-03	t	admin			admin@admin.com	t	t	2022-08-17 18:11:20-03	2
\.


--
-- Data for Name: core_customuser_groups; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.core_customuser_groups (id, customuser_id, group_id) FROM stdin;
\.


--
-- Data for Name: core_customuser_user_permissions; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.core_customuser_user_permissions (id, customuser_id, permission_id) FROM stdin;
\.


--
-- Data for Name: core_sistema; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.core_sistema (id, nome, criado_em, alterado_em, uuid, coresso_sistema_id) FROM stdin;
1	ptrf	2020-03-31 09:21:34.551185-03	2020-03-31 09:21:34.551206-03	adf5cc83-011d-47be-8683-1b279a702517	903
2	SIGPAE	2022-08-17 18:11:57.006549-03	2022-08-17 18:11:57.006573-03	ffaa2883-fed3-4cf2-b62c-1c3e1133204d	1004
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2020-03-31 09:21:34.554653-03	1	Nome: ptrf, CoreSSO ID: 903	1	[{"added": {}}]	7	1
2	2020-03-31 09:22:23.007371-03	2	ptrf	1	[{"added": {}}]	8	1
3	2022-08-17 18:11:57.021508-03	2	Nome: SIGPAE, CoreSSO ID: 1004	1	[{"added": {}}]	7	3
4	2022-08-17 18:12:35.955576-03	3	admin	2	[{"changed": {"fields": ["sistema"]}}]	8	3
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	contenttypes	contenttype
5	sessions	session
6	authtoken	token
7	core	sistema
8	core	customuser
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2020-03-30 11:12:22.442719-03
2	contenttypes	0002_remove_content_type_name	2020-03-30 11:12:22.47028-03
3	auth	0001_initial	2020-03-30 11:12:22.641895-03
4	auth	0002_alter_permission_name_max_length	2020-03-30 11:12:23.110577-03
5	auth	0003_alter_user_email_max_length	2020-03-30 11:12:23.167353-03
6	auth	0004_alter_user_username_opts	2020-03-30 11:12:23.194498-03
7	auth	0005_alter_user_last_login_null	2020-03-30 11:12:23.272894-03
8	auth	0006_require_contenttypes_0002	2020-03-30 11:12:23.343676-03
9	auth	0007_alter_validators_add_error_messages	2020-03-30 11:12:23.494132-03
10	auth	0008_alter_user_username_max_length	2020-03-30 11:12:23.662241-03
11	auth	0009_alter_user_last_name_max_length	2020-03-30 11:12:23.78756-03
12	auth	0010_alter_group_name_max_length	2020-03-30 11:12:23.870412-03
13	auth	0011_update_proxy_permissions	2020-03-30 11:12:23.938508-03
14	core	0001_initial	2020-03-30 11:12:24.737258-03
15	admin	0001_initial	2020-03-30 11:12:25.98755-03
16	admin	0002_logentry_remove_auto_add	2020-03-30 11:12:26.285046-03
17	admin	0003_logentry_add_action_flag_choices	2020-03-30 11:12:26.33919-03
18	authtoken	0001_initial	2020-03-30 11:12:26.378284-03
19	authtoken	0002_auto_20160226_1747	2020-03-30 11:12:26.566134-03
20	sessions	0001_initial	2020-03-30 11:12:26.774931-03
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: usr_coresso
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
fvtdmlc1ybsl8okv0ltq19rj7iud74gu	NDVjNmYwNjk5NmE3ZTU3MDQ5MWViN2JmNTk1YjExN2ZjZWI4M2Q5OTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiIyYTgxNTE5YTIxYjk1ZTNjMjlhZmZiYjY5NDI5NTRiMjA0ZWE3YjdiIn0=	2020-04-13 16:38:12.802851-03
604imq0mrdk3eqq7lp44o8l53qfwvkks	NDVjNmYwNjk5NmE3ZTU3MDQ5MWViN2JmNTk1YjExN2ZjZWI4M2Q5OTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiIyYTgxNTE5YTIxYjk1ZTNjMjlhZmZiYjY5NDI5NTRiMjA0ZWE3YjdiIn0=	2020-12-18 11:24:32.80531-03
m9dfdbwlwcp8bhv868e2foasm4ir9vc8	NDVjNmYwNjk5NmE3ZTU3MDQ5MWViN2JmNTk1YjExN2ZjZWI4M2Q5OTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiIyYTgxNTE5YTIxYjk1ZTNjMjlhZmZiYjY5NDI5NTRiMjA0ZWE3YjdiIn0=	2020-04-13 16:42:33.100953-03
kl6vojphf9zvkxq81u2j04ziesue7wxv	NDVjNmYwNjk5NmE3ZTU3MDQ5MWViN2JmNTk1YjExN2ZjZWI4M2Q5OTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiIyYTgxNTE5YTIxYjk1ZTNjMjlhZmZiYjY5NDI5NTRiMjA0ZWE3YjdiIn0=	2020-04-15 12:17:59.91459-03
tnjwl3m1awjmgv7bqog2eh7px93tpypw	NDVjNmYwNjk5NmE3ZTU3MDQ5MWViN2JmNTk1YjExN2ZjZWI4M2Q5OTp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiIyYTgxNTE5YTIxYjk1ZTNjMjlhZmZiYjY5NDI5NTRiMjA0ZWE3YjdiIn0=	2020-04-16 09:37:14.692983-03
mvyj3uqzmqpnsksuw9bbzvj4ihu20nbn	ZWE1NmZiNmUxMWJhNDc4OWQwNDM2MDdkZjc3NDdiM2M2YTJiZGNjNjp7Il9hdXRoX3VzZXJfaWQiOiIzIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiIyMjU4OTEwZjg5YWU2Mjc0OTMwZWUwOTJmN2JiZTY5OGFhMGM3NDRiIn0=	2022-08-31 18:11:27.073239-03
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usr_coresso
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usr_coresso
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usr_coresso
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 32, true);


--
-- Name: core_customuser_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usr_coresso
--

SELECT pg_catalog.setval('public.core_customuser_groups_id_seq', 1, false);


--
-- Name: core_customuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usr_coresso
--

SELECT pg_catalog.setval('public.core_customuser_id_seq', 3, true);


--
-- Name: core_customuser_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usr_coresso
--

SELECT pg_catalog.setval('public.core_customuser_user_permissions_id_seq', 1, false);


--
-- Name: core_sistema_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usr_coresso
--

SELECT pg_catalog.setval('public.core_sistema_id_seq', 2, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usr_coresso
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 4, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usr_coresso
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 8, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: usr_coresso
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 20, true);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: authtoken_token authtoken_token_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_pkey PRIMARY KEY (key);


--
-- Name: authtoken_token authtoken_token_user_id_key; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_key UNIQUE (user_id);


--
-- Name: core_customuser_groups core_customuser_groups_customuser_id_group_id_7990e9c6_uniq; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser_groups
    ADD CONSTRAINT core_customuser_groups_customuser_id_group_id_7990e9c6_uniq UNIQUE (customuser_id, group_id);


--
-- Name: core_customuser_groups core_customuser_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser_groups
    ADD CONSTRAINT core_customuser_groups_pkey PRIMARY KEY (id);


--
-- Name: core_customuser core_customuser_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser
    ADD CONSTRAINT core_customuser_pkey PRIMARY KEY (id);


--
-- Name: core_customuser_user_permissions core_customuser_user_per_customuser_id_permission_49ea742a_uniq; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser_user_permissions
    ADD CONSTRAINT core_customuser_user_per_customuser_id_permission_49ea742a_uniq UNIQUE (customuser_id, permission_id);


--
-- Name: core_customuser_user_permissions core_customuser_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser_user_permissions
    ADD CONSTRAINT core_customuser_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: core_customuser core_customuser_username_key; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser
    ADD CONSTRAINT core_customuser_username_key UNIQUE (username);


--
-- Name: core_sistema core_sistema_coresso_sistema_id_key; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_sistema
    ADD CONSTRAINT core_sistema_coresso_sistema_id_key UNIQUE (coresso_sistema_id);


--
-- Name: core_sistema core_sistema_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_sistema
    ADD CONSTRAINT core_sistema_pkey PRIMARY KEY (id);


--
-- Name: core_sistema core_sistema_uuid_key; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_sistema
    ADD CONSTRAINT core_sistema_uuid_key UNIQUE (uuid);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: authtoken_token_key_10f0b77e_like; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX authtoken_token_key_10f0b77e_like ON public.authtoken_token USING btree (key varchar_pattern_ops);


--
-- Name: core_customuser_groups_customuser_id_976bc4d7; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX core_customuser_groups_customuser_id_976bc4d7 ON public.core_customuser_groups USING btree (customuser_id);


--
-- Name: core_customuser_groups_group_id_301aeff4; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX core_customuser_groups_group_id_301aeff4 ON public.core_customuser_groups USING btree (group_id);


--
-- Name: core_customuser_sistema_id_58dca6ba; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX core_customuser_sistema_id_58dca6ba ON public.core_customuser USING btree (sistema_id);


--
-- Name: core_customuser_user_permissions_customuser_id_ebd2ce6c; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX core_customuser_user_permissions_customuser_id_ebd2ce6c ON public.core_customuser_user_permissions USING btree (customuser_id);


--
-- Name: core_customuser_user_permissions_permission_id_80ceaab9; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX core_customuser_user_permissions_permission_id_80ceaab9 ON public.core_customuser_user_permissions USING btree (permission_id);


--
-- Name: core_customuser_username_0e60666f_like; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX core_customuser_username_0e60666f_like ON public.core_customuser USING btree (username varchar_pattern_ops);


--
-- Name: core_sistema_coresso_sistema_id_b68d3139_like; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX core_sistema_coresso_sistema_id_b68d3139_like ON public.core_sistema USING btree (coresso_sistema_id varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: usr_coresso
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: authtoken_token authtoken_token_user_id_35299eff_fk_core_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.authtoken_token
    ADD CONSTRAINT authtoken_token_user_id_35299eff_fk_core_customuser_id FOREIGN KEY (user_id) REFERENCES public.core_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_customuser_groups core_customuser_grou_customuser_id_976bc4d7_fk_core_cust; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser_groups
    ADD CONSTRAINT core_customuser_grou_customuser_id_976bc4d7_fk_core_cust FOREIGN KEY (customuser_id) REFERENCES public.core_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_customuser_groups core_customuser_groups_group_id_301aeff4_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser_groups
    ADD CONSTRAINT core_customuser_groups_group_id_301aeff4_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_customuser core_customuser_sistema_id_58dca6ba_fk_core_sistema_id; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser
    ADD CONSTRAINT core_customuser_sistema_id_58dca6ba_fk_core_sistema_id FOREIGN KEY (sistema_id) REFERENCES public.core_sistema(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_customuser_user_permissions core_customuser_user_customuser_id_ebd2ce6c_fk_core_cust; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser_user_permissions
    ADD CONSTRAINT core_customuser_user_customuser_id_ebd2ce6c_fk_core_cust FOREIGN KEY (customuser_id) REFERENCES public.core_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: core_customuser_user_permissions core_customuser_user_permission_id_80ceaab9_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.core_customuser_user_permissions
    ADD CONSTRAINT core_customuser_user_permission_id_80ceaab9_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_core_customuser_id; Type: FK CONSTRAINT; Schema: public; Owner: usr_coresso
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_core_customuser_id FOREIGN KEY (user_id) REFERENCES public.core_customuser(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

