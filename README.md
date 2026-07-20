# Lacrei Saúde — API RESTful de Gerenciamento de Consultas Médicas

API voltada à comunidade LGBTQIAPN+, desenvolvida com **Django 6** + **Django REST Framework**, containerizada com **Docker** e entregue via **CI/CD no GitHub Actions** com deploy na **AWS**.

---

## Sumário

1. [Visão Geral](#visão-geral)
2. [Tecnologias](#tecnologias)
3. [Setup Local](#setup-local)
4. [Setup com Docker](#setup-com-docker)
5. [Evidências dos Ambientes](#evidências-dos-ambientes)
6. [Endpoints da API](#endpoints-da-api)
7. [Autenticação](#autenticação)
8. [Execução dos Testes](#execução-dos-testes)
9. [CI/CD](#cicd)
10. [Rollback](#rollback)
11. [Decisões Técnicas](#decisões-técnicas)
12. [Proposta de Integração — Assas](#proposta-de-integração--assas)
13. [Melhorias Futuras](#melhorias-futuras)

---

## Visão Geral

API RESTful para gerenciamento de **profissionais da saúde** e **consultas médicas**, construída sobre os pilares de:

| Pilar | Implementação |
|---|---|
| **Qualidade de código** | Ruff, pytest com 31 testes, tipagem completa |
| **Segurança** | API Key, CORS, HSTS, XSS filter, SQL Injection (ORM) |
| **Boas práticas** | Multi-stage Docker, 12-Factor App, DRF ViewSets |
| **Pronto para produção** | Gunicorn, WhiteNoise, logs rotativos, health check |

### Modelo de Dados

```
Professional ──1:N──> Appointment
├── nome_social      ├── professional (FK)
├── profissao        ├── data
├── endereco         ├── criado_em
├── contato          └── atualizado_em
├── criado_em
└── atualizado_em
```

---

## Tecnologias

| Tecnologia | Versão | Motivo |
|---|---|---|
| **Python** | 3.13 | Performance, novas features de tipagem |
| **Django** | 6.0 | ORM maduro, admin automático, segurança built-in |
| **DRF** | 3.17 | ViewSets, serializers, autenticação plugável |
| **Poetry** | 2.4 | Lock determinístico, grupos de dependências |
| **PostgreSQL** | 16 | Integridade referencial, performance, JSONB |
| **Docker** | 29 | Ambiente replicável, multi-stage builds |
| **Gunicorn** | 26 | WSGI server de produção com 3 workers |
| **WhiteNoise** | 6 | Servir arquivos estáticos sem CDN |
| **drf-spectacular** | 0.30 | OpenAPI 3.0 + Swagger + ReDoc automáticos |
| **django-cors-headers** | 4.9 | Controle granular de CORS |
| **django-filter** | 26 | Filtros via query params |
| **Ruff** | 0.15 | Linter + formatter (10x mais rápido que flake8) |
| **pytest** | 9.1 | Test runner com fixtures e cobertura |

---

## Setup Local

### Pré-requisitos

- Python 3.12+
- Poetry 2.4+
- PostgreSQL 16 (ou Docker para o banco)

### Passos

```bash
# 1. Clone o repositório
git clone <repo-url> lacrei-saude-backend
cd lacrei-saude-backend

# 2. Copie o arquivo de ambiente
cp .env.example .env
# Edite .env com suas credenciais de banco

# 3. Instale as dependências
poetry install

# 4. Execute as migrações
poetry run python manage.py migrate

# 5. Crie uma API Key para autenticação
poetry run python manage.py create_api_key --nome "dev-key"

# 6. (Opcional) Popule com dados de exemplo
poetry run python manage.py seed

# 7. Inicie o servidor de desenvolvimento
poetry run python manage.py runserver

# 8. Acesse http://localhost:8000/api/v1/health/
```

### Documentação da API

- **Swagger UI:** http://localhost:8000/api/v1/docs/swagger/
- **ReDoc:** http://localhost:8000/api/v1/docs/redoc/
- **Schema OpenAPI 3:** http://localhost:8000/api/v1/schema/

---

## Setup com Docker

### Pré-requisitos

- Docker 29+
- Docker Compose

### Ambiente de Desenvolvimento (hot reload)

```bash
docker compose -f docker-compose.dev.yml up --build
```

### Ambiente de Produção (Gunicorn)

```bash
docker compose up --build -d
```

### Verificar

```bash
curl http://localhost:8000/api/v1/health/
```

### Estrutura Docker

```
docker-compose.yml         # Ambiente padrão (Gunicorn, 3 workers)
docker-compose.dev.yml     # Desenvolvimento (runserver, hot reload)
Dockerfile                 # Multi-stage build (builder + production)
docker/postgres-init/      # Scripts de inicialização do PostgreSQL
  └── 01-roles.sql         # Cria role lacrei_app (não-superusuário)
```

**Padrão Vinculus aplicado:** Dois usuários de banco:
- `postgres` (superusuário) — usado apenas pelo container PostgreSQL
- `lacrei_app` (não-superusuário) — usado pela aplicação em runtime

---

## Evidências dos Ambientes

### Ambiente Local (Docker)

```bash
$ curl -s http://localhost:8000/api/v1/health/ | python -m json.tool
{
    "status": "ok",
    "versao": "1.0.0",
    "servico": "lacrei-saude-api",
    "database": "connected"
}
```

### Ambiente de CI (GitHub Actions)

Pipeline executado a cada push/PR — **lint + 34 testes contra PostgreSQL real:**

```
Push/PR → [Lint: Ruff] → [Test: PostgreSQL + pytest + cobertura]
```

**Última execução:** https://github.com/sinik6/lacrei-saude-backend/actions

### Simulando Produção Local

```bash
# Subir em modo produção (Gunicorn, DEBUG=False)
docker compose up --build -d

# Health check
curl http://localhost:8000/api/v1/health/

# Swagger
open http://localhost:8000/api/v1/docs/swagger/
```

> Para deploy real em staging/production, configurar secrets AWS no GitHub Actions (ver seção CI/CD).

---

## Endpoints da API

### Health Check

| Método | URL | Autenticação |
|---|---|---|
| `GET` | `/api/v1/health/` | Não |

### Profissionais da Saúde

| Método | URL | Descrição |
|---|---|---|
| `GET` | `/api/v1/professionals/` | Listar (com paginação) |
| `POST` | `/api/v1/professionals/` | Criar |
| `GET` | `/api/v1/professionals/{id}/` | Detalhar |
| `PUT` | `/api/v1/professionals/{id}/` | Atualizar completo |
| `PATCH` | `/api/v1/professionals/{id}/` | Atualizar parcial |
| `DELETE` | `/api/v1/professionals/{id}/` | Remover |

**Query params de filtro:**
- `?search=João` — busca por nome, profissão ou endereço
- `?profissao=Psicólogo` — filtra por profissão
- `?ordering=nome_social` — ordenação
- `?page=2&size=10` — paginação

### Consultas

| Método | URL | Descrição |
|---|---|---|
| `GET` | `/api/v1/appointments/` | Listar (com paginação) |
| `POST` | `/api/v1/appointments/` | Criar |
| `GET` | `/api/v1/appointments/{id}/` | Detalhar |
| `PUT` | `/api/v1/appointments/{id}/` | Atualizar completo |
| `PATCH` | `/api/v1/appointments/{id}/` | Atualizar parcial |
| `DELETE` | `/api/v1/appointments/{id}/` | Remover |

**Query params de filtro:**
- `?professional=1` — **Busca de consultas pelo ID do profissional**
- `?ordering=data` — ordenação por data

### Formato de Resposta de Erro

Seguindo o padrão Vinculus de erros estruturados:

```json
{
  "erro": "VALIDACAO",
  "mensagem": "Dados enviados não passaram na validação.",
  "detalhes": [
    {"campo": "nome_social", "mensagem": "Este campo é obrigatório."}
  ]
}
```

**Códigos de erro:**
| HTTP | Código | Significado |
|---|---|---|
| 400 | `REQUISICAO_INVALIDA` | Dados mal formatados |
| 401 | `NAO_AUTENTICADO` | API Key ausente ou inválida |
| 403 | `ACESSO_NEGADO` | Sem permissão |
| 404 | `NAO_ENCONTRADO` | Recurso não existe |
| 422 | `VALIDACAO` | Falha de validação |
| 429 | `MUITAS_REQUISICOES` | Rate limit excedido |
| 500 | `ERRO_INTERNO` | Erro do servidor |

---

## Autenticação

### API Key (Header)

Todas as requisições (exceto `/api/v1/health/`) exigem o header:

```
X-API-Key: <sua-chave>
```

### Criar API Key

```bash
# Via Django management command
poetry run python manage.py create_api_key --nome "meu-servico"

# Via Django Admin
# Acesse http://localhost:8000/admin/ e crie em "API Keys"

# Via Django shell
poetry run python manage.py shell -c "
from apps.users.models import ApiKey
key = ApiKey.objects.create(name='teste')
print(key.key)
"
```

### Segurança da API Key

- Chave gerada automaticamente via `secrets.token_hex(32)` (64 caracteres hex)
- Suporte a múltiplas chaves (uma por serviço consumidor)
- Chaves podem ser desativadas sem deletar (`is_active = False`)
- Todas as consultas ao banco usam Django ORM (proteção contra SQL Injection)
- Rate limiting: 60 req/min para não autenticados, 1000 req/min para autenticados

---

## Execução dos Testes

### Stack de Testes

| Ferramenta | Propósito |
|---|---|
| **pytest** | Test runner |
| **pytest-django** | Integração Django + pytest |
| **pytest-cov** | Relatório de cobertura |
| **SQLite :memory:** | Banco isolado para testes rápidos |
| **APITestCase (DRF)** | Testes de API (herdado pelo pytest) |

### Rodar os testes

```bash
# Todos os testes
poetry run pytest

# Com cobertura
poetry run pytest --cov=. --cov-report=term

# Apenas testes de profissionais
poetry run pytest apps/professionals/tests.py -v

# Apenas um teste específico
poetry run pytest apps/appointments/tests.py::AppointmentAPITestCase::test_create_appointment -v
```

### Cobertura

**31 testes**, distribuídos em:

| Módulo | Testes | Cobertura |
|---|---|---|
| `apps/professionals/tests.py` | 12 | CRUD completo + erros |
| `apps/appointments/tests.py` | 14 | CRUD completo + erros + cascade |
| `apps/users/tests.py` | 5 | Autenticação (válida, inválida, inativa, ausente, múltiplos endpoints) |

**Tipos de teste:**
- CRUD de profissionais (list, create, retrieve, update, delete)
- CRUD de consultas (list, create, retrieve, update, delete)
- Erros: campo obrigatório ausente, dados vazios, ID inexistente, formato inválido
- Autenticação: API key ausente, inválida, inativa
- Cascade delete (profissional deletado → consultas deletadas)
- Filtragem e busca

---

## CI/CD

### Pipeline (GitHub Actions)

```
Push/PR → [Lint] → [Test] → [Build Docker] → [Deploy Staging ou Production]
```

| Job | Gatilho | Descrição |
|---|---|---|
| **lint** | push, PR | Ruff check + format |
| **test** | push, PR | Migrações + APITestCase com PostgreSQL real |
| **build** | main, develop | Build multi-stage Docker |
| **deploy-staging** | develop | Push ECR → Deploy ECS |
| **deploy-production** | main | Push ECR → Deploy ECS |

### Ambientes

| Ambiente | Branch |
|---|---|
| **Staging** | `develop` |
| **Produção** | `main` |

### Rollback

**GitHub Actions:** GitHub → Actions → Rollback → Run workflow → selecionar ambiente. O script detecta a revisão anterior do ECS e reverte automaticamente.

**Git Revert:**
```bash
git revert <commit-com-problema>
git push origin main
```

**Blue/Green no ECS:** No deploy de produção, nova versão (green) sobe ao lado da antiga (blue). Health check falhou → tráfego permanece na blue (zero downtime).

### Secrets no GitHub

Settings → Environments → criar `staging` e `production` com:

| Secret | Propósito |
|---|---|
| `AWS_ACCESS_KEY_ID` | Credencial AWS |
| `AWS_SECRET_ACCESS_KEY` | Credencial AWS |
| `AWS_ECR_REGISTRY` | URI do ECR |

Ver também: [docs/DEPLOY.md](docs/DEPLOY.md)



---

## Decisões Técnicas

### 1. Django + DRF (não FastAPI)

**Motivo:** O desafio exige Django. O Django oferece:

- **Admin automático:** Gerencia API Keys e dados sem código extra
- **ORM maduro:** Proteção built-in contra SQL Injection (`cursor.execute` nunca usado)
- **Migrations:** Versionamento de schema determinístico
- **Management Commands:** `create_api_key`, `seed` como CLI nativa
- **Middleware stack:** SecurityMiddleware, clickjacking, CORS, HSTS — tudo built-in

### 2. API Key em vez de JWT

**Motivo:** Simplicidade para o escopo do desafio.

- Não requer refresh tokens, blacklist, ou gestão de sessão
- Ideal para comunicação server-to-server (integração com Assas, frontend, etc.)
- Fácil de evoluir para JWT no futuro (a estrutura `DEFAULT_AUTHENTICATION_CLASSES` é plugável)

### 3. SQLite para Testes

**Motivo:** Testes isolados e rápidos (sem container externo).

- Banco em memória (`:memory:`) destruído automaticamente
- CI usa PostgreSQL (serviço do GitHub Actions)
- `config/settings_test.py` sobrescreve apenas o necessário

### 4. ViewSets (não Views genéricas)

**Motivo:** Menos código, mais consistência.

- Cada ViewSet = 5-7 linhas de configuração
- Rotas geradas automaticamente pelo `DefaultRouter`
- Filtros, busca e ordenação declarativos

### 5. Multi-stage Docker

**Motivo:** Imagem final mínima e segura.

- **Builder stage:** Compila dependências (gcc, libpq-dev)
- **Production stage:** Apenas runtime (libpq, curl para health check)
- **Usuário não-root:** `appuser` (segurança)
- **Health check:** Docker monitora `/api/v1/health/` automaticamente

### 6. Erros Estruturados (Padrão Vinculus)

**Motivo:** Consumidores da API (frontend, Assas, etc.) precisam de erros parseáveis.

```json
{"erro": "CODIGO", "mensagem": "...", "detalhes": [...]}
```

- Códigos de erro em português (consistente com nomes de tabelas e campos)
- Campo `detalhes` sempre array (consumidor não precisa tratar `null` vs `[]`)

### 7. Logs Rotativos

**Motivo:** Debug em produção sem explodir o disco.

- `app.log` (INFO+): 10MB × 5 arquivos
- `error.log` (ERROR+): 10MB × 5 arquivos
- `access.log`: Requisições (para métricas)
- Console colorido em desenvolvimento, JSON estruturado em produção (padrão Vinculus)

### 8. Rate Limiting

**Motivo:** Proteção contra abuso sem autenticação.

- Health check não tem rate limit (`AllowAny`)
- Endpoints autenticados: 1000 req/min
- Endpoints não autenticados: 60 req/min

---

## Proposta de Integração — Assas

### Visão Geral

O **Asaas** é uma plataforma de pagamentos brasileira com API REST para:

- **Split de pagamento:** Distribuir valores entre múltiplos recebedores
- **Cobrança:** Boleto, cartão de crédito, PIX
- **Assinatura:** Cobrança recorrente
- **Notificações:** Webhooks para eventos de pagamento

### Arquitetura Proposta

```
┌──────────┐    ┌──────────────────┐    ┌─────────┐
│ Frontend │───>│  Lacrei Saúde    │───>│  Asaas  │
│ (Next.js)│    │  (Django API)    │    │  (API)  │
└──────────┘    └────────┬─────────┘    └────┬────┘
                         │                    │
                         │  Webhook           │
                         │<───────────────────┘
                         │  (pagamento.confirmado)
                         │
                  ┌──────┴──────┐
                  │  PostgreSQL │
                  │  (faturas)  │
                  └─────────────┘
```

### Fluxo de Split de Pagamento

```
1. Paciente agenda consulta (POST /api/v1/appointments/)
2. Sistema cria cobrança no Asaas com split:
   - 80% → Profissional da saúde
   - 20% → Lacrei Saúde (taxa de plataforma)
3. Paciente paga via PIX/Cartão/Boleto
4. Asaas envia webhook "PAYMENT_RECEIVED" para /api/v1/webhooks/asaas/
5. Sistema atualiza status da consulta para "pago"
6. Split é processado automaticamente pelo Asaas
```

### Modelo de Dados (Proposto)

```python
class Fatura(models.Model):
    appointment = models.OneToOneField("appointments.Appointment", on_delete=models.CASCADE)
    asaas_payment_id = models.CharField(max_length=255, unique=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_profissional = models.DecimalField(max_digits=10, decimal_places=2)
    valor_plataforma = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=30,
        choices=[
            ("PENDING", "Pendente"),
            ("RECEIVED", "Recebido"),
            ("CONFIRMED", "Confirmado"),
            ("REFUNDED", "Reembolsado"),
            ("OVERDUE", "Vencido"),
        ],
        default="PENDING",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
```

### Webhook Handler (Proposto)

```python
@api_view(["POST"])
@permission_classes([AllowAny])  # Validado via token Asaas
def asaas_webhook(request):
    payload = request.data
    event = payload.get("event")
    payment = payload.get("payment", {})

    # Validar token Asaas (access_token configurado no painel Asaas)
    if request.headers.get("asaas-access-token") != settings.ASAAS_WEBHOOK_TOKEN:
        return Response({"erro": "NAO_AUTORIZADO"}, status=401)

    if event == "PAYMENT_RECEIVED":
        fatura = Fatura.objects.get(asaas_payment_id=payment["id"])
        fatura.status = "CONFIRMED"
        fatura.save()

    return Response({"status": "ok"})
```

### Configuração de Ambiente

```bash
# .env
ASAAS_API_KEY=$aact_...
ASAAS_WEBHOOK_TOKEN=wh_...
ASAAS_BASE_URL=https://sandbox.asaas.com/api/v3  # Sandbox
# ASAAS_BASE_URL=https://api.asaas.com/v3        # Produção
```

### Mock para Desenvolvimento

```python
# apps/payments/asaas_mock.py
class AsaasMockClient:
    """Simula a API do Asaas para desenvolvimento e testes."""

    def criar_cobranca(self, valor, split_rules):
        return {
            "id": f"pay_mock_{uuid.uuid4().hex[:8]}",
            "status": "PENDING",
            "valor": valor,
            "split": split_rules,
            "pix_qr_code": "https://pix.mock/qrcode",
            "boleto_url": "https://boleto.mock/123",
        }

    def consultar_cobranca(self, payment_id):
        return {"id": payment_id, "status": "RECEIVED"}

    def estornar(self, payment_id):
        return {"id": payment_id, "status": "REFUNDED"}
```

### Plano de Implementação

| Fase | Escopo | Prazo |
|---|---|---|
| **Fase 1** | Mock do Asaas + modelo Fatura + endpoints de cobrança | 1 sprint |
| **Fase 2** | Integração real com sandbox Asaas + webhook handler | 1 sprint |
| **Fase 3** | Split de pagamento + dashboard de faturas | 1 sprint |
| **Fase 4** | Produção: chaves reais, monitoramento, logs de auditoria | 1 sprint |

---

## Melhorias Futuras

1. **Autenticação JWT** — Evoluir de API Key para JWT multi-token (padrão Vinculus: access + refresh + selection)
2. **Tenant Isolation via RLS** — PostgreSQL Row-Level Security para multi-tenant (padrão Vinculus)
3. **RBAC** — Role-based access control (admin, profissional, atendente) — padrão Vinculus
4. **Cache com Redis** — Reduzir carga no banco para listagens frequentes
5. **Observabilidade** — Prometheus + Grafana para métricas, Sentry para erros
6. **Testes de integração** — Testes end-to-end com banco PostgreSQL isolado (padrão Vinculus)
7. **Ambiente Preview por PR** — Deploy automático de PRs para validação antes do merge

---

## Comandos Rápidos

```bash
# Desenvolvimento
poetry run python manage.py runserver
poetry run python manage.py create_api_key --nome "minha-key"
poetry run python manage.py seed

# Testes
poetry run pytest                          # Rodar todos
poetry run pytest --cov=. --cov-report=term # Com cobertura

# Lint
poetry run ruff check .                    # Verificar
poetry run ruff check --fix .              # Auto-corrigir
poetry run ruff format .                   # Formatar

# Docker (desenvolvimento)
docker compose -f docker-compose.dev.yml up --build

# Docker (produção)
docker compose up --build -d
docker compose logs -f web
```
