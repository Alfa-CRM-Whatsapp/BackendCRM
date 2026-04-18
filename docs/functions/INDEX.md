# Funcoes

Esta secao lista as funcoes mapeadas na varredura da pasta [src](src), com foco em `utils`, `metrics`, arquivos soltos e `defs` especiais.

## Utils (Classificacao De Mensagens)

Fonte: [src/core/crm/utils/message_classifier.py](src/core/crm/utils/message_classifier.py)

| Funcao | Para Que Serve |
| --- | --- |
| `normalize(text)` | Normaliza texto para comparacao (minusculo, sem acentos, sem caracteres especiais e com espacos padronizados). |
| `similarity(a, b)` | Calcula similaridade fuzzy entre dois textos usando multiplas estrategias da RapidFuzz. |
| `typo_bonus(a, b)` | Adiciona bonus quando a diferenca entre palavras e pequena (erro de digitacao). |
| `final_score(a, b)` | Soma similaridade base com bonus de typo para compor uma pontuacao final simples. |
| `word_score(message_text, example_text)` | Compara palavra a palavra da mensagem com exemplos para reforcar match semantico parcial. |
| `combined_score(message_text, example_text)` | Combina `final_score` e `word_score` com pesos para gerar score final de classificacao. |
| `is_duplicate(category, text)` | Verifica se o texto ja existe ou e muito parecido com exemplos da categoria. |
| `auto_learn(category, message_text)` | Auto-aprendizado: adiciona novo exemplo positivo na categoria quando regras de qualidade sao atendidas. |
| `classify_message(message_text, whatsapp_number_id, similarity_threshold=65)` | Classifica mensagem recebida na melhor categoria ativa do numero WhatsApp e retorna categoria + confianca. |

## Utils/Metrics

### Messages Metrics

Fonte: [src/core/crm/utils/metrics/messages.py](src/core/crm/utils/metrics/messages.py)

| Funcao | Para Que Serve |
| --- | --- |
| `_build_number_label(name)` | Padroniza label de numero para exibicao em cards. |
| `_get_top_category_by_messages()` | Busca a categoria com mais mensagens recebidas. |
| `_get_number_with_most_inbound()` | Busca o numero com maior volume de inbound. |
| `get_messages_metrics_cards()` | Monta os cards de metricas de mensagens para o endpoint de dashboard. |

### Categories Metrics

Fonte: [src/core/crm/utils/metrics/categories.py](src/core/crm/utils/metrics/categories.py)

| Funcao | Para Que Serve |
| --- | --- |
| `_build_number_label(number_name)` | Padroniza nome do numero para exibicao. |
| `_get_top_category_by_examples()` | Retorna categoria com maior quantidade de exemplos cadastrados. |
| `_get_top_category_by_messages()` | Retorna categoria mais frequente nas mensagens classificadas. |
| `get_categories_metrics_cards()` | Gera cards consolidados de categorias e exemplos. |

### Numbers Metrics

Fonte: [src/core/crm/utils/metrics/numbers.py](src/core/crm/utils/metrics/numbers.py)

| Funcao | Para Que Serve |
| --- | --- |
| `_build_number_label(name)` | Padroniza exibicao do nome do numero. |
| `_get_top_number_by_categories()` | Busca numero com maior quantidade de categorias vinculadas. |
| `_get_top_number_by_messages()` | Soma inbound + outbound e identifica o numero mais movimentado. |
| `get_numbers_metrics_cards()` | Monta cards de metricas de numeros cadastrados/verificados e ranking de uso. |

## Arquivos Soltos (Fora De Utils)

| Arquivo | Funcao | Para Que Serve |
| --- | --- | --- |
| [src/manage.py](src/manage.py) | `main()` | Entry-point de comandos administrativos do Django (`runserver`, `migrate`, etc.). |
| [src/core/crm/signals/message_signal.py](src/core/crm/signals/message_signal.py) | `classify_message_signal(...)` | Aciona classificacao automatica quando nova mensagem inbound e salva. |
| [src/core/crm/models/contact.py](src/core/crm/models/contact.py) | `normalize_phone(number)` | Normaliza numero para padrao esperado (incluindo DDI 55 quando aplicavel). |
| [src/core/authentication/models/admin_invite.py](src/core/authentication/models/admin_invite.py) | `generate_invite_code()` | Gera token numerico de 6 digitos para convite de SuperAdmin. |
| [src/core/authentication/managers.py](src/core/authentication/managers.py) | `create_user(...)` | Cria usuario normal no manager customizado, normalizando email e hash de senha. |
| [src/core/authentication/managers.py](src/core/authentication/managers.py) | `create_superuser(...)` | Cria superusuario preenchendo flags administrativas obrigatorias. |
| [src/core/crm/views/webhook/messages.py](src/core/crm/views/webhook/messages.py) | `handle_messages_field(value)` | Processa payload de `messages/statuses` do webhook e persiste inbound/outbound. |
| [src/core/crm/views/webhook/templates.py](src/core/crm/views/webhook/templates.py) | `handle_template_status_update(value)` | Atualiza status de template com base em evento de webhook da Meta. |
| [src/core/crm/views/webhook/templates.py](src/core/crm/views/webhook/templates.py) | `handle_template_category_update(value)` | Atualiza categoria do template quando webhook informa mudanca. |
| [src/core/crm/views/webhook/account.py](src/core/crm/views/webhook/account.py) | `_resolve_target_numbers(entry_id, value)` | Resolve quais numeros locais devem receber atualizacao de conta. |
| [src/core/crm/views/webhook/account.py](src/core/crm/views/webhook/account.py) | `handle_account_update_field(value, entry_id=None)` | Aplica atualizacoes de `account_update` nos dados do numero (status, ban, tier, etc.). |
| [src/core/crm/views/send_template_message.py](src/core/crm/views/send_template_message.py) | `build_send_components(template, parameters)` | Monta componentes de envio de template para payload da Meta. |
| [src/core/authentication/views/admin_invite.py](src/core/authentication/views/admin_invite.py) | `generate_invite_code()` (Interna) | Funcao interna usada no reenvio para gerar novo token unico de convite. |

## Defs Especiais (Helpers Privados Ou De Infra)

### Chat Helpers

Fonte: [src/core/crm/views/chat.py](src/core/crm/views/chat.py)

| Def Especial | Para Que Serve |
| --- | --- |
| `_parse_int_param(value)` | Converte parametros de query em inteiro com fallback seguro. |
| `_extract_message_text(content)` | Extrai texto pesquisavel de payloads complexos (dict/list/strings). |
| `walk(value)` (Interna) | Percorre recursivamente estruturas aninhadas para coletar trechos textuais. |
| `_normalize_search_param(value)` | Normaliza termo de busca, removendo aspas externas e espacos extras. |

### Dispatch Helpers

Fonte: [src/core/crm/views/dispatch.py](src/core/crm/views/dispatch.py)

| Def Especial | Para Que Serve |
| --- | --- |
| `_stringify_dict(data)` | Converte chaves/valores de overrides para string, evitando inconsistencias de tipo. |
| `_resolve_parameter_value(parameter, global_overrides)` | Resolve valor final de parametro de template por nome/posicao/com fallback. |
| `_render_text_with_parameters(text, parameters_payload)` | Renderiza placeholders no texto com valores resolvidos de parametros. |
| `_build_template_components_payload(...)` | Monta estrutura final de componentes/parametros/botoes para envio local. |
| `_execute_dispatch(...)` | Executa disparo para todos os contatos, cria outbounds e salva metadados de execucao. |

### Template Submission Helpers

Fonte: [src/core/crm/views/template_submission.py](src/core/crm/views/template_submission.py)

| Def Especial | Para Que Serve |
| --- | --- |
| `build_body_examples(component, template)` | Gera exemplos de corpo no formato esperado pela Meta (named ou positional). |
| `build_components_for_meta(template)` | Converte componentes locais para payload de submissao de template na Meta. |

### Outros Helpers Especificos

| Arquivo | Def Especial | Para Que Serve |
| --- | --- | --- |
| [src/core/crm/views/messages_by_contact.py](src/core/crm/views/messages_by_contact.py) | `parse_date(msg)` (Interna) | Uniformiza data/hora de inbound e outbound para ordenacao cronologica combinada. |
| [src/core/crm/filters/messages_by_number.py](src/core/crm/filters/messages_by_number.py) | `filter_text(queryset, name, value)` | Aplica filtro textual nas mensagens por numero com normalizacao de termo entre aspas. |
| [src/core/crm/apps.py](src/core/crm/apps.py) | `ready()` | Inicializa registros de signal da app CRM no startup do Django. |

## Observacao

- Esta lista cobre as funcoes identificadas em `utils`, `metrics`, arquivos soltos e helpers especiais durante a varredura atual da pasta [src](src).
- Funcoes triviais de CRUD em serializers/viewsets nao foram detalhadas aqui, pois o foco desta pagina e utilitario, metrica e suporte de infraestrutura.
