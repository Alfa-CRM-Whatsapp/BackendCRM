# Models

Esta secao lista todos os models existentes no projeto e resume para que cada um serve.

## Resumo

| Item | Valor |
| --- | --- |
| Total De Arquivos De Models | 10 |
| Total De Classes Model | 16 |

## Authentication

### Arquivo: [src/core/authentication/models/admin_invite.py](src/core/authentication/models/admin_invite.py)

| Model | Para Que Serve |
| --- | --- |
| SuperAdminInvite | Armazena convites de superadmin com token, email, senha hash, status de aprovacao e controle de uso. |

### Arquivo: [src/core/authentication/models/user.py](src/core/authentication/models/user.py)

| Model | Para Que Serve |
| --- | --- |
| User | Usuario customizado da aplicacao com login por email e flag de superadmin. |
| UserPreferences | Preferencias visuais do usuario, como tema e cor primaria. |

## CRM

### Arquivo: [src/core/crm/models/category.py](src/core/crm/models/category.py)

| Model | Para Que Serve |
| --- | --- |
| MessageCategory | Categoria de classificacao de mensagens por numero WhatsApp (nome, descricao, cor e status). |
| CategoryExample | Exemplo de texto usado para treinar e apoiar classificacao automatica por categoria. |

### Arquivo: [src/core/crm/models/chat.py](src/core/crm/models/chat.py)

| Model | Para Que Serve |
| --- | --- |
| Chat | Conversa entre um contato e um numero de origem, usada para agrupar mensagens inbound/outbound. |

### Arquivo: [src/core/crm/models/contact.py](src/core/crm/models/contact.py)

| Model | Para Que Serve |
| --- | --- |
| ContactWhatsapp | Contato WhatsApp (perfil, wa_id e numero), com normalizacao de telefone no save. |

### Arquivo: [src/core/crm/models/dispatch.py](src/core/crm/models/dispatch.py)

| Model | Para Que Serve |
| --- | --- |
| Dispatch | Registra disparos de template para multiplos contatos, incluindo execucao e parametros aplicados. |

### Arquivo: [src/core/crm/models/message.py](src/core/crm/models/message.py)

| Model | Para Que Serve |
| --- | --- |
| WhatsappMessage | Mensagem inbound recebida via webhook, com payload bruto, contato, numero e categoria. |
| OutboundWhatsappMessage | Mensagem outbound enviada para contato, com status de entrega, payload e rastreamento de resposta. |

### Arquivo: [src/core/crm/models/number.py](src/core/crm/models/number.py)

| Model | Para Que Serve |
| --- | --- |
| WhatsappNumber | Numero WhatsApp conectado ao sistema, com IDs da Meta, status de verificacao e dados de account update. |

### Arquivo: [src/core/crm/models/template_submission.py](src/core/crm/models/template_submission.py)

| Model | Para Que Serve |
| --- | --- |
| TemplateSubmission | Historico de tentativas de submissao de template para Meta, com status e resposta da API. |

### Arquivo: [src/core/crm/models/templates.py](src/core/crm/models/templates.py)

| Model | Para Que Serve |
| --- | --- |
| WhatsAppTemplate | Template de mensagem WhatsApp com idioma, categoria, status e qualidade. |
| TemplateComponent | Componente estrutural do template (header, body, footer, buttons). |
| TemplateParameter | Parametro dinamico de componente para placeholders e exemplos. |
| TemplateButton | Botao de template (quick reply, URL ou telefone) com ordenacao. |

## Funcoes Auxiliares Em Arquivos De Model

Mesmo nao sendo classes model, estes arquivos tambem possuem funcoes de apoio:

| Arquivo | Funcao | Para Que Serve |
| --- | --- | --- |
| [src/core/authentication/models/admin_invite.py](src/core/authentication/models/admin_invite.py) | generate_invite_code | Gera token numerico de 6 digitos para convites de superadmin. |
| [src/core/crm/models/contact.py](src/core/crm/models/contact.py) | normalize_phone | Padroniza numero telefonico para formato aceito antes de persistir. |

## Observacao

- Esta listagem foi gerada a partir da varredura atual de [src](src), cobrindo todos os arquivos em pastas models (exceto __init__.py e migrations).
