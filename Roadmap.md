<details>
<summary>1. Configuração do Ambiente de Desenvolvimento - Parte I</summary>

## Descrição
Nesta etapa, vamos configurar o ambiente de desenvolvimento para o projeto Django. Isso inclui a criação do repositório Git, instalação do Django, configuração do banco de dados e preparação do ambiente virtual.

### Passos:
1. **Criar Repositório no GitHub**
   - Acesse sua conta no GitHub e crie um novo repositório chamado `blog-api`.
   - Adicione um `.gitignore` para projetos Django, que pode ser gerado automaticamente ao criar o repositório ou copiado de templates comuns.

2. **Instalar Python e Configurar Ambiente Virtual**
   - Certifique-se de que o Python esteja instalado em sua máquina (`python --version`).
   - Crie um ambiente virtual:
     ```bash
     python -m venv venv
     ```
   - Ative o ambiente virtual:
     - **Windows**: `venv\Scripts\activate`
     - **Linux/Mac**: `source venv/bin/activate`

3. **Instalar Django e Dependências**
   - Com o ambiente virtual ativo, instale o Django:
     ```bash
     pip install django
     ```
   - Verifique se a instalação foi bem-sucedida:
     ```bash
     python -m django --version
     ```

4. **Criar Projeto Django**
   - Inicie um novo projeto Django chamado `blog`:
     ```bash
     django-admin startproject blog
     cd blog
     ```

5. **Configurar Banco de Dados**
   - Inicialmente, utilizaremos o banco de dados SQLite. As configurações já estão presentes no arquivo `settings.py` do projeto.
   - Crie as tabelas necessárias com:
     ```bash
     python manage.py migrate
     ```

6. **Iniciar Servidor de Desenvolvimento**
   - Execute o servidor para testar a configuração:
     ```bash
     python manage.py runserver
     ```
   - Acesse `http://localhost:8000/` no navegador para confirmar se tudo está funcionando.

### Evidências:
![image](https://example.com/image1.png)
![image](https://example.com/image2.png)
</details>

<details>
<summary>2. Configuração de Ambiente de Desenvolvimento - Parte II</summary>

## Descrição
Configurar PostgreSQL como o banco de dados para o projeto Django. Inclui instalação, configuração e migração de banco de dados.

### Passos:
1. **Instalar PostgreSQL**
   - Baixe e instale o PostgreSQL a partir do [site oficial](https://www.postgresql.org/download/).

2. **Instalar DBeaver**
   - Use o DBeaver para gerenciar o banco de dados PostgreSQL. Baixe a ferramenta [aqui](https://dbeaver.io/download/).

3. **Criar Banco de Dados**
   - Crie um novo banco de dados chamado `blog_api` usando o DBeaver ou comandos SQL no terminal do PostgreSQL.

4. **Instalar `psycopg2`**
   - `psycopg2` é necessário para conectar o Django ao PostgreSQL:
     ```bash
     pip install psycopg2-binary
     ```

5. **Atualizar Configurações do Banco de Dados no `settings.py`**
   - No arquivo `blog/settings.py`, configure o banco de dados:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.postgresql',
             'NAME': 'blog_api',
             'USER': 'postgres',
             'PASSWORD': 'password',
             'HOST': 'localhost',
             'PORT': '5432',
         }
     }
     ```

6. **Migrar Banco de Dados**
   - Aplique as migrações para criar tabelas no PostgreSQL:
     ```bash
     python manage.py migrate
     ```

### Evidências:
![image](https://example.com/image3.png)
![image](https://example.com/image4.png)
</details>

<details> <summary>3. Gerenciamento de Variáveis de Ambiente e Configurações por Ambiente</summary>

## Descrição

Para tornar o projeto mais seguro e escalável, é necessário gerenciar variáveis de ambiente e configurar o Django para diferentes ambientes (desenvolvimento, teste e produção).

## Instalação do Gerenciador de Variáveis de Ambiente

Instale o pacote `python-decouple` para gerenciar variáveis de ambiente:

```bash
pip install python-decouple
```
## Configuração do `.env` e `.env.example`

Crie um arquivo `.env` na raiz do projeto para armazenar variáveis sensíveis como chaves secretas, credenciais de banco de dados e outras configurações específicas do ambiente.

Crie um arquivo `.env.example` para fornecer um modelo de como deve ser configurado o `.env`, facilitando o setup para outros desenvolvedores.

**Exemplo de `.env`:**

```python
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=blog_development
DB_USER=postgres
DB_PASSWORD=mysecretpassword
DB_HOST=localhost
DB_PORT=5432

```

## Configurações Diferenciadas por Ambiente
- Crie diferentes arquivos de configuração para ambientes de desenvolvimento, teste e produção. Isso ajuda a manter variáveis específicas para cada um desses contextos.
```python
settings/
    ├── base.py          # Configurações comuns a todos os ambientes
    ├── development.py   # Configurações específicas para desenvolvimento
    ├── production.py    # Configurações específicas para produção
    ├── staging.py       # Configurações específicas para ambiente de homologação (opcional)

```
Exemplo de base.py:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

# Configuração para Diferentes Ambientes

## Desenvolvimento (`development.py`)

Inclua configurações que são específicas para desenvolvimento, como `DEBUG=True` e `ALLOWED_HOSTS` definidos para `localhost`:

```python
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Configurações adicionais específicas para desenvolvimento podem ser adicionadas aqui
```

## Produção (production.py)

No ambiente de produção, garanta que DEBUG=False, defina ALLOWED_HOSTS para incluir o domínio do seu site, e configure variáveis adicionais para melhorar a segurança e a performance:

```python
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['yourwebsite.com']

# Configurações adicionais específicas para produção
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Comando para Selecionar o Ambiente

Para facilitar a execução do projeto em diferentes ambientes, crie um script que permita selecionar qual configuração usar ao iniciar o Django.

Crie um Script de Gerenciamento Personalizado

Crie um arquivo chamado manage_env.py na raiz do projeto, com o seguinte conteúdo:

```python
import os
import sys

if __name__ == "__main__":
    # Definir qual ambiente usar
    env = sys.argv[1] if len(sys.argv) > 1 else "development"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"blog.settings.{env}")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv[2:])

```

## Como Usar o Script

Para iniciar o ambiente de desenvolvimento:
```bash
python manage_env.py development runserver
```

Para aplicar migrações no ambiente de produção:
```bash
python manage_env.py production migrate
```

</details>

<details>
  <summary>4. Configuração para Integração Contínua com GitHub Actions</summary>

### Configuração de CI/CD Usando GitHub Actions

Para automatizar a execução de testes e verificar se as alterações estão funcionando corretamente em cada commit ou Pull Request, vamos configurar um pipeline simples usando GitHub Actions.

#### Criar Workflow no GitHub Actions

**Adicionar Arquivo de Workflow**

Crie um diretório chamado `.github/workflows` na raiz do seu projeto e adicione um arquivo chamado `ci.yml`:

```yaml
name: CI Pipeline

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main
      - develop

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_DB: ${{ secrets.DB_NAME }}
          POSTGRES_USER: ${{ secrets.DB_USER }}
          POSTGRES_PASSWORD: ${{ secrets.DB_PASSWORD }}
        options: >-
          --health-cmd "pg_isready -U ${{ secrets.DB_USER }}" 
          --health-interval 10s 
          --health-timeout 5s 
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - name: Check out repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run migrations
        run: |
          python manage.py migrate --settings=settings.base

      - name: Run tests
        run: |
          python manage.py test --settings=settings.base
```
### Explicação:
- `on`: Define quando o workflow será executado (em push para main e develop, e em PRs).
- `services`: Inicia um container PostgreSQL para que os testes sejam executados em um ambiente similar ao de produção.
- `steps`: Cada etapa executa um comando específico:
- `Check out repository`: Faz checkout do repositório.
- `Set up Python`: Configura o Python na versão desejada.
- `Install dependencies`: Instala as dependências definidas no requirements.txt.
- `Run migrations`: Aplica as migrações do banco de dados.
- `Run tests`: Executa os testes.

### Configurar Segredos no GitHub

Certifique-se de adicionar os seguintes segredos no repositório para que as credenciais do banco de dados não fiquem expostas:
```
DB_NAME
DB_USER
DB_PASSWORD
```
Esses segredos são configurados diretamente no repositório, em Settings > Secrets.

