[Skip to content](https://lacrei-saude.notion.site/Desafio-Back-end-32a28e22d088463ab4bee78ff394c5f9#main)

![](https://lacrei-saude.notion.site/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F25b45dd4-8819-4957-87f6-fe9bc5022a95%2F0aad5c05-6797-4061-94b5-ba0a0b0770ed%2FLS_Pattern_Background02.png?table=block&id=32a28e22-d088-463a-b4be-e78ff394c5f9&spaceId=25b45dd4-8819-4957-87f6-fe9bc5022a95&width=2000&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

![Page icon](https://lacrei-saude.notion.site/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fd4fcb498-7ae8-4271-ac8b-dc24e2aa8436%2FAvatar_Redes_Sociais.png?id=32a28e22-d088-463a-b4be-e78ff394c5f9&table=block&spaceId=25b45dd4-8819-4957-87f6-fe9bc5022a95&width=250&userId=&cache=v2&imgBuildSrc=requestProxiedImageUrl)

# Desafio Back end

## Desafio Técnico – Back-end na Lacrei Saúde

### ![🌈](<Base64-Image-Removed>) Olá, futura pessoa voluntária de Back-end da Lacrei Saúde!

Estamos felizes por contar com você em nosso time voluntário! ![💙](<Base64-Image-Removed>)​

Sua contribuição será essencial para construir soluções que ampliam o acesso à saúde inclusiva e de qualidade para a comunidade LGBTQIAPN+.

### ![💡](<Base64-Image-Removed>) Sobre a Atividade Voluntária

Duração: 3 meses

Carga horária: 20 horas semanais

Encontros obrigatórios:

![🕖](<Base64-Image-Removed>) Segundas e terças, das 19h às 20h30 (horário de Brasília)

### ![🎯](<Base64-Image-Removed>) Proposta do Desafio

![➡️ Callout icon](<Base64-Image-Removed>)

#### Desenvolva uma API funcional, segura e pronta para produção com propósito e impacto social.

Sua missão será desenvolver uma API RESTful de Gerenciamento de Consultas Médicas, com foco em:

Qualidade de código

Segurança dos dados

Boas práticas de desenvolvimento

Preparação para ambiente de produção

Este projeto será base para integrações com outros serviços da Lacrei Saúde, incluindo sistema de pagamentos, deploy e monitoramento.

### ![📝](<Base64-Image-Removed>) Sobre os dados e regras de negócio

O cadastro de profissionais deve conter: Nome social, Profissão, Endereço, Contato.

As consultas devem conter: Data, Profissional vinculado (chave estrangeira).

Todos os retornos da API devem estar em JSON.

### ![📋](<Base64-Image-Removed>)O que esperamos de você — Itens obrigatórios:

![✅](<Base64-Image-Removed>)CRUD completo:

![🔹](<Base64-Image-Removed>) Profissionais da saúde

![🔹](<Base64-Image-Removed>) Consultas (relacionadas a profissionais)

![🔹](<Base64-Image-Removed>) Busca de consultas pelo ID do profissional

![✅](<Base64-Image-Removed>)Segurança obrigatória:

![🔸](<Base64-Image-Removed>) Sanitização e validação dos dados

![🔸](<Base64-Image-Removed>) Proteção contra SQL Injection

![🔸](<Base64-Image-Removed>) Implementação de CORS configurado corretamente

![🔸](<Base64-Image-Removed>) Controle básico de autenticação (ex.: API Key, JWT ou Token simples)

![🔸](<Base64-Image-Removed>) Logs de acesso e erros

![✅](<Base64-Image-Removed>)Tecnologias obrigatórias:

Python com Django + Django REST Framework

Poetry (gerenciamento de dependências)

PostgreSQL

Docker (containerização)

GitHub Actions (para CI/CD)

![✅](<Base64-Image-Removed>)Testes automatizados:

![🔸](<Base64-Image-Removed>) Usando

APITestCase

do Django

![🔸](<Base64-Image-Removed>) Cobertura mínima:

CRUD de consultas

CRUD de profissionais

Testes de erro (ex.: requisição inválida, dados ausentes)

![✅](<Base64-Image-Removed>)Deploy funcional:

![🔸](<Base64-Image-Removed>) Ambientes separados: staging e produção (AWS)

![✅](<Base64-Image-Removed>)Pipeline CI/CD:

![🔸](<Base64-Image-Removed>) GitHub Actions com steps obrigatórios:

Lint

Testes

Build

Deploy

![✅](<Base64-Image-Removed>)Documentação obrigatória:

README com setup local e via Docker

Execução dos testes

Fluxo de deploy (CI/CD)

Justificativas técnicas das escolhas feitas

Proposta de rollback funcional:

Ex.: Deploy Blue/Green, Revert no GitHub Actions, Preview Deploy

![🟨](<Base64-Image-Removed>)(Bônus recomendado):

Proposta de integração com a Assas (mock, arquitetura ou real)

Geração de documentação da API (ex.: Swagger, Redoc, Postman)

### ![🌐](<Base64-Image-Removed>) Como irá fazer - Fluxo de atuação

Criar uma API Restful com:

Cadastro, edição, exclusão e listagem de profissionais da saúde

Cadastro e edição de consultas médicas com vínculo ao profissional

Busca por consultas utilizando o ID da pessoa profissional

Garantir segurança e validação de dados:

Sanitização de inputs

Prevenção contra SQL Injection e outras vulnerabilidades

Criar o projeto usando:

Python, com Django \+ Django REST Framework

Poetry para gerenciar dependências

PostgreSQL como banco de dados

Docker para configurar o ambiente

[![🐳](<Base64-Image-Removed>)\\
\\
Configurando e Utilizando o Ambiente Docker para sua Aplicação](https://lacrei-saude.notion.site/Configurando-e-Utilizando-o-Ambiente-Docker-para-sua-Aplica-o-1c9cdb7220b980e69b88f50fe91b1a95?pvs=25)

GitHub Actions para automatização de testes e deploy

Realizar o deploy da aplicação em:

Staging e produção, utilizando a AWS

(Opcional mas será esta integração em que irá atuar) Propor uma integração com a AssAs para split de pagamento (pode ser mock ou proposta de fluxo com base na documentação pública).

(Opcional, mas super valorizado!) Documentar um fluxo de rollback para o deploy da aplicação em caso de falha.

### ![📚](<Base64-Image-Removed>) Documentação e Testes

Criar um README completo, contendo:

Setup do ambiente local e com Docker

Instruções para rodar o projeto

Instruções para rodar os testes com

APITestCase

Explicações sobre decisões técnicas

Instruções de como foi feito o deploy (ambientes, ferramentas, fluxo CI/CD)

Documentar no repositório os erros encontrados, decisões e melhorias propostas ao longo do desafio.

### ![⏳](<Base64-Image-Removed>) Prazo de entrega

Você terá 5 dias ÚTEIS após o recebimento deste desafio para finalizá-lo.

Envie o link do repositório público no GitHub (com README, deploy e documentação) para:

![📧](<Base64-Image-Removed>)

desenvolvimento.humano@lacreisaude.com.br

### ![🏗️](<Base64-Image-Removed>)Critérios de Aceite

|     |     |     |
| --- | --- | --- |
| Item | Obrigatório | Observações |
| CRUD funcional de profissionais e consultas | ![✅](<Base64-Image-Removed>)​ | Incluindo busca por ID do profissional |
| Segurança (sanitização, CORS, autenticação) | ![✅](<Base64-Image-Removed>)​ | Proteção contra SQL Injection, API segura |
| Docker + PostgreSQL configurados | ![✅](<Base64-Image-Removed>)​ | Setup replicável para qualquer ambiente |
| GitHub Actions (CI/CD) | ![✅](<Base64-Image-Removed>)​ | Build, testes e deploy automatizados |
| Deploy funcional (staging e produção) | ![✅](<Base64-Image-Removed>)​ | Na AWS ou serviço equivalente |
| Testes unitários e de erro com APITestCase | ![✅](<Base64-Image-Removed>)​ | Cobertura mínima exigida |
| README completo + rollback | ![✅](<Base64-Image-Removed>)​ | Setup local, CI/CD, rollback e justificativas técnicas |
| Documentação da API (Swagger, Postman, etc.) | ![🟨](<Base64-Image-Removed>) Opcional | Fortemente recomendado para profissionalização da entrega |
| Proposta de integração com Assas | ![🟨](<Base64-Image-Removed>) Opcional | Agrega valor ao entendimento de fluxo de pagamentos |

### ![🎁](<Base64-Image-Removed>)O que você ganha com a atividade voluntária

Participação em um projeto real de impacto social

Networking com profissionais de diversas áreas

Desenvolvimento técnico prático com tecnologias atuais

Certificado de participação na Lacrei Saúde

A experiência de construir tecnologia com propósito, inclusão e impacto real

### ![💙](<Base64-Image-Removed>) Nosso agradecimento

Na Lacrei Saúde, acreditamos que código é cuidado, e tecnologia pode transformar realidades.

Ficamos muito felizes com sua dedicação e vontade de contribuir com algo tão significativo.

Seu trabalho será parte da construção de um sistema que acolhe, respeita e protege.

> ![🥰](<Base64-Image-Removed>) Boa sorte! Estamos aqui torcendo por você ![🚀](<Base64-Image-Removed>)![🌈](<Base64-Image-Removed>)​