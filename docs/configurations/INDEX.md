# Configuracoes

Esta secao centraliza a explicacao dos arquivos de configuracao do projeto em [src/application](src/application).

## Arquivos da pasta application

### __init__.py

- Funcao: Marca a pasta `application` como pacote Python.
- Observacao: Atualmente esta vazio, o que e normal quando nao ha inicializacao customizada do pacote.

### asgi.py

- Funcao: Ponto de entrada ASGI da aplicacao Django.
- O Que Faz:
- Define `DJANGO_SETTINGS_MODULE` como `application.settings`.
- Cria o objeto `application` com `get_asgi_application()`.
- Quando E Usado: Em servidores ASGI (exemplo: Uvicorn).

### urls.py

- Funcao: Mapa central de rotas HTTP da API.
- O Que Faz:
- Registra ViewSets no `DefaultRouter`.
- Define endpoints adicionais com `path(...)` para fluxos especificos (token, webhook, dispatch direto, docs, etc.).
- Quando E Usado: Sempre que uma requisicao entra na API; o Django resolve aqui qual view deve responder.

### wsgi.py

- Funcao: Ponto de entrada WSGI da aplicacao Django.
- O Que Faz:
- Define `DJANGO_SETTINGS_MODULE` como `application.settings`.
- Cria o objeto `application` com `get_wsgi_application()`.
- Quando E Usado: Em servidores WSGI (exemplo: Gunicorn em modo WSGI).

### templates/approve_invite.html

- Funcao: Tela HTML para aprovacao manual de convite de SuperAdmin.
- O Que Mostra:
- Email do usuario que solicitou permissao.
- Botao para enviar POST de aprovacao.

### templates/invite_success.html

- Funcao: Tela HTML de sucesso apos aprovacao do SuperAdmin.
- O Que Mostra:
- Mensagem de sucesso.
- Email aprovado.

### templates/invite_used.html

- Funcao: Tela HTML para token de aprovacao ja utilizado.
- O Que Mostra:
- Mensagem informando que o token ja foi aprovado anteriormente.

### templates/emails/superadmin_invite.html

- Funcao: Template de email para solicitacao de aprovacao de SuperAdmin.
- O Que Mostra:
- Email do solicitante.
- Token de aprovacao.
- Instrucao para ignorar o email caso a solicitacao nao seja reconhecida.

## settings.py (Por ultimo)

Arquivo principal de configuracao do Django. Abaixo esta o que cada variavel (e constantes relacionadas) faz.

### Inicializacao e caminhos

- `load_dotenv()`: Carrega variaveis do arquivo `.env` para `os.environ`.
- `BASE_DIR`: Caminho base do projeto (usado para montar paths de arquivos, banco SQLite, templates, etc.).

### Seguranca e ambiente

- `SECRET_KEY`: Chave criptografica do Django para assinaturas e seguranca interna.
- `DEBUG`: Liga/desliga modo de debug (detalhes de erro e comportamento de desenvolvimento).
- `ALLOWED_HOSTS` (Primeira Definicao): Lista inicial de hosts permitidos. No arquivo atual, e redefinida depois.

### Apps e autenticacao

- `INSTALLED_APPS`: Lista de apps Django e apps do projeto carregados na inicializacao.
- `AUTH_USER_MODEL`: Define o modelo de usuario customizado (`authentication.User`).

### Middleware e roteamento

- `MIDDLEWARE`: Cadeia de middlewares executada em cada requisicao/resposta (CORS, seguranca, sessao, CSRF, auth, mensagens, clickjacking).
- `ROOT_URLCONF`: Modulo raiz de URLs (`application.urls`).

### Templates e interface

- `TEMPLATES`: Configuracao do engine de templates.
- `BACKEND`: Engine de renderizacao Django.
- `DIRS`: Pasta principal de templates globais (`application/templates`).
- `APP_DIRS`: Permite buscar templates dentro dos apps.
- `OPTIONS.context_processors`: Injeta variaveis padrao em templates (`request`, `auth`, `messages`).

### Deploy WSGI

- `WSGI_APPLICATION`: Referencia ao callable WSGI (`application.wsgi.application`).

### Banco de dados e modo de execucao

- `MODE`: Le variavel de ambiente e define modo de execucao (`DEV` por padrao).
- `database_url`: Variavel local usada no bloco `MODE=PROD` para ler `DATABASE_URL`.
- `DATABASES`: Configuracao final do banco.
- Em `MODE=PROD`: Usa PostgreSQL via `dj_database_url.parse(...)`.
- Em outros modos: Usa SQLite local em `BASE_DIR / db.sqlite3`.
- `conn_max_age=600`: Mantem conexao reaproveitavel por 600 segundos no PostgreSQL.
- `ssl_require=...`: Exige SSL no Postgres quando `POSTGRES_SSL=true`.

### Senhas

- `AUTH_PASSWORD_VALIDATORS`: Lista de validadores de senha do Django.
- `UserAttributeSimilarityValidator`: Evita senha parecida com dados do usuario.
- `MinimumLengthValidator`: Exige tamanho minimo.
- `CommonPasswordValidator`: Bloqueia senhas comuns.
- `NumericPasswordValidator`: Bloqueia senha somente numerica.

### Internacionalizacao e tempo

- `LANGUAGE_CODE`: Idioma padrao (`pt-br`).
- `TIME_ZONE`: Fuso horario padrao (`America/Sao_Paulo`).
- `USE_I18N`: Ativa internacionalizacao.
- `USE_TZ`: Ativa suporte a timezone em objetos de data/hora.

### Arquivos estaticos

- `STATIC_URL`: Prefixo de URL para arquivos estaticos.

### DRF

- `REST_FRAMEWORK`: Configuracoes globais do Django REST Framework.
- `DEFAULT_SCHEMA_CLASS`: Classe de schema usada para OpenAPI (`drf-spectacular`).
- `DEFAULT_AUTHENTICATION_CLASSES`: Autenticacao padrao da API (JWT).
- `DEFAULT_FILTER_BACKENDS`: Backend padrao de filtros (`django-filter`).

### CORS e documentacao

- `CORS_ALLOW_METHODS`: Metodos HTTP permitidos por CORS.
- `SPECTACULAR_SETTINGS`: Metadados do schema OpenAPI.
- `TITLE`: Titulo da API na documentacao.
- `DESCRIPTION`: Descricao exibida na documentacao.
- `VERSION`: Versao da API no schema.
- `CORS_ALLOW_ALL_ORIGINS`: Permite todas as origens (no estado atual do arquivo, esta `True`).
- `CORS_ALLOW_CREDENTIALS`: Permite credenciais em requests cross-origin.
- `ALLOWED_HOSTS` (Segunda Definicao): Sobrescreve a definicao anterior e permite qualquer host (`['*']`).
- `CORS_ALLOW_HEADERS`: Headers aceitos em requests CORS.

### JWT

- `SIMPLE_JWT`: Configuracoes de token JWT.
- `ACCESS_TOKEN_LIFETIME`: Duracao do token de acesso (12 horas).
- `REFRESH_TOKEN_LIFETIME`: Duracao do token de refresh (1 dia).
- `AUTH_HEADER_TYPES`: Tipo de header esperado (`Bearer`).

### Email

- `EMAIL_BACKEND`: Backend SMTP do Django para envio de emails.
- `EMAIL_HOST`: Servidor SMTP (`smtp.gmail.com`).
- `EMAIL_PORT`: Porta SMTP (`587`).
- `EMAIL_USE_TLS`: Ativa TLS para transporte seguro.
- `EMAIL_HOST_USER`: Usuario SMTP vindo de variavel de ambiente.
- `EMAIL_HOST_PASSWORD`: Senha SMTP (ou senha de app) vindo de variavel de ambiente.
- `DEFAULT_FROM_EMAIL`: Remetente padrao (usa `EMAIL_HOST_USER`).
- `ADMINS_EMAILS`: Lista de emails de admin carregada de `ADMINS_EMAILS` e separada por virgula.

### Integracoes e tokens

- `VERIFY_TOKEN`: Token usado na verificacao do webhook da Meta.
- `META_APP_ID`: ID do app Meta.
- `META_APP_SECRET`: Segredo do app Meta.
- `ACCESS_TOKEN`: Token de acesso para chamadas na API da Meta.
- `WABA_ID`: ID da conta WhatsApp Business.
- `BM_ID`: ID do portfolio Business Manager.

## Observacao Importante

- O arquivo atual possui duas definicoes de `ALLOWED_HOSTS`; a segunda sobrescreve a primeira.
- Em ambiente de producao, e recomendado revisar `DEBUG`, `ALLOWED_HOSTS` e `CORS_ALLOW_ALL_ORIGINS` para configuracoes mais restritivas.
