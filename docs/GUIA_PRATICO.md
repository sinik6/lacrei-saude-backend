# Guia Prático: Rodando o Sistema do Zero

Cada comando explicado — o que faz, por que usamos essa tecnologia, e o que esperar.

---

## Pré-requisitos

Você precisa destas ferramentas instaladas:

| Ferramenta | Como instalar | Pra que serve |
|---|---|---|
| **Docker** | `sudo apt install docker.io` | Empacota a aplicação e o banco em containers isolados |
| **Docker Compose** | Já vem com Docker 29+ | Orquestra múltiplos containers (app + banco) |
| **Git** | `sudo apt install git` | Baixa o código do repositório |

## Pré-requisitos (opcional, só se quiser editar o código)

| Ferramenta | Como instalar | Pra que serve |
|---|---|---|
| **Python 3.12+** | `sudo apt install python3` | Linguagem do projeto |
| **Poetry** | `pip install poetry` | Gerenciador de dependências (tipo npm do Python) |

---

## Passo 1: Baixar o código

```bash
git clone https://github.com/sinik6/lacrei-saude-backend.git

cd lacrei-saude-backend
```

**Explicação:** `git clone` baixa o repositório inteiro — código, Dockerfiles, CI/CD, testes, tudo. O projeto já tem 16 commits organizados por funcionalidade.

---

## Passo 2: Subir o sistema com Docker

```bash
docker compose -f docker-compose.dev.yml up --build
```

**O que vai acontecer:**
- O Docker vai baixar a imagem do **PostgreSQL 16** (banco de dados)
- O Docker vai **compilar** nossa aplicação Python dentro de um container
- O banco sobe primeiro → a aplicação espera o banco ficar saudável → depois sobe também
- O terminal vai mostrar os logs da aplicação subindo

**Explicação de cada tecnologia:**

| Peça | Tecnologia | Por que usamos |
|---|---|---|
| **Banco de dados** | PostgreSQL 16 | Exigido pelo desafio. Banco relacional robusto, melhor que MySQL para dados complexos |
| **Container da aplicação** | Python 3.13 + Gunicorn | Python é a linguagem do Django. Gunicorn é o servidor WSGI que recebe requisições HTTP e distribui entre workers |
| **Empacotamento** | Docker multi-stage | Compila dependências em um container temporário (builder) e copia só o necessário pro container final — a imagem fica mais leve e segura |
| **Orquestração** | Docker Compose | Define como os containers se comunicam. O banco expõe porta 5432, a aplicação expõe porta 8000 |

**O Dockerfile (como a aplicação é empacotada):**
```
Estágio 1 (builder):   Python 3.13 + compiladores → instala dependências via Poetry
Estágio 2 (production): Python 3.13 + runtime only → copia dependências → roda como usuário não-root
```

Se quiser parar o sistema: `docker compose -f docker-compose.dev.yml down`

---

## Passo 3: Verificar que está funcionando

**Health check (sem autenticação):**
```bash
curl http://localhost:8000/api/v1/health/
```

Resposta esperada:
```json
{
    "status": "ok",
    "versao": "1.0.0",
    "servico": "lacrei-saude-api",
    "database": "connected"
}
```

**Explicação:** O health check verifica se o banco de dados está respondendo. Se o banco estiver fora, retorna `"status": "degraded"` com HTTP 503. Isso é usado pelo Docker e pelo load balancer da AWS para saber se o container está saudável.

---

## Passo 4: Criar uma chave de autenticação (API Key)

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py create_api_key --nome "minha-chave"
```

Saída esperada:
```
API Key criada com sucesso!
  Nome: minha-chave
  Key:  af5e5f09da222409503c0e0c8b5740c922a4b501f27464563126d1defd81af6a
  Guarde esta chave em local seguro.
  Use no header: X-API-Key: af5e5f09da...
```

**Explicação:** Toda requisição à API (exceto health check) precisa do header `X-API-Key` com essa chave. A chave é gerada com `secrets.token_hex(32)` — 64 caracteres hexadecimais aleatórios, impossível de adivinhar. Você pode criar quantas chaves quiser (uma por serviço consumidor) e desativar chaves sem deletar.

**Guarde essa chave** — vamos chamar ela de `SUA_KEY` nos próximos passos.

---

## Passo 5: Popular o banco com dados de exemplo

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py seed
```

Saída esperada:
```
Populando banco de dados...
  5 profissionais criados
  40 consultas criadas
Seed concluído com sucesso!
```

**Explicação:** O comando `seed` cria 5 profissionais (psicólogo, clínico geral, endocrinologista, ginecologista, psiquiatra) e 40 consultas distribuídas entre eles. É idempotente — se rodar de novo, não duplica os dados.

---

## Passo 6: Testar a API

Substitua `SUA_KEY` pela chave do Passo 4.

### Listar profissionais
```bash
curl -s -H "X-API-Key: SUA_KEY" http://localhost:8000/api/v1/professionais/ | python3 -m json.tool
```

### Criar um profissional
```bash
curl -s -H "X-API-Key: SUA_KEY" \
  -H "Content-Type: application/json" \
  -d '{"nome_social":"Dr. Novo Profissional","profissao":"Nutricionista","endereco":"Av. Brasil, 500","contato":"11988887777"}' \
  http://localhost:8000/api/v1/professionais/ | python3 -m json.tool
```

### Buscar consultas de um profissional específico
```bash
curl -s -H "X-API-Key: SUA_KEY" \
  "http://localhost:8000/api/v1/appointments/?professional=1" | python3 -m json.tool
```

**Explicação:** `?professional=1` filtra as consultas do profissional com ID 1. Isso é o requisito "busca de consultas pelo ID do profissional". O Django traduz automaticamente o query param em um filtro SQL seguro (sem SQL injection possível).

### Criar uma consulta
```bash
curl -s -H "X-API-Key: SUA_KEY" \
  -H "Content-Type: application/json" \
  -d '{"professional":1,"data":"2026-12-25T10:00:00Z"}' \
  http://localhost:8000/api/v1/appointments/ | python3 -m json.tool
```

### Acessar a documentação da API
```
http://localhost:8000/api/v1/docs/swagger/    ← Swagger (testar endpoints)
http://localhost:8000/api/v1/docs/redoc/       ← ReDoc (ler documentação)
```

**Explicação:** Swagger e ReDoc são gerados automaticamente pelo `drf-spectacular`. Qualquer mudança no código atualiza a documentação. No Swagger você pode testar os endpoints direto no navegador — só precisa configurar o header `X-API-Key`.

---

## Rodar os testes

### Testes locais (rápidos, usam SQLite em memória)
```bash
poetry run pytest -v
```

### Ver o que cada teste cobre
```bash
poetry run pytest --cov=. --cov-report=term
```

**Os 34 testes:**

| Arquivo | Quantos | O que testam |
|---|---|---|
| `apps/professionals/tests.py` | 13 | CRUD completo + sanitização HTML + filtros + autenticação |
| `apps/appointments/tests.py` | 16 | CRUD completo + data passada + duplicata + cascade delete |
| `apps/users/tests.py` | 5 | API Key: válida, inválida, inativa, ausente, múltiplos endpoints |

**Explicação:** Usamos `APITestCase` do Django REST Framework — cada teste faz uma requisição HTTP real (passando por middleware, autenticação, views, serializers, banco). Localmente usa SQLite em memória (instantâneo). No CI do GitHub Actions, usa PostgreSQL real.

---

## Ver o código passar no CI/CD

```bash
https://github.com/sinik6/lacrei-saude-backend/actions
```

**Resultado atual:**
```
✅ Lint (Ruff)     — código limpo, sem erros de estilo
✅ Tests           — 34/34 passando com PostgreSQL real no CI
✅ Build Docker    — imagem compilada e salva
❌ Deploy AWS      — precisa de credenciais da sua conta AWS
```

---

## Resumo das tecnologias e por que cada uma

| Tecnologia | O que é | Por que usamos |
|---|---|---|
| **Django 6** | Framework web Python | Exigido pelo desafio. ORM maduro, admin automático, segurança built-in |
| **DRF 3** | Django REST Framework | Transforma models Django em API REST automaticamente (ViewSets, Serializers) |
| **Poetry** | Gerenciador de dependências | Exigido pelo desafio. Lock file determinístico — todo dev instala exatamente as mesmas versões |
| **PostgreSQL 16** | Banco de dados relacional | Exigido pelo desafio. Melhor que SQLite/MySQL para produção: integridade referencial, performance, JSONB |
| **Docker** | Containerização | Exigido pelo desafio. Garante que o sistema roda igual em qualquer máquina |
| **Gunicorn** | Servidor WSGI | Servidor de produção — recebe requisições HTTP e distribui entre 3 workers Python |
| **WhiteNoise** | Servidor de arquivos estáticos | Serve arquivos CSS/JS do Django Admin sem precisar de CDN |
| **Ruff** | Linter + formatador | 10x mais rápido que Flake8. Verifica estilo, imports, e erros comuns |
| **pytest** | Test runner | Roda os 34 testes. Mais rápido e flexível que o unittest padrão do Django |
| **drf-spectacular** | Gerador OpenAPI | Gera documentação Swagger e ReDoc automaticamente do código |
| **django-cors-headers** | Controle CORS | Define quais origens (frontends) podem acessar a API — proteção contra CSRF cross-origin |
| **GitHub Actions** | CI/CD | Exigido pelo desafio. Roda lint, testes, build e deploy automaticamente a cada push |
| **Terraform** | Infraestrutura como código | Define toda a infra AWS (VPC, ECS, RDS, ALB) em arquivos versionados |

---

## Comandos rápidos (resumo)

```bash
# Subir o sistema
docker compose -f docker-compose.dev.yml up --build

# Parar o sistema
docker compose -f docker-compose.dev.yml down

# Health check
curl http://localhost:8000/api/v1/health/

# Criar API Key
docker compose exec web python manage.py create_api_key --nome "demo"

# Popular banco
docker compose exec web python manage.py seed

# Rodar testes
poetry run pytest -v

# Lint
poetry run ruff check .

# Swagger
open http://localhost:8000/api/v1/docs/swagger/
```
