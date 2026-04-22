# Alfa Manager CRM — Backend

> Backend do CRM da Alfa Manager, focado em operação de atendimento e disparos via WhatsApp usando a API oficial da Meta.

---

## Índice

- [Visão Geral](#visão-geral)
- [Stack e Tecnologias](#stack-e-tecnologias)
- [Arquitetura do Projeto](#arquitetura-do-projeto)
- [Banco de Dados](#banco-de-dados)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Como Executar Localmente](#como-executar-localmente)
- [Scripts PDM](#scripts-pdm)
- [Documentação Interna](#documentação-interna)
- [Configuração do App no Meta Developers](#configuração-do-app-no-meta-developers)

---

## Visão Geral

Este projeto foi desenvolvido para centralizar o atendimento de múltiplos números WhatsApp de uma BM verificada em um único CRM.

---

## Stack e Tecnologias

### Core

| Tecnologia | Versão |
|---|---|
| Python | 3.12+ |
| Django | 6 |
| Django REST Framework | latest |
| WhatsApp Cloud API (Meta) | oficial |

### Dependências principais

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

---

## Arquitetura do Projeto

Arquitetura baseada em apps Django, com separação de responsabilidades por domínio.

### Estrutura de alto nível

```
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
    │   ├── views/
    │   └── migrations/
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

### Camadas do domínio CRM

| Camada | Responsabilidade |
|---|---|
| **Models** | Entidades e regras persistidas |
| **Serializers** | Validação e transformação de payload |
| **Views** | Endpoints HTTP (CRUD, integrações, ações de negócio) |
| **Webhook handlers** | Processamento por tipo de evento da Meta |
| **Utils / Metrics** | Consolidação de métricas para dashboards |

### Padrões adotados

- API REST com DRF
- `ViewSets` para recursos CRUD
- `APIViews` para fluxos específicos (ex.: verify/register, webhook, validações)
- Separação de handlers de webhook por tipo de field
- Persistência de payloads de integração para rastreabilidade

### Modelagem

![Modelagem do Projeto](models.png)

---

## Banco de Dados

O banco de dados é configurado via variável `MODE`:

| Valor de `MODE` | Banco utilizado |
|---|---|
| `PROD` | PostgreSQL via `DATABASE_URL` |
| Qualquer outro | SQLite local |

**Exemplo de configuração para produção:**

```dotenv
MODE=PROD
DATABASE_URL=postgres://usuario:senha@host:5432/database
POSTGRES_SSL=true
```

---

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```dotenv
# ── Servidor ──────────────────────────────────────────────
SECRET_KEY=chave_secreta_para_django
DEBUG=true
ALLOWED_HOSTS=localhost,meudominio.com

# ── Banco de dados ────────────────────────────────────────
MODE=DEV
DATABASE_URL=postgres://usuario:senha@host:5432/database
POSTGRES_SSL=false

# ── E-mail ────────────────────────────────────────────────
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_de_app_google
ADMINS_EMAILS=admin1@empresa.com,admin2@empresa.com

# ── Meta / WhatsApp ───────────────────────────────────────
VERIFY_TOKEN=seu_token_de_verificacao_webhook
ACCESS_TOKEN=token_de_acesso_admin_gerado_pela_bm
META_APP_ID=id_do_app_publicado
META_APP_SECRET=chave_secreta_do_app_publicado
WABA_ID=id_da_conta_whatsapp_business
BM_ID=id_do_portfolio_profissional_bm
```

> **Atenção:** Em `MODE=PROD`, a variável `DATABASE_URL` é obrigatória. Em outros modos, o projeto usa SQLite local automaticamente.

---

## Como Executar Localmente

### Pré-requisitos

- Python 3.12+ instalado
- PDM instalado ([ver instalação](#instalando-o-pdm))

### Instalando o PDM

Consulte a [documentação oficial do PDM](https://pdm-project.org/en/latest/) e siga as instruções para o seu sistema operacional.

Após instalar, verifique com:

```bash
pdm --version
```

### Passo a passo

**1. Instalar dependências**

```bash
pdm install
```

**2. Configurar variáveis de ambiente**

```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

**3. Aplicar migrações**

```bash
pdm run migrate
```

**4. Subir o servidor**

```bash
pdm run dev
```

---

## Scripts PDM

Referência completa dos scripts definidos em `[tool.pdm.scripts]` no `pyproject.toml`.

### Servidor

| Script | O que faz | Exemplo |
|---|---|---|
| `dev` | Sobe o servidor Django em desenvolvimento | `pdm run dev` |
| `runserver` | Alias equivalente ao `dev` | `pdm run runserver` |

### Banco de Dados

| Script | O que faz | Exemplo |
|---|---|---|
| `pre_migrate` | Gera novas migrações a partir das mudanças nos models | `pdm run pre_migrate` |
| `migrate` | Aplica migrações pendentes no banco de dados | `pdm run migrate` |
| `loaddata` | Carrega fixture para o banco de dados | `pdm run loaddata fixtures/seed.json` |
| `dumpdata` | Exporta dados do banco em formato fixture JSON | `pdm run dumpdata core.crm.Contact` |

### Usuários

| Script | O que faz | Exemplo |
|---|---|---|
| `createsuperuser` | Cria usuário administrador do Django | `pdm run createsuperuser` |

### Shell / Debug

| Script | O que faz | Exemplo |
|---|---|---|
| `shell` | Abre shell padrão do Django | `pdm run shell` |
| `shellp` | Abre shell_plus com imports automáticos | `pdm run shellp` |
| `test` | Executa a suite de testes Django | `pdm run test` |

### Geração / Exportação

| Script | O que faz | Exemplo |
|---|---|---|
| `model` | Gera diagrama de models em `models.png` | `pdm run model` |
| `req` | Exporta dependências para `requirements.txt` | `pdm run req` |
| `startapp` | Cria um novo app Django | `pdm run startapp crm_extra` |

### Qualidade de Código

| Script | O que faz | Exemplo |
|---|---|---|
| `check` | Lint com Ruff — encontra problemas de estilo | `pdm run check` |
| `pre_format` | Aplica correções automáticas via Ruff | `pdm run pre_format` |
| `format` | Formata o código com Ruff Formatter | `pdm run format` |

---

## Documentação Interna

Documentação modular disponível na pasta `docs/`:

| Documento | Conteúdo |
|---|---|
| [Configurations](docs/configurations/INDEX.md) | Configurações do projeto (ambiente, setup e parâmetros globais) |
| [Technologies](docs/technologies/INDEX.md) | Visão das tecnologias e bibliotecas utilizadas |
| [Models](docs/models/INDEX.md) | Entidades de domínio e estrutura de dados persistida |
| [Serializers](docs/serializers/INDEX.md) | Regras de validação e transformação de payloads da API |
| [Routes](docs/routes/INDEX.md) | Mapeamento de rotas disponíveis na API |
| [Functions](docs/functions/INDEX.md) | Funções utilitárias e regras de negócio auxiliares |

---

## Configuração do App no Meta Developers

### Pré-requisitos obrigatórios

Antes de começar, certifique-se de que você possui:

| Requisito | Detalhe |
|---|---|
| ✅ **BM Verificada** | Obrigatório para uso em produção. Sem isso, não é possível integrar com a API da Meta |
| ✅ **Método de pagamento** | A BM precisa de pagamento vinculado para habilitar envio de mensagens |
| ✅ **Número verificado** | Necessário para envio dentro ou fora da janela de 24h, via template ou direto |

> Apps em sandbox têm muitas limitações e **não são adequados para uso real.**

---

### Parte 1 — Criando o App

#### 1. Acesse o Meta Developers

Acesse [developers.facebook.com](https://developers.facebook.com/) e faça login.

#### 2. Crie um novo App

No painel, clique em **"Meus Apps"** → **"Criar App"**.

![Criar App](./docs/images/developers_app.png)

Preencha o **nome do app** e o **e-mail responsável**, depois avance.

#### 3. Escolha o tipo correto

> ⚠️ Selecione **obrigatoriamente** a opção abaixo — sem ela, o app não servirá para este projeto.

**"Conectar-se com clientes pelo WhatsApp"**

![Tipo de App](./docs/images/whats_connect.png)

#### 4. Vincule ao portfólio da BM

Selecione o **portfólio profissional da BM Verificada** que deseja usar e avance.

Em "Requisitos" não há nada para configurar — apenas avance e finalize a criação.

---

### Parte 2 — Credenciais do App

#### 5. Acesse as configurações básicas

Com o app criado, vá em **Configurações do App** → **Básico**.

![Configurações do App](./docs/images/configs.png)

#### 6. Copie as credenciais

Nessa seção você encontrará:

| Campo no painel | Variável no `.env` |
|---|---|
| ID do App | `META_APP_ID` |
| Chave Secreta do App | `META_APP_SECRET` |

#### 7. Publique o App

Para publicar, o app precisa ter obrigatoriamente:

- URL de política de privacidade
- URL dos termos de serviço
- Ícone do aplicativo **1024×1024px** sem fundo branco

---

### Parte 3 — Permissões e Webhook

#### 8. Acesse os casos de uso

Vá em **Casos de Uso** → **Personalizar caso de uso** e selecione o caso do WhatsApp que foi ativado na criação.

![Casos de Uso](./docs/images/casos.png)

#### 9. Ative as permissões necessárias

Em **"Permissões e recursos"**, ative todas as permissões conforme a imagem abaixo:

![Permissões](./docs/images/perms.png)

#### 10. Configure o Webhook

Acesse **Webhooks** → **Configurar Webhooks** e preencha:

| Campo | Valor |
|---|---|
| **URL de callback** | URL do seu backend + `/api/webhook/whatsapp/` |
| **Token de verificação** | Valor definido em `VERIFY_TOKEN` no `.env` |

**Exemplo de URL:**
```
https://meu-backend.com/api/webhook/whatsapp/
```

![Webhook](./docs/images/webhook.png)

Após verificar, o `GET` retornará `200` e o webhook estará ativo.

#### 11. Ative os eventos do webhook

Após a verificação, ative os seguintes eventos para que a Meta envie notificações ao backend:

```
account_settings_update
account_update
phone_number_quality_update
message_template_components_update
message_template_category_update
message_template_status_update
messages
template_category_update
template_correct_category_detection
```

---

### Parte 4 — Access Token

#### 12. Gere o token de acesso permanente

O `ACCESS_TOKEN` é gerado nas configurações da própria BM.

![Token de Acesso](./docs/images/token.png)

**Passo a passo:**

1. Nas configurações da BM, acesse **Usuários do Sistema**
2. Adicione um usuário do sistema com perfil **Admin**
3. Atribua **todos os ativos do app** a esse usuário
4. Avance até o final — a BM irá gerar um **token permanente**
5. Salve o token no `.env` como `ACCESS_TOKEN`

---

### Resumo das variáveis obtidas neste processo

| Variável | Onde obter |
|---|---|
| `META_APP_ID` | Configurações do App → Básico |
| `META_APP_SECRET` | Configurações do App → Básico |
| `VERIFY_TOKEN` | Definido por você, inserido no webhook |
| `ACCESS_TOKEN` | BM → Usuários do Sistema → Token permanente |
| `WABA_ID` | Painel do WhatsApp Business na BM |
| `BM_ID` | Configurações da Business Manager |

---

> Em caso de dúvidas ou erros, entre em contato com o desenvolvedor responsável.

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
| `model` | `python src/manage.py graph_models -a -g -o models.png` | Gera diagrama de modelos do projeto em imagem. | `pdm run model` |
| `req` | `pdm export -f requirements --without-hashes -o requirements.txt` | Exporta dependencias para `requirements.txt`. | `pdm run req` |
| `check` | `ruff check` | Roda lint para encontrar problemas de estilo e qualidade. | `pdm run check` |
| `pre_format` | `ruff check --fix` | Aplica correcoes automaticas suportadas pelo Ruff. | `pdm run pre_format` |
| `format` | `ruff format` | Formata o codigo seguindo padrao do Ruff Formatter. | `pdm run format` |