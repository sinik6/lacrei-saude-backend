# =============================================================================
# Lacrei Saúde — Guia de Deploy AWS (Terraform + CI/CD)
# =============================================================================

## Pré-requisitos

Antes de começar, você precisa ter:

| Ferramenta | Versão | Instalação |
|---|---|---|
| AWS CLI | 2.x | `aws configure` |
| Terraform | 1.5+ | `brew install terraform` |
| GitHub CLI | 2.x | `gh auth login` |
| Docker | 29+ | Já instalado |

E uma **conta AWS** com permissões para criar: VPC, ECS, ECR, RDS, ALB, Secrets Manager, IAM, CloudWatch.

---

## Arquitetura AWS

```
                         Internet
                            │
                    ┌───────▼────────┐
                    │  ALB (HTTP/80) │
                    └───────┬────────┘
                            │
              ┌─────────────▼─────────────┐
              │      ECS Fargate          │
              │  ┌─────────────────────┐  │
              │  │ lacrei-saude-api    │  │
              │  │ (2 instâncias)      │  │
              │  └────────┬────────────┘  │
              └───────────┼───────────────┘
                          │
              ┌───────────▼───────────────┐
              │     RDS PostgreSQL 16     │
              │   (Multi-AZ em production)│
              └───────────────────────────┘
              ┌───────────────────────────┐
              │    Secrets Manager        │
              │  (DB pass + Django key)   │
              └───────────────────────────┘
```

---

## Passo 1: Criar bucket S3 para estado do Terraform (uma vez)

```bash
aws s3 mb s3://lacrei-terraform-state --region us-east-1
aws s3api put-bucket-versioning \
  --bucket lacrei-terraform-state \
  --versioning-configuration Status=Enabled
aws dynamodb create-table \
  --table-name lacrei-terraform-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

---

## Passo 2: Deploy Staging

```bash
cd infra/terraform

# Inicializar Terraform
terraform init

# Planejar (visualizar o que será criado)
terraform plan \
  -var="environment=staging" \
  -out=staging.tfplan

# Aplicar
terraform apply staging.tfplan

# Anotar outputs:
#   ecr_repository_url = "<conta>.dkr.ecr.us-east-1.amazonaws.com/lacrei-saude-api-staging"
#   ecs_cluster_name   = "lacrei-saude-api-staging"
#   ecs_service_name   = "lacrei-saude-api-staging"
#   alb_dns_name       = "lacrei-saude-api-staging-xxxx.us-east-1.elb.amazonaws.com"
```

---

## Passo 3: Deploy Production

```bash
terraform plan \
  -var="environment=production" \
  -out=production.tfplan

terraform apply production.tfplan
```

---

## Passo 4: Configurar GitHub Secrets

Adicione esses secrets no repositório GitHub (`Settings → Secrets and variables → Actions`):

### Secrets de Ambiente — Staging

| Secret | Onde obter |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM → Users → Create access key |
| `AWS_SECRET_ACCESS_KEY` | IAM → Users → Create access key |
| `AWS_ECR_REGISTRY` | Output do Terraform: `ecr_repository_url` (sem o `:latest`) |

### Secrets de Ambiente — Production

Mesmos secrets acima, mas com credenciais separadas.

### Variáveis de Ambiente

| Variable | Valor |
|---|---|
| `AWS_REGION` | `us-east-1` |

---

## Passo 5: Primeiro Deploy Manual

O CI/CD faz deploy automático, mas o primeiro push precisa popular o ECR:

```bash
# Login no ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  $(terraform output -raw ecr_repository_url | cut -d'/' -f1)

# Build e push
docker build -t lacrei-saude-api .
docker tag lacrei-saude-api:latest $(terraform output -raw ecr_repository_url):latest
docker push $(terraform output -raw ecr_repository_url):latest

# Forçar primeiro deploy
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw ecs_service_name) \
  --force-new-deployment

# Aguardar
aws ecs wait services-stable \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw ecs_service_name)
```

---

## Passo 6: Verificar

```bash
# Pegar URL do ALB
ALB=$(terraform output -raw alb_dns_name)

# Health check
curl "http://$ALB/api/v1/health/"

# Criar API Key
# (execute dentro do container via ECS Exec ou use o endpoint admin)
```

---

## Fluxo de Deploy Automático (CI/CD)

```
git push origin develop        git push origin main
        │                              │
        ▼                              ▼
   ┌─────────┐                   ┌─────────┐
   │  Lint   │                   │  Lint   │
   └────┬────┘                   └────┬────┘
        ▼                              ▼
   ┌─────────┐                   ┌─────────┐
   │  Test   │                   │  Test   │
   │(Postgres)│                   │(Postgres)│
   └────┬────┘                   └────┬────┘
        ▼                              ▼
   ┌─────────┐                   ┌─────────┐
   │  Build  │                   │  Build  │
   │ Docker  │                   │ Docker  │
   └────┬────┘                   └────┬────┘
        ▼                              ▼
   ┌───────────┐                ┌───────────────┐
   │ Deploy    │                │ Deploy        │
   │ STAGING   │                │ PRODUCTION    │
   │ ECS + ECR │                │ ECS + ECR     │
   └───────────┘                └───────────────┘
```

---

## Rollback

### Via GitHub Actions (recomendado)

```
GitHub → Actions → Rollback → Run workflow
        Selecione: staging ou production
```

O workflow automático detecta a revisão anterior da task definition e reverte.

### Via CLI

```bash
# Pegar task definition anterior
TASK_DEF=$(aws ecs describe-services \
  --cluster lacrei-saude-api-staging \
  --services lacrei-saude-api-staging \
  --query 'services[0].taskDefinition' --output text | sed 's/:[0-9]*$//')

PREV_REV=$(( $(aws ecs describe-task-definition \
  --task-definition "$TASK_DEF" \
  --query 'taskDefinition.revision' --output text) - 1 ))

# Rollback
aws ecs update-service \
  --cluster lacrei-saude-api-staging \
  --service lacrei-saude-api-staging \
  --task-definition "${TASK_DEF}:${PREV_REV}" \
  --force-new-deployment
```

---

## Comandos Úteis

```bash
# Ver logs do ECS
aws logs tail /ecs/lacrei-saude-api-staging --follow

# Ver status do serviço
aws ecs describe-services \
  --cluster lacrei-saude-api-staging \
  --services lacrei-saude-api-staging \
  --query 'services[0].[status,desiredCount,runningCount,deployments]'

# Conectar ao container
aws ecs execute-command \
  --cluster lacrei-saude-api-staging \
  --task <task-id> \
  --container lacrei-saude-api \
  --command "/bin/sh" \
  --interactive

# Destruir ambiente staging
terraform destroy -var="environment=staging"
```

---

## Custos Estimados (AWS)

| Recurso | Staging/mês | Production/mês |
|---|---|---|
| ECS Fargate (2 tasks) | ~$25 | ~$50 |
| RDS db.t3.micro | ~$15 | ~$30 (Multi-AZ) |
| ALB | ~$20 | ~$20 |
| Secrets Manager | ~$1 | ~$1 |
| CloudWatch Logs | ~$5 | ~$10 |
| **Total** | **~$66** | **~$111** |
