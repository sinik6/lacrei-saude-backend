# Roteiro de Entrevista — Lacrei Saúde Backend

## 1. Apresentação do Projeto (2 min)

> "Desenvolvi uma API RESTful de Gerenciamento de Consultas Médicas para a Lacrei Saúde, voltada à comunidade LGBTQIAPN+. O sistema usa Django 6 + Django REST Framework, PostgreSQL, Docker, CI/CD com GitHub Actions e deploy na AWS via Terraform."

**Números pra usar:**
- 34 testes automatizados (100% passando no CI)
- 16 commits organizados por responsabilidade
- Cobertura de 84% no CI com PostgreSQL real
- 3 ambientes: local (SQLite), CI (PostgreSQL), produção (AWS RDS)

---

## 2. Arquitetura (3 min)

### Estrutura do Projeto
```
lacrei-backend/
├── apps/
│   ├── professionals/    # CRUD de profissionais da saúde
│   ├── appointments/     # CRUD de consultas com vínculo ao profissional
│   ├── users/            # Autenticação via API Key
│   └── health/           # Health check com verificação de banco
├── config/               # Settings (produção, teste, CI)
├── infra/terraform/      # Infraestrutura como código (AWS)
├── .github/workflows/    # CI/CD (lint → test → build → deploy)
└── docker/               # Scripts de inicialização do PostgreSQL
```

### Modelo de Dados
```
Professional ──1:N──> Appointment
├── nome_social          ├── professional (FK, CASCADE)
├── profissao            ├── data (DateTimeField)
├── endereco             └── UniqueConstraint(professional, data)
└── contato
```

### Pontos pra destacar
- **Separação por domínio**: cada app Django representa um contexto de negócio real
- **Settings por ambiente**: `settings.py` (prod), `settings_test.py` (SQLite local), `settings_ci.py` (PostgreSQL CI)
- **ViewSets**: menos código, mais consistência — cada ViewSet são ~6 linhas de configuração

---

## 3. Decisões Técnicas (3 min)

### Por que Django + DRF e não FastAPI?

> "O desafio exigia Django. Além disso, o ecossistema Django oferece Admin automático (gestão de API Keys sem código extra), ORM maduro com proteção built-in contra SQL Injection, migrations determinísticas e middleware stack completo de segurança."

### Por que API Key e não JWT?

> "API Key é mais simples para comunicação server-to-server, ideal pra integrações futuras com Asaas, frontend e outros serviços. A estrutura de autenticação é plugável — evoluir pra JWT é questão de trocar a classe de autenticação."

### Por que SQLite nos testes locais e PostgreSQL no CI?

> "SQLite em memória torna os testes instantâneos (< 0.5s) sem dependência externa. No CI, o GitHub Actions sobe um container PostgreSQL dedicado — garantindo que os testes validem o banco real que vai pra produção."

### Por que Terraform?

> "A infraestrutura AWS inteira é versionada como código. Qualquer pessoa do time pode recriar o ambiente staging ou produção com 3 comandos. Isso elimina configuração manual e garante ambientes idênticos."

---

## 4. Segurança (2 min)

### O que foi implementado

| Camada | Técnica |
|---|---|
| **Input** | `strip_tags()` em todos os campos de texto (anti-XSS) |
| **Banco** | 100% Django ORM — zero SQL raw (anti-SQL Injection) |
| **Transporte** | HSTS, SSL redirect, CORS configurado |
| **Autenticação** | API Key via header `X-API-Key`, chave 64 caracteres (secrets.token_hex) |
| **Negócio** | UniqueConstraint evita double-booking, validação de data futura |
| **Rate Limit** | 60 req/min anônimo, 1000 req/min autenticado |
| **Logs** | Access logging middleware em toda requisição, erros estruturados com códigos |

### Formato de erro (padrão Vinculus)

```json
{
  "erro": "NAO_ENCONTRADO",
  "mensagem": "Recurso não encontrado.",
  "detalhes": []
}
```

> "Todo erro retorna um JSON estruturado com código, mensagem em português e array de detalhes. Isso permite que o frontend ou serviços externos façam tratamento de erro programático sem precisar parsear mensagens de texto."

---

## 5. CI/CD (2 min)

### Pipeline
```
Push → Lint (Ruff) → Test (PostgreSQL + 34 testes) → Build (Docker multi-stage) → Deploy (ECS)
```

### O que acontece em cada push
1. **Lint**: Ruff verifica estilo e erros de código
2. **Test**: Sobe PostgreSQL → roda migrations → 34 testes → coverage report
3. **Build**: Docker multi-stage (builder + production) → imagem enxuta com usuário não-root
4. **Deploy Staging** (branch `develop`) ou **Deploy Production** (branch `main`)

### Rollback
> "Temos 3 estratégias de rollback: workflow_dispatch no GitHub Actions (reverte task definition do ECS pra revisão anterior), git revert manual, e Blue/Green deploy no ECS."

---

## 6. Desafios e Aprendizados (1 min)

### O bug do SSL Redirect no CI

> "O maior desafio foi um bug sutil: os 34 testes quebravam com HTTP 301 no CI mas passavam localmente. Depois de 4 commits de investigação, descobri que o `--ds=config.settings` no comando do pytest usava as configurações de produção, onde `SECURE_SSL_REDIRECT=True` redirecionava todas as requisições HTTP para HTTPS. A solução foi criar `settings_ci.py` com `SECURE_SSL_REDIRECT=False` e corrigir o flag `--ds=config.settings_ci`. Esse bug me ensinou a sempre isolar configurações de ambiente e verificar flags de override em pipelines CI/CD."

---

## 7. Perguntas Prováveis e Respostas

### "Como você lidaria com 10.000 requisições simultâneas?"

> "O ECS Fargate já está configurado com auto scaling baseado em CPU (70% target). Em produção, começa com 2 tasks e escala até 4 automaticamente. Pra ir além, adicionaria Redis como cache de leitura e consideraria read replicas do RDS. O Django ORM com `select_related` já evita N+1 queries."

### "Como funciona a busca de consultas por profissional?"

> "Endpoint `GET /api/v1/appointments/?professional=3`. O `DjangoFilterBackend` traduz o query param `professional` em um filtro SQL `WHERE professional_id = 3`. O ORM parametriza a query — impossível SQL Injection."

### "O que faria diferente na próxima versão?"

> "Adicionaria JWT multi-token com refresh token, cache com Redis, e observabilidade com Prometheus/Grafana. Também implementaria o split de pagamento com Asaas — já tenho o modelo `Fatura` e o mock documentados no README."

### "Como você garante que o deploy não quebra em produção?"

> "Três camadas: 1) CI roda 34 testes contra PostgreSQL real antes de permitir o deploy, 2) O deploy vai pra staging primeiro (branch develop), 3) Em produção, o ECS faz health check no endpoint `/api/v1/health/` — se falhar, o deploy é revertido automaticamente."

---

## 8. Demo Rápida (se pedirem)

```bash
# Clone e sobe em 2 comandos
git clone https://github.com/sinik6/lacrei-saude-backend
cd lacrei-saude-backend
docker compose -f docker-compose.dev.yml up --build

# Health check
curl http://localhost:8000/api/v1/health/
# → {"status":"ok","database":"connected"}

# Criar API Key
docker compose exec web python manage.py create_api_key --nome demo

# CRUD completo
curl -H "X-API-Key: <key>" http://localhost:8000/api/v1/professionals/
curl -H "X-API-Key: <key>" http://localhost:8000/api/v1/appointments/?professional=1

# Swagger
open http://localhost:8000/api/v1/docs/swagger/
```
