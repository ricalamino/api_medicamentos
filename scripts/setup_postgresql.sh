#!/bin/bash

# Script para instalar e configurar PostgreSQL no WSL

set -e

echo "=== Instalando PostgreSQL ==="
sudo apt update
sudo apt install -y postgresql postgresql-contrib

echo "=== Iniciando serviço PostgreSQL ==="
sudo service postgresql start

echo "=== Configurando PostgreSQL ==="
# Criar usuário e banco de dados
sudo -u postgres psql << EOF
-- Criar usuário se não existir
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'medicamentos_user') THEN
        CREATE USER medicamentos_user WITH PASSWORD 'medicamentos_pass';
    END IF;
END
\$\$;

-- Criar banco de dados se não existir
SELECT 'CREATE DATABASE medicamentos_db OWNER medicamentos_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'medicamentos_db')\gexec

-- Dar permissões
GRANT ALL PRIVILEGES ON DATABASE medicamentos_db TO medicamentos_user;
\q
EOF

echo "=== Configuração concluída! ==="
echo ""
echo "Credenciais:"
echo "  Database: medicamentos_db"
echo "  User: medicamentos_user"
echo "  Password: medicamentos_pass"
echo ""
echo "Connection string:"
echo "  postgresql://medicamentos_user:medicamentos_pass@localhost:5432/medicamentos_db"
echo ""
echo "Para iniciar o PostgreSQL manualmente:"
echo "  sudo service postgresql start"
echo ""
echo "Para parar o PostgreSQL:"
echo "  sudo service postgresql stop"
