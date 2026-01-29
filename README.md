# API de Medicamentos do Brasil

API REST autenticada para consulta de medicamentos brasileiros registrados na ANVISA.

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

A documentação interativa estará disponível em `http://localhost:8000/docs`

## Autenticação

Todas as requisições devem incluir o header:
```
X-API-Key: sua-api-key-aqui
```

## Endpoints

- `GET /api/v1/medicamentos` - Lista medicamentos com paginação e filtros
- `GET /api/v1/medicamentos/{id}` - Detalhes de um medicamento
- `GET /api/v1/medicamentos/search` - Busca textual
- `GET /api/v1/stats` - Estatísticas
- `POST /api/v1/auth/keys` - Criar nova API Key (protegido)
- `GET /api/v1/auth/keys` - Listar API Keys (protegido)
