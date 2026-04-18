# Alfa Manager CRM - Backend

Backend do CRM da Alfa Manager, focado em operacao de atendimento e disparos via WhatsApp usando a API oficial da Meta.

## Navegacao da documentacao interna

Documentacao modular criada na pasta docs:

| Link | Explicacao do que e a pagina |
| --- | --- |
| [Configurations](docs/configurations/INDEX.md) | Documentacao de configuracoes do projeto (ambiente, setup e parametros globais). |
| [Technologies](docs/technologies/INDEX.md) | Visao das tecnologias e bibliotecas utilizadas no backend. |
| [Models](docs/models/INDEX.md) | Documentacao das entidades de dominio e estrutura de dados persistida. |
| [Serializers](docs/serializers/INDEX.md) | Regras de validacao e transformacao de payloads da API. |
| [Routes](docs/routes/INDEX.md) | Mapeamento de rotas disponiveis na API. |
| [Functions](docs/functions/INDEX.md) | Funcoes utilitarias e regras de negocio auxiliares. |

## Modelagem do projeto

![Modelagem do Projeto](models.png)

## Visao geral

Este projeto foi desenvolvido para centralizar o atendimento de multiplos numeros WhatsApp de uma BM verificada em um unico CRM.

## Stack e tecnologias

### Core

- Python 3.12+
- Django 6
- Django REST Framework
- API oficial da Meta (WhatsApp Cloud API)

### Bibliotecas principais

```toml
dependencies = [
	"django>=6.0.3",
	"djangorestframework>=3.16.0",
	"drf-spectacular>=0.28.0",
	"python-dotenv>=1.1.0",
	"django-cors-headers>=4.7.0",
	"django-extensions>=4.1",
	"pydotplus>=2.0.2",
	"djangorestframework-simplejwt>=5.5.1",
	"dj-database-url>=3.0.0",
	"psycopg2-binary>=2.9.10",
	"uvicorn>=0.35.0",
	"whitenoise[brotli]>=6.6.0",
	"gunicorn>=21.2.0",
	"django-filter>=25.2",
	"ipython>=9.7.0",
	"requests>=2.32.5",
	"rapidfuzz>=3.14.5",
]
```

## Arquitetura do projeto

Arquitetura baseada em apps Django, com separacao de responsabilidades por dominio.

### Estrutura de alto nivel

```text
src/
├── manage.py
├── application/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── core/
	├── authentication/
	│   ├── models/
	│   ├── serializers/
	│   └── views/
    |   └── migrations/
	└── crm/
		├── models/
		├── serializers/
		├── views/
		│   └── webhook/
		├── filters/
		├── utils/
		│   └── metrics/
		└── migrations/
```

### Camadas no dominio CRM

- Models: entidades e regras persistidas
- Serializers: validacao e transformacao de payload
- Views: endpoints HTTP (CRUD, integracoes, acoes de negocio)
- Webhook handlers: processamento por tipo de evento da Meta
- Utils/metrics: consolidacao de metricas para dashboards

### Padrões adotados

- API REST com DRF
- ViewSets para recursos CRUD
- APIViews para fluxos especificos (ex.: verify/register, webhook, validacoes)
- Separacao de handlers de webhook por tipo de field
- Persistencia de payloads de integracao para rastreabilidade

## Banco de dados

Configuracao por variavel MODE:

- MODE=PROD: usa PostgreSQL via DATABASE_URL
- Qualquer outro valor: usa SQLite local

Exemplo de producao:

```dotenv
MODE=PROD
DATABASE_URL=postgres://usuario:senha@host:5432/database
POSTGRES_SSL=true
```

## Variaveis de ambiente principais

```dotenv
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_de_app_google
ADMINS_EMAILS=admin1@empresa.com,admin2@empresa.com
VERIFY_TOKEN=seu_token_de_verificacao_webhook

MODE=DEV
DATABASE_URL=postgres://usuario:senha@host:5432/database
POSTGRES_SSL=false

ACCESS_TOKEN=token_de_acesso_admin_gerado_pela_bm
META_APP_ID=id_do_app_publicado
META_APP_SECRET=chave_secreta_do_app_publicado
WABA_ID=id_da_conta_whatsapp_business
BM_ID=id_do_portfolio_profissional_bm
```

Notas:

- Em `MODE=PROD`, `DATABASE_URL` e obrigatoria.
- Em modo diferente de `PROD`, o projeto usa SQLite local.

## Como executar localmente

### 1. Instalar dependencias

```bash
pdm install
```

### 2. Configurar .env

Defina pelo menos MODE, credenciais Meta e configuracoes de email.

### 3. Rodar migracoes

```bash
pdm run migrate
```

### 4. Subir servidor

```bash
pdm run dev
```

## Scripts PDM

Secao de referencia para os scripts definidos em `[tool.pdm.scripts]` no `pyproject.toml`.

| Script | Comando executado | O que faz | Exemplo |
| --- | --- | --- | --- |
| `dev` | `python src/manage.py runserver` | Sobe o servidor Django em desenvolvimento. | `pdm run dev` |
| `runserver` | `python src/manage.py runserver` | Alias equivalente ao `dev`. | `pdm run runserver` |
| `createsuperuser` | `python src/manage.py createsuperuser` | Cria usuario administrador do Django. | `pdm run createsuperuser` |
| `pre_migrate` | `python src/manage.py makemigrations` | Gera novas migracoes a partir das mudancas nos models. | `pdm run pre_migrate` |
| `migrate` | `python src/manage.py migrate` | Aplica migracoes pendentes no banco de dados. | `pdm run migrate` |
| `shell` | `python src/manage.py shell` | Abre shell padrao do Django para testes rapidos. | `pdm run shell` |
| `shellp` | `python src/manage.py shell_plus` | Abre shell_plus (django-extensions) com imports automaticos. | `pdm run shellp` |
| `test` | `python src/manage.py test` | Executa a suite de testes Django. | `pdm run test` |
| `startapp` | `python src/manage.py startapp {args}` | Cria um novo app Django com nome informado. | `pdm run startapp crm_extra` |
| `loaddata` | `python src/manage.py loaddata {args}` | Carrega fixture para o banco de dados. | `pdm run loaddata fixtures/seed.json` |
| `dumpdata` | `python src/manage.py dumpdata {args}` | Exporta dados do banco em formato fixture JSON. | `pdm run dumpdata core.crm.Contact` |
| `model` | `python src/manage.py graph_models -a -g -o models.png` | Gera diagrama de modelos do projeto em imagem. | `pdm run model` |
| `req` | `pdm export -f requirements --without-hashes -o requirements.txt` | Exporta dependencias para `requirements.txt`. | `pdm run req` |
| `check` | `ruff check` | Roda lint para encontrar problemas de estilo e qualidade. | `pdm run check` |
| `pre_format` | `ruff check --fix` | Aplica correcoes automaticas suportadas pelo Ruff. | `pdm run pre_format` |
| `format` | `ruff format` | Formata o codigo seguindo padrao do Ruff Formatter. | `pdm run format` |
