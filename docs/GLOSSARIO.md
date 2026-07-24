# Glossário Técnico — Lacrei Saúde Backend

## Conceitos Fundamentais

### CRUD

**C**reate, **R**ead, **U**pdate, **D**elete — as 4 operações básicas que qualquer sistema de dados precisa ter.

| Operação | HTTP | Exemplo no nosso sistema |
|---|---|---|
| **Create** (Criar) | `POST` | `POST /api/v1/professionals/` — cadastra um novo profissional |
| **Read** (Ler/Listar) | `GET` | `GET /api/v1/professionals/` — lista todos os profissionais |
| **Update** (Atualizar) | `PUT` / `PATCH` | `PATCH /api/v1/professionals/3/` — edita o nome do profissional 3 |
| **Delete** (Excluir) | `DELETE` | `DELETE /api/v1/professionals/3/` — remove o profissional 3 |

Nosso sistema implementa CRUD completo para:
- **Profissionais da saúde** — cadastrar, listar, editar, excluir
- **Consultas médicas** — agendar, listar, reagendar, cancelar

### API RESTful

**API** = Application Programming Interface (Interface de Programação). É um "cardápio" de funcionalidades que outros sistemas podem consumir.

**RESTful** = um estilo de arquitetura que usa:
- URLs que representam recursos (`/professionals/`, `/appointments/`)
- Métodos HTTP com significado (`GET` = buscar, `POST` = criar, `DELETE` = remover)
- Respostas em JSON (formato leve e universal)
- Sem estado (cada requisição é independente)

### JSON

**J**ava**S**cript **O**bject **N**otation — formato de dados leve, legível por humanos e máquinas.

```json
{
  "id": 1,
  "nome_social": "Dr. João Silva",
  "profissao": "Psicólogo"
}
```

Todas as respostas da nossa API são em JSON. É o formato padrão da web moderna.

---

## Tecnologias do Projeto

### Django

Framework web em Python. É como uma "caixa de ferramentas" que já vem com:
- **ORM** — traduz código Python em SQL automaticamente (sem escrever queries)
- **Admin** — painel administrativo gerado automaticamente
- **Migrations** — controle de versão do banco de dados
- **Middleware** — camadas de segurança que processam toda requisição

### Django REST Framework (DRF)

Complemento do Django especializado em APIs REST. Fornece:
- **ViewSets** — classes que geram CRUD automático
- **Serializers** — convertem dados Python ↔ JSON
- **Autenticação** — sistema plugável de login/tokens

### Model

Representa uma tabela no banco de dados. Exemplo:

```python
class Professional(models.Model):    # → Tabela "professionals_professional"
    nome_social = models.CharField()  # → Coluna "nome_social" (texto)
    profissao = models.CharField()    # → Coluna "profissao" (texto)
    endereco = models.TextField()     # → Coluna "endereco" (texto longo)
    contato = models.CharField()      # → Coluna "contato" (texto)
```

Cada `Professional` no código = uma linha na tabela do banco.

### Migration

Arquivo que registra mudanças na estrutura do banco de dados. Exemplo: quando criamos o modelo `Professional`, o Django gerou `0001_initial.py` — um arquivo que contém as instruções SQL para criar a tabela. Rodar `python manage.py migrate` executa essas instruções no banco.

### Serializer

Converte objetos Python em JSON (e vice-versa). É a "tradução" entre o banco de dados e a resposta da API.

```python
class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ["id", "nome_social", "profissao", "endereco", "contato"]
```

### ViewSet

Classe que implementa todas as operações CRUD automaticamente. Em vez de escrever 5 funções separadas, o ViewSet gera todas:

```python
class ProfessionalViewSet(viewsets.ModelViewSet):
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
```

6 linhas = CRUD completo (listar, criar, detalhar, atualizar, atualizar parcial, deletar).

### Endpoint

Uma URL específica que representa uma funcionalidade da API.

| Endpoint | O que faz |
|---|---|
| `GET /api/v1/professionals/` | Listar profissionais |
| `POST /api/v1/professionals/` | Criar profissional |
| `GET /api/v1/professionals/3/` | Detalhar profissional ID 3 |
| `GET /api/v1/appointments/?professional=1` | Consultas do profissional 1 |
| `GET /api/v1/health/` | Verificar se o sistema está saudável |

---

## Banco de Dados

### Chave Estrangeira (Foreign Key / FK)

Ligação entre duas tabelas. Exemplo: uma consulta (`Appointment`) pertence a um profissional (`Professional`).

```python
class Appointment(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
```

Se o profissional for deletado (`on_delete=CASCADE`), todas as consultas dele também são removidas automaticamente.

### UniqueConstraint

Regra que impede dados duplicados. No nosso sistema, um profissional não pode ter duas consultas no mesmo horário:

```python
constraints = [
    UniqueConstraint(fields=["professional", "data"], name="uk_appointment_professional_data")
]
```

---

## Segurança

### API Key

Uma "senha" que identifica quem está acessando a API. Vai no header da requisição:

```bash
curl -H "X-API-Key: af5e5f09da222409..." http://localhost:8000/api/v1/professionals/
```

Usamos `secrets.token_hex(32)` — gera 64 caracteres aleatórios, matematicamente impossível de adivinhar.

### CORS (Cross-Origin Resource Sharing)

Mecanismo de segurança do navegador que controla quais sites podem acessar a API. Nosso sistema só permite requisições de origens configuradas (ex: `http://localhost:3000`). Isso impede que um site malicioso acesse a API sem permissão.

### SQL Injection

Ataque onde o invasor tenta injetar comandos SQL maliciosos nos campos de entrada. Exemplo: alguém digita `' OR '1'='1` no campo de busca para tentar listar todos os dados.

**Por que estamos protegidos:** usamos 100% Django ORM — nunca escrevemos SQL manualmente. O ORM automaticamente escapa (limpa) todos os parâmetros antes de enviar ao banco.

### XSS (Cross-Site Scripting)

Ataque onde o invasor injeta código HTML/JavaScript nos campos. Exemplo: alguém cadastra um profissional com nome `<script>roubarDados()</script>`.

**Por que estamos protegidos:** a função `strip_tags()` remove todas as tags HTML antes de salvar no banco.

### HSTS (HTTP Strict Transport Security)

Força o navegador a usar sempre HTTPS (conexão criptografada), nunca HTTP. Configuramos com `SECURE_HSTS_SECONDS = 31536000` (1 ano).

---

## Docker

### Container

Ambiente isolado que contém tudo que a aplicação precisa: código, dependências, configurações. É como uma "máquina virtual leve".

### Imagem

O "molde" do container — define o que vai dentro. Nosso Dockerfile constrói a imagem.

### Dockerfile

Receita que o Docker segue para criar a imagem. O nosso usa **multi-stage build**:

```
Estágio 1 (builder):   instala compiladores + dependências Poetry
Estágio 2 (production): copia só o necessário + roda como usuário não-root
```

### Docker Compose

Orquestra múltiplos containers juntos. Define:
- **db**: PostgreSQL 16 (banco de dados)
- **web**: nossa aplicação Django + Gunicorn (servidor)

Os dois containers se comunicam por uma rede interna.

---

## CI/CD (Integração e Entrega Contínua)

### CI (Continuous Integration)

A cada `git push`, o GitHub Actions automaticamente:
1. Roda o **linter** (verifica erros de código)
2. Roda os **34 testes** (confirma que nada quebrou)
3. Faz o **build** da imagem Docker (confirma que compila)

### CD (Continuous Deployment)

Se CI passar, automaticamente:
4. Faz o **deploy** na AWS (sobe a nova versão pra produção)

### Pipeline

O "cano" por onde o código passa: `push → lint → test → build → deploy`. Cada etapa é um **job** no GitHub Actions.

### Lint

Ferramenta que analisa o código sem executá-lo. Verifica:
- Erros de sintaxe
- Imports não usados
- Estilo inconsistente
- Más práticas comuns

Usamos **Ruff** (10x mais rápido que as alternativas).

---

## Infraestrutura AWS

### Terraform

Ferramenta que cria toda a infraestrutura na nuvem a partir de código. Em vez de clicar no console AWS, você escreve arquivos `.tf` e o Terraform cria tudo automaticamente.

### ECS (Elastic Container Service)

Serviço da AWS que roda containers Docker. Nosso sistema usa **Fargate** (AWS gerencia os servidores, não precisamos nos preocupar com máquinas).

### ECR (Elastic Container Registry)

"Depósito" de imagens Docker na AWS. O CI/CD empurra a imagem pro ECR e o ECS puxa de lá.

### RDS (Relational Database Service)

PostgreSQL gerenciado pela AWS. Backup automático, Multi-AZ (réplica em outra zona), criptografia.

### ALB (Application Load Balancer)

Distribui as requisições entre múltiplas instâncias da aplicação. Se uma instância cair, o ALB para de enviar tráfego pra ela automaticamente.

---

## Outros Termos

### Middleware

Código que roda **entre** a requisição chegar e a view processar. Todo request passa por todos os middlewares. Exemplos no nosso sistema:
- `SecurityMiddleware` — headers de segurança (HSTS, XSS filter)
- `CorsMiddleware` — controle de origens permitidas
- `AccessLoggingMiddleware` — registra toda requisição no log

### Query Param

Parâmetro passado na URL depois do `?`. Exemplo: `?professional=1`. Usamos para filtrar consultas por profissional.

### Paginação

Dividir resultados em páginas. Nossa API retorna no máximo 20 itens por página. O frontend pode navegar com `?page=2`.

### Rate Limiting

Limite de requisições por minuto. Configuramos:
- **60 req/min** para usuários não autenticados
- **1000 req/min** para usuários autenticados

Protege o sistema contra abuso.

### Health Check

Endpoint que verifica se o sistema está saudável. Retorna se o banco de dados está respondendo. Usado pelo Docker e pelo load balancer da AWS para saber se o container está vivo.
