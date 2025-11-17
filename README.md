# API de Gerenciamento de Usuários 🚀

Este é um projeto de uma API RESTful completa para gerenciamento de usuários, construída com Django, Django Rest Framework e PostgreSQL. Todo o ambiente de desenvolvimento e produção é containerizado com Docker e Docker Compose, garantindo consistência e facilidade de setup.

A API implementa funcionalidades essenciais como CRUD de usuários, autenticação segura baseada em tokens JWT, permissões baseadas em roles (usuário comum vs. admin) e documentação automática de endpoints com Swagger.

## ✨ Funcionalidades Principais

*   **CRUD completo de Usuários:** Crie, leia, atualize e delete usuários.
*   **Autenticação com JWT:** Sistema de login seguro que retorna `access` e `refresh` tokens.
*   **Permissões e Segurança:**
    *   Endpoints protegidos que só podem ser acessados com um token válido.
    *   Regras de negócio que impedem um usuário de editar ou deletar outros usuários (a menos que seja admin).
    *   "Soft Delete": Usuários não são deletados do banco, apenas marcados como inativos.
*   **Documentação Automática:** Interface do Swagger UI (`/api/docs/`) e ReDoc (`/api/redoc/`) gerada automaticamente para testar e explorar a API.
*   **Tarefas em Segundo Plano com Celery:** Estrutura pronta para executar tarefas assíncronas (ex: envio de e-mails, processamento de dados).
*   **Ambiente Containerizado:** Setup de desenvolvimento simplificado com um único comando (`docker-compose up`).

## ⚙️ Tecnologias e Dependências

Este projeto utiliza uma variedade de tecnologias modernas para garantir robustez e escalabilidade.

#### Backend
*   **[Django](https://www.djangoproject.com/):** O framework web principal.
*   **[Django Rest Framework (DRF)](https://www.django-rest-framework.org/):** Toolkit poderoso para construir APIs Web.
*   **[Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/):** Para implementação da autenticação baseada em JSON Web Tokens.
*   **[Gunicorn](https://gunicorn.org/):** Servidor WSGI para produção.

#### Banco de Dados & Cache
*   **[PostgreSQL](https://www.postgresql.org/):** Banco de dados relacional principal.
*   **[Redis](https://redis.io/):** Usado como cache e como message broker para o Celery.
*   **[psycopg2-binary](https://www.psycopg.org/):** Adaptador PostgreSQL para Python.

#### Containerização e Ferramentas
*   **[Docker](https://www.docker.com/):** Plataforma para criar, implantar e executar aplicações em contêineres.
*   **[Docker Compose](https://docs.docker.com/compose/):** Ferramenta para definir e executar aplicações Docker multi-contêiner.
*   **[pgAdmin](https://www.pgadmin.org/):** Ferramenta de administração visual para PostgreSQL.

#### Documentação e Testes
*   **[drf-yasg](https://drf-yasg.readthedocs.io/):** Gerador de documentação Swagger/OpenAPI.
*   **[Pytest](https://docs.pytest.org/):** Framework para escrita de testes.
*   **[pytest-django](https://pytest-django.readthedocs.io/):** Plugin para integrar Pytest com Django.

#### Outras Dependências
*   **[Celery](https://docs.celeryq.dev/):** Sistema de filas de tarefas distribuídas.
*   **[python-decouple](https://pypi.org/project/python-decouple/):** Para gerenciar variáveis de ambiente e separá-las do código.
*   **[django-cors-headers](https://pypi.org/project/django-cors-headers/):** Para lidar com Cross-Origin Resource Sharing (CORS).

---

## 🔧 Instalação e Execução

Para executar este projeto localmente, você precisa ter o **Docker** e o **Docker Compose** instalados.

**1. Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio
```

**2. Crie o arquivo de variáveis de ambiente:**
Crie um arquivo chamado `.env` na raiz do projeto, copiando o conteúdo do exemplo abaixo. **Nunca** envie seu arquivo `.env` para o repositório Git.

```env
# .env

# Chaves de segurança do Django (use chaves fortes e aleatórias em produção)
SECRET_KEY='django-insecure-@1j8!s(2z^6k*&m+f%7q_x(p#=b5t$h@y9n-c)w!d*#0v_z'
JWT_SECRET_KEY='u#h9$V^7d@k!L&pE*r2sW@zY3bB!qN*m'

# Configurações do Django
DEBUG=True

# Configurações do Banco de Dados PostgreSQL
DB_NAME=users_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432
```

**3. Suba os contêineres:**
Execute o seguinte comando no terminal. Ele irá construir as imagens, criar os volumes e iniciar todos os serviços.

```bash
docker-compose up --build -d
```

**4. Crie um superusuário (Admin):**
Para acessar a área administrativa do Django e ter permissões de admin na API, execute o comando abaixo e siga as instruções para criar seu usuário.

```bash
docker-compose exec web python manage.py createsuperuser
```

Pronto! Sua aplicação está no ar e acessível nos seguintes endereços:
*   **API:** `http://localhost:8000/`
*   **Documentação Swagger:** `http://localhost:8000/api/docs/`
*   **pgAdmin (Banco de Dados):** `http://localhost:5050` (Login: `admin@admin.com`, Senha: `admin`)

---

## 🚀 Como Usar a API

A maneira mais fácil de explorar e testar a API é através da **documentação do Swagger**. No entanto, aqui está um resumo dos principais endpoints.

### Autenticação

Para acessar os endpoints protegidos, primeiro obtenha um token de acesso:

1.  **Faça uma requisição `POST` para `/api/users/login/`** com seu email e senha.
2.  A resposta conterá um `access` e um `refresh` token.
3.  **Para as próximas requisições**, inclua o `access` token no cabeçalho (Header) `Authorization` com o prefixo `Bearer`.
    *   Exemplo: `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### Endpoints Principais

| Método | Endpoint                | Descrição                                         | Autenticação         |
| :----- | :---------------------- | :------------------------------------------------ | :------------------- |
| `POST` | `/api/users/`           | Cria um novo usuário.                             | Pública              |
| `POST` | `/api/users/login/`     | Autentica um usuário e retorna tokens JWT.        | Pública              |
| `GET`  | `/api/users/`           | Lista todos os usuários ativos.                   | Requer Token JWT     |
| `GET`  | `/api/users/{id}/`      | Retorna os detalhes de um usuário específico.     | Requer Token JWT     |
| `PUT`  | `/api/users/{id}/`      | Atualiza os dados de um usuário.                  | Requer Token JWT     |
| `DELETE`| `/api/users/{id}/`     | Desativa (soft delete) um usuário.                | Requer Token JWT     |

---

## 🧪 Executando os Testes

Para rodar a suíte de testes automatizados, execute o seguinte comando:

```bash
docker-compose exec web pytest
```

---

## 📁 Estrutura do Projeto

```
.
├── apps/
│   └── users/              # App Django para gerenciamento de usuários
│       ├── migrations/
│       ├── __init__.py
│       ├── models.py       # (Model) Define a estrutura do usuário no banco
│       ├── serializers.py  # (Template/Serializer) Valida e formata os dados para JSON
│       ├── urls.py         # Rotas específicas do app de usuários
│       └── views.py        # (View) Controla a lógica das requisições HTTP
├── config/                 # Configurações gerais do projeto Django
│   ├── __init__.py
│   ├── settings.py         # Configurações principais do Django
│   ├── urls.py             # Rotas principais do projeto
│   └── ...
├── .env                    # Arquivo com variáveis de ambiente (NÃO VERSIONADO)
├── docker-compose.yml      # Orquestração dos contêineres
├── Dockerfile              # Receita para construir a imagem da aplicação Django
├── docker-entrypoint.sh    # Script de inicialização do contêiner da aplicação
├── manage.py               # Utilitário de linha de comando do Django
└── requirements.txt        # Lista de dependências Python
```