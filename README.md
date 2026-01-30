# API de Medicamentos do Brasil

API REST autenticada para consulta de medicamentos brasileiros registrados na ANVISA.

- **Landing page** em `/`: explicação da API e formulário para **gerar sua API Key** (autoatendimento, rate limit por IP).
- **Documentação** em `/docs` (Swagger) e `/redoc`.

## Tecnologias

- FastAPI
- PostgreSQL
- SQLAlchemy
- Autenticação por API Key

## Setup

### Instalação do PostgreSQL no WSL

Execute o script de setup (ou siga os passos manuais abaixo):

```bash
# No WSL
chmod +x scripts/setup_postgresql.sh
./scripts/setup_postgresql.sh
```

**Ou manualmente:**

```bash
# No WSL
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo service postgresql start

# Criar usuário e banco
sudo -u postgres psql -c "CREATE USER medicamentos_user WITH PASSWORD 'medicamentos_pass';"
sudo -u postgres psql -c "CREATE DATABASE medicamentos_db OWNER medicamentos_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE medicamentos_db TO medicamentos_user;"
```

### Configuração da API

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
```bash
# Crie um arquivo .env com:
DATABASE_URL=postgresql://medicamentos_user:medicamentos_pass@localhost:5432/medicamentos_db
SECRET_KEY=your-secret-key-here-change-in-production
API_PREFIX=/api/v1
```

4. Execute o script de importação do CSV:
```bash
python scripts/import_csv.py
```

5. Crie uma API Key inicial:
```bash
python scripts/create_admin.py
```

6. Inicie o servidor:
```bash
uvicorn app.main:app --reload
```

A landing e a documentação interativa estarão em `http://localhost:8000/` e `http://localhost:8000/docs`.

## Autenticação

Todas as requisições devem incluir o header:
```
X-API-Key: sua-api-key-aqui
```

## Endpoints

- `GET /` - Landing page (API info + gerar API Key)
- `GET /api/v1/medicamentos` - Lista medicamentos com paginação e filtros
- `GET /api/v1/medicamentos/{id}` - Detalhes de um medicamento
- `GET /api/v1/medicamentos/search` - Busca textual
- `GET /api/v1/stats` - Estatísticas
- `POST /api/v1/auth/keys/public` - **Criar API Key (público, rate limit 5/hora por IP)**
- `POST /api/v1/auth/keys` - Criar nova API Key (exige API Key)
- `GET /api/v1/auth/keys` - Listar API Keys (exige API Key)

## Deploy

### Docker Compose (local ou VPS)

```bash
docker compose up --build
```

Acesse `http://localhost:8000`. Primeira vez: importar CSV e (opcional) criar key admin:

```bash
docker compose run api python scripts/import_csv.py
docker compose run api python scripts/create_admin.py
```

Variáveis: `SECRET_KEY` no `.env` ou em `environment` no `docker-compose.yml`.

### PaaS (Railway, Render)

1. Conectar o repositório (GitHub); adicionar PostgreSQL no projeto.
2. Variáveis: `DATABASE_URL` (do Postgres), `SECRET_KEY`, `API_PREFIX=/api/v1`.
3. Comando de start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (Railway/Render injetam `PORT`).
4. Se usar Dockerfile, a imagem já usa `$PORT`; basta configurar o build pela Dockerfile na Railway.
