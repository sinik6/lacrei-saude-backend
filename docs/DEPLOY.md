# Guia de Deploy

## Pré-requisitos

- AWS CLI configurada (`aws configure`)
- Docker
- GitHub CLI (`gh auth login`)

## Secrets obrigatórios no GitHub

Settings → Secrets and variables → Actions:

| Secret | Valor |
|---|---|
| `AWS_ACCESS_KEY_ID` | Access key IAM |
| `AWS_SECRET_ACCESS_KEY` | Secret key IAM |
| `AWS_ECR_REGISTRY` | URI do ECR (ex: `12345.dkr.ecr.us-east-1.amazonaws.com`) |

## Variáveis de ambiente

| Variable | Valor |
|---|---|
| `AWS_REGION` | `us-east-1` |

## Fluxo

```
git push develop  →  lint → test → build Docker → deploy STAGING
git push main     →  lint → test → build Docker → deploy PRODUCTION
```

## Rollback

GitHub → Actions → Rollback → Run workflow → selecionar `staging` ou `production`. O script detecta a revisão anterior da task definition do ECS e reverte automaticamente.

## Verificação

```bash
# Health check
curl http://<alb-dns>/api/v1/health/

# Swagger
open http://<alb-dns>/api/v1/docs/swagger/
```
