# Tecnologias

Esta pagina apresenta a stack principal do backend e explica o papel de cada biblioteca instalada no projeto.

## Gerenciamento com PDM

Este projeto usa PDM como gerenciador de dependencias e execucao de scripts (com base no `pyproject.toml`).

### Pre-requisitos

- Python > 3.12 instalado.
- Pip instalado e funcionando no terminal.

Exemplos de uso no projeto:

- `pdm install`: Instala dependencias.
- `pdm run dev`: Sobe o servidor Django em desenvolvimento.
- `pdm run migrate`: Aplica migracoes do banco.

### Como instalar o PDM (Caso nao tenha)

Opcoes recomendadas:

- Via Python (pip): `python -m pip install -U pdm`
- Via Windows (PowerShell + Scoop): `scoop install pdm`
- Via pipx (isolado): `pipx install pdm`

Verificacao apos instalar:

- `pdm --version`

Se não der certo, consulte a documentação oficial para mais informacoes e outras formas de instalacao:

- Documentacao oficial:
```
https://pdm-project.org/en/latest/
```

## Base da stack

- Python 3.12+
- Django 6
- Django REST Framework (DRF)
- API Oficial da Meta (WhatsApp Cloud API)
- PDM (Gerenciador de dependencias e scripts do projeto)

## Como a arquitetura usa essas bases

- Django 6: Estrutura principal do backend, configuracoes globais, ORM, migrations e ciclo de execucao.
- DRF: Camada de API REST com serializers, viewsets, APIViews, autenticacao e respostas padronizadas.
- API Oficial da Meta: Integracao de negocio para envio de mensagens, registro/verificacao de numero e processamento de webhooks.

## Dependencias instaladas e aplicacao no projeto

| Biblioteca | O que faz | Exemplo de aplicacao no projeto |
| --- | --- | --- |
| django | Framework web principal com ORM, admin, migrations e roteamento base. | Estrutura do app em `src/application` e modulos `core/*`, com modelos persistidos e URLs da API. |
| djangorestframework | Extensao REST do Django para APIs. | Uso de `ViewSet`, `APIView` e serializers nos endpoints de CRM e autenticacao. |
| drf-spectacular | Gera schema OpenAPI e UI de documentacao. | Endpoints de schema e Swagger em `/api/schema/` e `/api/docs/`. |
| python-dotenv | Carrega variaveis de ambiente de arquivo `.env`. | Leitura de tokens e configs de ambiente em desenvolvimento local. |
| django-cors-headers | Controla politicas CORS para acesso do frontend. | Permite chamadas do frontend para a API com seguranca configuravel por origem. |
| django-extensions | Comandos extras para produtividade no Django. | Uso de `shell_plus` e geracao de diagrama de modelos via script `pdm run model`. |
| pydotplus | Biblioteca para construir grafos/diagramas. | Suporte ao comando de grafo de modelos que exporta `models.png`. |
| djangorestframework-simplejwt | Implementa autenticacao JWT no DRF. | Endpoints de login e refresh token em `/api/token/` e `/api/token/refresh/`. |
| dj-database-url | Converte `DATABASE_URL` em configuracao `DATABASES` do Django. | Em `MODE=PROD`, conecta PostgreSQL a partir de uma URL unica. |
| psycopg2-binary | Driver PostgreSQL para Python/Django. | Conexao com banco PostgreSQL no ambiente de producao. |
| uvicorn | Servidor ASGI de alta performance. | Script `devweb` para executar app ASGI em cenarios de desenvolvimento web. |
| whitenoise[brotli] | Servico de arquivos estaticos com compressao. | Entrega de estaticos em deploy com suporte a compressao Brotli/Gzip. |
| gunicorn | Servidor WSGI para producao. | Execucao da aplicacao Django em ambiente Linux de producao. |
| django-filter | Filtros declarativos para queries em endpoints DRF. | Filtros de mensagens por data, categoria e texto nas rotas de CRM. |
| ipython | Shell interativo para exploracao e debug. | Apoio ao desenvolvimento via `pdm run shell` e `shell_plus`. |
| requests | Cliente HTTP para chamadas externas. | Integracao com endpoints da Meta para envio e registro de numero. |
| rapidfuzz | Comparacao textual eficiente (fuzzy matching). | Suporte a buscas/aproximacao textual em fluxos de CRM quando necessario. |

## Resumo rapido

O projeto combina Django 6 + DRF para construir a API e usa a API Oficial da Meta como integracao central de WhatsApp. O fluxo de dependencias e comandos do dia a dia e gerenciado com PDM. As bibliotecas adicionais cobrem documentacao, autenticacao, banco de dados, deploy e produtividade de desenvolvimento.
