# Serializers

Esta secao lista todos os serializers existentes no projeto e resume para que cada um serve.

## Resumo

| Item | Valor |
| --- | --- |
| Total De Arquivos De Serializers | 10 |
| Total De Classes Serializer | 30 |

## Authentication

### Arquivo: [src/core/authentication/serializers/admin_invite.py](src/core/authentication/serializers/admin_invite.py)

| Serializer | Tipo | Para Que Serve |
| --- | --- | --- |
| `SuperAdminInviteCreateSerializer` | ModelSerializer | Valida criacao de convite de superadmin e aplica hash na senha antes de salvar. |
| `SuperAdminInviteListSerializer` | ModelSerializer | Serializa dados de listagem de convites, incluindo email de quem aprovou. |
| `ApproveSuperAdminInviteSerializer` | Serializer | Valida payload de aprovacao (`email` + token numerico de 6 digitos). |
| `ResendSuperAdminInviteSerializer` | Serializer | Valida payload de reenvio de token de convite (email). |

### Arquivo: [src/core/authentication/serializers/user.py](src/core/authentication/serializers/user.py)

| Serializer | Tipo | Para Que Serve |
| --- | --- | --- |
| `UserPreferencesSerializer` | ModelSerializer | Serializa preferencias de usuario (tema e cor principal). |
| `EmailTokenObtainPairSerializer` | TokenObtainPairSerializer | Customiza resposta de login JWT para incluir dados de usuario e preferencias. |
| `UserListSerializer` | ModelSerializer | Serializa listagem resumida de usuarios com preferencias. |
| `UserCreateSerializer` | ModelSerializer | Valida criacao de usuario comum e cria preferencias padrao associadas. |

## CRM

### Arquivo: [src/core/crm/serializers/category.py](src/core/crm/serializers/category.py)

| Serializer | Tipo | Para Que Serve |
| --- | --- | --- |
| `MessageCategorySerializer` | ModelSerializer | Serializa categorias de mensagens (nome, descricao, cor, status e numero vinculado). |
| `CategoryExampleSerializer` | ModelSerializer | Serializa exemplos de categoria com categoria em modo somente leitura. |
| `CategoryExampleCreateSerializer` | ModelSerializer | Valida criacao de exemplos de categoria com referencia direta da categoria. |

### Arquivo: [src/core/crm/serializers/chat.py](src/core/crm/serializers/chat.py)

| Serializer | Tipo | Para Que Serve |
| --- | --- | --- |
| `ChatSerializer` | ModelSerializer | Serializa chat em listagem, com contato e numero remetente aninhados. |
| `ChatCreateSerializer` | ModelSerializer | Valida criacao de chat com chaves de contato e numero. |
| `ChatRetrieveSerializer` | ModelSerializer | Serializa detalhe do chat incluindo mensagens processadas via contexto. |

### Arquivo: [src/core/crm/serializers/contact.py](src/core/crm/serializers/contact.py)

| Serializer | Tipo | Para Que Serve |
| --- | --- | --- |
| `ContactWhatsappListSerializer` | ModelSerializer | Serializa dados de contato WhatsApp para respostas de API. |

### Arquivo: [src/core/crm/serializers/dispatch.py](src/core/crm/serializers/dispatch.py)

| Serializer | Tipo | Para Que Serve |
| --- | --- | --- |
| `DispatchSerializer` | ModelSerializer | Serializa dispatch com leitura rica (template/contatos) e escrita por IDs (`template_id`, `contact_ids`). |
| `DispatchExecuteSerializer` | Serializer | Valida payload de reexecucao de dispatch (`from_number` e overrides de parametros). |
| `DispatchDirectTemplateSerializer` | Serializer | Valida bloco de template no disparo direto (template + params). |
| `DispatchDirectSendSerializer` | Serializer | Valida payload completo de disparo direto (numero, contatos e template). |

### Arquivo: [src/core/crm/serializers/message.py](src/core/crm/serializers/message.py)

| Serializer | Tipo | Para Que Serve |
| --- | --- | --- |
| `WhatsappMessageListSerializer` | ModelSerializer | Serializa mensagens inbound com contato/numero/chat/categoria. |
| `WhatsappMessageCreateSerializer` | Serializer | Valida criacao de inbound e garante associacao/criacao de chat. |
| `OutboundWhatsappMessageListSerializer` | ModelSerializer | Serializa mensagens outbound com metadados de contato/numero/chat/status/template. |
| `OutboundWhatsappMessageCreateSerializer` | Serializer | Valida criacao de outbound e garante associacao/criacao de chat. |

### Arquivo: [src/core/crm/serializers/number.py](src/core/crm/serializers/number.py)

| Serializer | Tipo | Para Que Serve |
| --- | --- | --- |
| `WhatsappNumberSerializer` | ModelSerializer | Serializa configuracoes do numero WhatsApp, status de verificacao e metadados de account update. |

### Arquivo: [src/core/crm/serializers/template_submission.py](src/core/crm/serializers/template_submission.py)

| Serializer | Tipo | Para Que Serve |
| --- | --- | --- |
| `TemplateSubmissionSerializer` | ModelSerializer | Serializa tentativas de submissao de template para Meta, com resposta e status. |

### Arquivo: [src/core/crm/serializers/templates.py](src/core/crm/serializers/templates.py)

| Serializer | Tipo | Para Que Serve |
| --- | --- | --- |
| `TemplateParameterSerializer` | ModelSerializer | Serializa parametros de template e valida modo named/positional. |
| `TemplateButtonSerializer` | ModelSerializer | Serializa botoes de template e valida campos obrigatorios por tipo. |
| `TemplateComponentSerializer` | ModelSerializer | Serializa componentes do template com parametros e botoes aninhados. |
| `WhatsAppTemplateSerializer` | ModelSerializer | Serializa template completo com estrutura de componentes. |
| `SendTemplateMessageSerializer` | Serializer | Valida envio de mensagem template, resolve contato/template por ID e anexa objetos validados. |

## Observacao

- Esta listagem foi gerada a partir da varredura atual de [src](src), cobrindo todos os arquivos em pastas `serializers` (exceto `__init__.py`).
